"""Player HTTP server and message handler.

This module implements the player server that handles game invitations
and move requests from referees.
"""

import logging
from typing import Any, Dict

from ..common.errors import ErrorCode, LeagueError
from ..common.protocol import (
    Envelope,
    JSONRPCRequest,
    JSONRPCResponse,
    MessageType,
    create_error_response,
    create_success_response,
    generate_conversation_id,
    utc_now,
)
from ..common.transport import LeagueHTTPClient, LeagueHTTPServer
from .strategies import get_strategy

logger = logging.getLogger(__name__)


class PlayerServer:
    """Player server for handling game invitations and move requests."""

    def __init__(
        self,
        player_id: str,
        host: str,
        port: int,
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
        self.player_id = player_id
        self.host = host
        self.port = port
        self.league_manager_url = league_manager_url
        self.auth_token = None
        self.league_id = None

        # Initialize strategy using registry
        try:
            self.strategy = get_strategy(strategy_type, player_id)
            logger.info(f"Loaded strategy: {self.strategy.get_strategy_name()}")
        except ValueError as e:
            logger.error(f"Failed to load strategy '{strategy_type}': {e}")
            # Fallback to smart strategy
            self.strategy = get_strategy('smart', player_id)
            logger.warning(f"Using fallback strategy: {self.strategy.get_strategy_name()}")

        # HTTP client and server
        self.http_client = LeagueHTTPClient()
        self.http_server = LeagueHTTPServer(
            host,
            port,
            self._handle_request,
            self._get_status
        )

        # Track current matches
        self.current_matches = {}

    def start(self):
        """Start the player server."""
        self.http_server.start()
        logger.info(f"Player {self.player_id} started on {self.host}:{self.port}")

    def stop(self):
        """Stop the player server."""
        self.http_server.stop()
        logger.info(f"Player {self.player_id} stopped")

    def register(self) -> bool:
        """Register with the League Manager.

        Returns:
            True if registration successful
        """
        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
            sender=f"player:{self.player_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id()
        )

        payload = {
            'player_id': self.player_id,
            'endpoint_url': f"http://{self.host}:{self.port}/mcp"
        }

        try:
            result = self.http_client.send_request(
                self.league_manager_url,
                envelope,
                payload
            )
            response_payload = result.get('payload', {})
            self.auth_token = response_payload.get('auth_token')
            self.league_id = response_payload.get('league_id')
            logger.info(f"Player registered successfully. League ID: {self.league_id}")
            return True
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False

    def send_ready(self) -> bool:
        """Send ready signal to League Manager.

        Signals that the player has completed initialization and is ready
        to participate in matches.

        Returns:
            True if ready signal acknowledged
        """
        if not self.auth_token:
            logger.error("Cannot send ready signal: not registered")
            return False

        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.AGENT_READY_REQUEST.value,
            sender=f"player:{self.player_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            auth_token=self.auth_token
        )

        payload = {}

        try:
            result = self.http_client.send_request(
                self.league_manager_url,
                envelope,
                payload
            )
            response_payload = result.get('payload', {})
            agent_state = response_payload.get('agent_state')
            logger.info(f"Player ready signal acknowledged. Status: {agent_state}")
            return True
        except Exception as e:
            logger.error(f"Failed to send ready signal: {e}")
            return False

    def _handle_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle incoming JSON-RPC request.

        Args:
            request: Validated JSON-RPC request

        Returns:
            JSON-RPC response
        """
        try:
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
                response_envelope = Envelope(
                    protocol="league.v2",
                    message_type=response_type,
                    sender=f"player:{self.player_id}",
                    timestamp=utc_now(),
                    conversation_id=envelope.conversation_id,
                    match_id=envelope.match_id
                )

                return create_success_response(
                    response_envelope,
                    response_payload,
                    request.id
                )
            else:
                # Acknowledgement without specific response
                return create_success_response(
                    envelope,
                    {},
                    request.id
                )

        except LeagueError as e:
            logger.warning(f"League error: {e}")
            return create_error_response(
                int(e.code),
                e.message,
                e.details,
                request.id
            )
        except Exception as e:
            logger.exception("Unexpected error handling request")
            return create_error_response(
                ErrorCode.INTERNAL_ERROR,
                f"Internal error: {str(e)}",
                request_id=request.id
            )

    def _handle_game_invitation(
        self,
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle game invitation from referee.

        Args:
            envelope: Request envelope
            payload: Invitation payload

        Returns:
            Join acknowledgement payload
        """
        match_id = payload.get('match_id')
        game_type = payload.get('game_type')
        opponents = payload.get('opponents', [])

        logger.info(f"Received game invitation: {match_id}, opponents: {opponents}")

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
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle move request from referee.

        Args:
            envelope: Request envelope
            payload: Move request payload

        Returns:
            Move response payload
        """
        step_number = payload.get('step_number')
        step_context = payload.get('step_context', {})

        logger.debug(f"Received move request for step {step_number}")

        # Compute move using strategy
        try:
            move = self.strategy.compute_move(step_context)
        except Exception as e:
            logger.error(f"Strategy error: {e}")
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

        logger.info(f"Game over for match {match_id}: {outcome}")

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
        import random
        board = step_context.get('board', [])
        available = []
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":
                    available.append((row, col))

        if available:
            move = random.choice(available)
            return {'row': move[0], 'col': move[1]}
        else:
            return {'row': 0, 'col': 0}

    def _get_status(self) -> Dict[str, Any]:
        """Get player status.

        Returns:
            Status dictionary
        """
        return {
            'player_id': self.player_id,
            'status': 'ACTIVE' if self.auth_token else 'INIT',
            'league_id': self.league_id,
            'active_matches': len(self.current_matches)
        }
