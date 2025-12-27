"""Referee HTTP server and message handler.

This module implements the referee server that handles match assignments
from the League Manager.
"""

import logging
import threading
from typing import Any, Dict

from ..common.agent_base import AgentServerBase
from ..common.errors import ErrorCode, LeagueError, OperationalError
from ..common.protocol import (
    Envelope,
    JSONRPCRequest,
    JSONRPCResponse,
    MessageType,
    create_success_response,
    generate_conversation_id,
    utc_now,
)
from ..common.request_handlers import handle_request_errors
from .match_executor import MatchExecutor

logger = logging.getLogger(__name__)


class RefereeServer(AgentServerBase):
    """Referee server for handling match assignments."""

    def __init__(self, referee_id: str, host: str, port: int, league_manager_url: str):
        """Initialize the referee server.

        Args:
            referee_id: Referee identifier
            host: Host to bind to
            port: Port to bind to
            league_manager_url: URL of League Manager
        """
        super().__init__(
            referee_id, "referee", host=host, port=port, league_manager_url=league_manager_url
        )
        self.referee_id = referee_id

        # HTTP server
        self.http_server = self._create_http_server(self._handle_request, self._get_status)

        # Player URLs (would be received during invitation)
        self.player_urls = {}

    def start(self):
        """Start the referee server."""
        self.http_server.start()
        logger.info("Referee %s started on %s:%s", self.referee_id, self.host, self.port)

    def stop(self):
        """Stop the referee server."""
        self.http_server.stop()
        logger.info("Referee %s stopped", self.referee_id)

    def register(self) -> bool:
        """Register with the League Manager.

        Returns:
            True if registration successful
        """
        return self._do_register(MessageType.REGISTER_REFEREE_REQUEST, "referee_id")

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
        envelope = Envelope.from_dict(request.params["envelope"])
        payload = request.params.get("payload", {})

        # Dispatch based on message type
        message_type = MessageType(envelope.message_type)

        if message_type == MessageType.MATCH_ASSIGNMENT:
            response_payload = self._handle_match_assignment(envelope, payload)
        else:
            raise LeagueError(
                ErrorCode.INVALID_MESSAGE_TYPE, f"Unsupported message type: {message_type}"
            )

        # Create response envelope
        response_envelope = self._create_response_envelope(
            MessageType.MATCH_ASSIGNMENT_ACK.value, envelope.conversation_id, envelope.match_id
        )
        # Add auth_token and league_id to response envelope
        response_envelope.auth_token = self.auth_token
        response_envelope.league_id = self.league_id

        return create_success_response(response_envelope, response_payload, request.id)

    def _handle_match_assignment(
        self, _envelope: Envelope, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle match assignment from League Manager.

        Args:
            _envelope: Request envelope (unused but required by handler interface)
            payload: Assignment payload

        Returns:
            Acknowledgement payload
        """
        match_id = payload.get("match_id")
        round_id = payload.get("round_id")
        game_type = payload.get("game_type")
        players = payload.get("players", [])
        player_endpoints = payload.get("player_endpoints", {})

        logger.info("Received match assignment: %s, players: %s", match_id, players)

        # Use player endpoints from payload
        for player_id, endpoint_url in player_endpoints.items():
            self.player_urls[player_id] = endpoint_url
            logger.debug("Player %s endpoint: %s", player_id, endpoint_url)

        # Execute match in background thread (asynchronous)
        def execute_match_async():
            try:
                executor = MatchExecutor(self.referee_id, self.http_client, self.player_urls)

                result = executor.execute_match(
                    match_id, round_id, game_type, players=players, _league_id=self.league_id
                )

                # Report result to League Manager
                self._report_result(result)

            except (LeagueError, OperationalError) as e:
                logger.error("Match execution failed: %s", e)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Unexpected error during match execution")

        # Start match execution in background
        match_thread = threading.Thread(target=execute_match_async, daemon=True)
        match_thread.start()

        # Return acknowledgement immediately
        return {"status": "acknowledged", "match_id": match_id}

    def _report_result(self, result: Dict[str, Any]):
        """Report match result to League Manager.

        Args:
            result: Match result dictionary
        """
        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.MATCH_RESULT_REPORT.value,
            sender=f"referee:{self.referee_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            auth_token=self.auth_token,
            league_id=self.league_id,
            round_id=result["round_id"],
            match_id=result["match_id"],
            game_type=result["game_type"],
        )

        payload = {
            "game_type": result["game_type"],
            "players": result["players"],
            "outcome": result["outcome"],
            "points": result["points"],
            "game_metadata": result.get("game_metadata"),
        }

        try:
            self.http_client.send_request(self.league_manager_url, envelope, payload)
            logger.info("Reported result for match %s", result["match_id"])
        except LeagueError as e:
            logger.error("Failed to report result: %s", e)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Unexpected error reporting result")

    def _get_status(self) -> Dict[str, Any]:
        """Get referee status.

        Returns:
            Status dictionary
        """
        return self._get_base_status()
