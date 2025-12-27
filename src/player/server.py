"""Player HTTP server and message handler.

This module implements the player server that handles game invitations
and move requests from referees.
"""

import logging
import random
from typing import Any, Dict

from ..common.agent_base import AgentServerBase
from ..common.errors import ErrorCode, LeagueError
from ..common.protocol import (
    Envelope,
    JSONRPCRequest,
    JSONRPCResponse,
    MessageType,
    create_success_response,
)
from ..common.request_handlers import handle_request_errors
from .strategies import get_strategy

logger = logging.getLogger(__name__)


class PlayerServer(AgentServerBase):
    """Player server for handling game invitations and move requests."""

    def __init__(
        self,
        player_id: str,
        host: str,
        port: int,
        *,
        league_manager_url: str,
        strategy_type: str = "smart"
    ):
        """Initialize the player server.

        Args:
            player_id: Player identifier
            host: Host to bind to
            port: Port to bind to
            league_manager_url: URL of League Manager
            strategy_type: Strategy to use ("smart" or "random")
        """
        super().__init__(
            player_id,
            "player",
            host=host,
            port=port,
            league_manager_url=league_manager_url
        )
        self.player_id = player_id

        # Initialize strategy using registry
        try:
            self.strategy = get_strategy(strategy_type, player_id)
            logger.info("Loaded strategy: %s", self.strategy.get_strategy_name())
        except ValueError as e:
            logger.error("Failed to load strategy '%s': %s", strategy_type, e)
            # Fallback to smart strategy
            self.strategy = get_strategy('smart', player_id)
            logger.warning("Using fallback strategy: %s", self.strategy.get_strategy_name())

        # HTTP server
        self.http_server = self._create_http_server(
            self._handle_request,
            self._get_status
        )

        # Track current matches
        self.current_matches = {}

    def start(self):
        """Start the player server."""
        self.http_server.start()
        logger.info("Player %s started on %s:%s", self.player_id, self.host, self.port)

    def stop(self):
        """Stop the player server."""
        self.http_server.stop()
        logger.info("Player %s stopped", self.player_id)

    def register(self) -> bool:
        """Register with the League Manager.

        Returns:
            True if registration successful
        """
        return self._do_register(
            MessageType.REGISTER_PLAYER_REQUEST,
            'player_id'
        )

    def _handle_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle incoming JSON-RPC request.

        Args:
            request: Validated JSON-RPC request

        Returns:
            JSON-RPC response
        """
        return handle_request_errors(request, self._handle_request_internal)

    def _handle_request_internal(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Internal request handler with business logic.

        Args:
            request: Validated JSON-RPC request

        Returns:
            JSON-RPC response
        """
        envelope = Envelope.from_dict(request.params['envelope'])
        payload = request.params.get('payload', {})

        # Dispatch based on message type
        message_type = MessageType(envelope.message_type)

        if message_type == MessageType.GAME_INVITATION:
            response_payload = self._handle_game_invitation(envelope, payload)
            response_type = MessageType.GAME_JOIN_ACK.value
        elif message_type == MessageType.REQUEST_MOVE:
            response_payload = self._handle_move_request(envelope, payload)
            response_type = MessageType.MOVE_RESPONSE.value
        elif message_type == MessageType.GAME_OVER:
            response_payload = self._handle_game_over(envelope, payload)
            response_type = None  # No response expected
        else:
            raise LeagueError(
                ErrorCode.INVALID_MESSAGE_TYPE,
                f"Unsupported message type: {message_type}"
            )

        if response_type:
            # Create response envelope
            response_envelope = self._create_response_envelope(
                response_type,
                envelope.conversation_id,
                envelope.match_id
            )

            return create_success_response(
                response_envelope,
                response_payload,
                request.id
            )
        # Acknowledgement without specific response
        return create_success_response(
            envelope,
            {},
            request.id
        )

    def _handle_game_invitation(
        self,
        _envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle game invitation from referee.

        Args:
            _envelope: Request envelope (unused but required by handler interface)
            payload: Invitation payload

        Returns:
            Join acknowledgement payload
        """
        match_id = payload.get('match_id')
        game_type = payload.get('game_type')
        opponents = payload.get('opponents', [])

        logger.info("Received game invitation: %s, opponents: %s", match_id, opponents)

        # Track match
        self.current_matches[match_id] = {
            'game_type': game_type,
            'opponents': opponents
        }

        return {
            'status': 'accepted',
            'match_id': match_id
        }

    def _handle_move_request(
        self,
        _envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle move request from referee.

        Args:
            _envelope: Request envelope (unused but required by handler interface)
            payload: Move request payload

        Returns:
            Move response payload
        """
        step_number = payload.get('step_number')
        step_context = payload.get('step_context', {})

        logger.debug("Received move request for step %s", step_number)

        # Compute move using strategy
        try:
            move = self.strategy.compute_move(step_context)
        except (ValueError, KeyError, IndexError) as e:
            logger.error("Strategy error: %s", e)
            # Return a random valid move as fallback
            move = self._get_fallback_move(step_context)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Unexpected error in strategy")
            # Return a random valid move as fallback
            move = self._get_fallback_move(step_context)

        return {
            'move_payload': move
        }

    def _handle_game_over(
        self,
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle game over notification from referee.

        Args:
            envelope: Request envelope
            payload: Game over payload

        Returns:
            Empty acknowledgement
        """
        match_id = envelope.match_id
        outcome = payload.get('outcome')

        logger.info("Game over for match %s: %s", match_id, outcome)

        # Clean up match tracking
        if match_id in self.current_matches:
            del self.current_matches[match_id]

        return {}

    def _get_fallback_move(self, step_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get a fallback move if strategy fails.

        Args:
            step_context: Game context

        Returns:
            Valid move
        """
        board = step_context.get('board', [])
        available = []
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":
                    available.append((row, col))

        if available:
            move = random.choice(available)
            return {'row': move[0], 'col': move[1]}
        return {'row': 0, 'col': 0}

    def _get_status(self) -> Dict[str, Any]:
        """Get player status.

        Returns:
            Status dictionary
        """
        status = self._get_base_status()
        status['active_matches'] = len(self.current_matches)
        return status
