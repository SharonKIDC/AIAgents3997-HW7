"""Referee HTTP server and message handler.

This module implements the referee server that handles match assignments
from the League Manager.
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
from .match_executor import MatchExecutor

logger = logging.getLogger(__name__)


class RefereeServer:
    """Referee server for handling match assignments."""

    def __init__(
        self,
        referee_id: str,
        host: str,
        port: int,
        league_manager_url: str
    ):
        """Initialize the referee server.

        Args:
            referee_id: Referee identifier
            host: Host to bind to
            port: Port to bind to
            league_manager_url: URL of League Manager
        """
        self.referee_id = referee_id
        self.host = host
        self.port = port
        self.league_manager_url = league_manager_url
        self.auth_token = None
        self.league_id = None

        # HTTP client and server
        self.http_client = LeagueHTTPClient()
        self.http_server = LeagueHTTPServer(
            host,
            port,
            self._handle_request,
            self._get_status
        )

        # Player URLs (would be received during invitation)
        self.player_urls = {}

    def start(self):
        """Start the referee server."""
        self.http_server.start()
        logger.info(f"Referee {self.referee_id} started on {self.host}:{self.port}")

    def stop(self):
        """Stop the referee server."""
        self.http_server.stop()
        logger.info(f"Referee {self.referee_id} stopped")

    def register(self) -> bool:
        """Register with the League Manager.

        Returns:
            True if registration successful
        """
        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_REFEREE_REQUEST.value,
            sender=f"referee:{self.referee_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id()
        )

        payload = {
            'referee_id': self.referee_id,
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
            logger.info(f"Referee registered successfully. League ID: {self.league_id}")
            return True
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False

    def send_ready(self) -> bool:
        """Send ready signal to League Manager.

        Signals that the referee has completed initialization and is ready
        to accept match assignments.

        Returns:
            True if ready signal acknowledged
        """
        if not self.auth_token:
            logger.error("Cannot send ready signal: not registered")
            return False

        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.AGENT_READY_REQUEST.value,
            sender=f"referee:{self.referee_id}",
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
            logger.info(f"Referee ready signal acknowledged. Status: {agent_state}")
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

            if message_type == MessageType.MATCH_ASSIGNMENT:
                response_payload = self._handle_match_assignment(envelope, payload)
            else:
                raise LeagueError(
                    ErrorCode.INVALID_MESSAGE_TYPE,
                    f"Unsupported message type: {message_type}"
                )

            # Create response envelope
            response_envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.MATCH_ASSIGNMENT_ACK.value,
                sender=f"referee:{self.referee_id}",
                timestamp=utc_now(),
                conversation_id=envelope.conversation_id,
                auth_token=self.auth_token,
                league_id=self.league_id,
                match_id=envelope.match_id
            )

            return create_success_response(
                response_envelope,
                response_payload,
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

    def _handle_match_assignment(
        self,
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle match assignment from League Manager.

        Args:
            envelope: Request envelope
            payload: Assignment payload

        Returns:
            Acknowledgement payload
        """
        match_id = payload.get('match_id')
        round_id = payload.get('round_id')
        game_type = payload.get('game_type')
        players = payload.get('players', [])
        player_endpoints = payload.get('player_endpoints', {})

        logger.info(f"Received match assignment: {match_id}, players: {players}")

        # Use player endpoints from payload
        for player_id, endpoint_url in player_endpoints.items():
            self.player_urls[player_id] = endpoint_url
            logger.debug(f"Player {player_id} endpoint: {endpoint_url}")

        # Execute match in background thread (asynchronous)
        import threading
        def execute_match_async():
            try:
                executor = MatchExecutor(
                    self.referee_id,
                    self.http_client,
                    self.player_urls
                )

                result = executor.execute_match(
                    match_id,
                    round_id,
                    game_type,
                    players,
                    self.league_id
                )

                # Report result to League Manager
                self._report_result(result)

            except Exception as e:
                logger.error(f"Match execution failed: {e}")

        # Start match execution in background
        match_thread = threading.Thread(target=execute_match_async, daemon=True)
        match_thread.start()

        # Return acknowledgement immediately
        return {
            'status': 'acknowledged',
            'match_id': match_id
        }

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
            round_id=result['round_id'],
            match_id=result['match_id'],
            game_type=result['game_type']
        )

        payload = {
            'game_type': result['game_type'],
            'players': result['players'],
            'outcome': result['outcome'],
            'points': result['points'],
            'game_metadata': result.get('game_metadata')
        }

        try:
            self.http_client.send_request(
                self.league_manager_url,
                envelope,
                payload
            )
            logger.info(f"Reported result for match {result['match_id']}")
        except Exception as e:
            logger.error(f"Failed to report result: {e}")

    def _get_status(self) -> Dict[str, Any]:
        """Get referee status.

        Returns:
            Status dictionary
        """
        return {
            'referee_id': self.referee_id,
            'status': 'ACTIVE' if self.auth_token else 'INIT',
            'league_id': self.league_id
        }
