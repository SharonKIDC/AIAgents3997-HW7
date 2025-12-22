"""League Manager HTTP server and message dispatcher.

This module implements the main server that handles all league-level
JSON-RPC requests and coordinates between components.
"""

import logging
from typing import Dict, Any, Callable
import uuid

from ..common.transport import LeagueHTTPServer, LeagueHTTPClient
from ..common.protocol import (
    JSONRPCRequest,
    JSONRPCResponse,
    Envelope,
    MessageType,
    create_success_response,
    create_error_response,
    utc_now
)
from ..common.auth import AuthManager
from ..common.persistence import LeagueDatabase
from ..common.config import ConfigManager
from ..common.logging_utils import AuditLogger
from ..common.errors import LeagueError, ValidationError, ErrorCode

from .state import LeagueState, LeagueStatus
from .registration import RegistrationHandler
from .scheduler import RoundRobinScheduler
from .match_assigner import MatchAssigner
from .standings import StandingsEngine

logger = logging.getLogger(__name__)


class LeagueManagerServer:
    """Main League Manager server coordinating all league operations."""

    def __init__(
        self,
        host: str,
        port: int,
        config: ConfigManager,
        database: LeagueDatabase,
        audit_logger: AuditLogger
    ):
        """Initialize the League Manager server.

        Args:
            host: Host to bind to
            port: Port to bind to
            config: Configuration manager
            database: Database connection
            audit_logger: Audit logger
        """
        self.host = host
        self.port = port
        self.config = config
        self.database = database
        self.audit_logger = audit_logger

        # Initialize components
        self.auth_manager = AuthManager()
        self.league_state = LeagueState(
            config.league.league_id if config.league else "default-league",
            database,
            config
        )
        self.registration_handler = RegistrationHandler(
            self.league_state,
            database,
            self.auth_manager
        )
        self.scheduler = RoundRobinScheduler(database)
        self.http_client = LeagueHTTPClient()
        self.match_assigner = MatchAssigner(database, self.http_client)
        self.standings_engine = StandingsEngine(database)

        # Initialize HTTP server
        self.http_server = LeagueHTTPServer(
            host,
            port,
            self._handle_request,
            self._get_status
        )

        # Message handlers
        self._handlers: Dict[MessageType, Callable] = {
            MessageType.REGISTER_REFEREE_REQUEST: self._handle_register_referee,
            MessageType.REGISTER_PLAYER_REQUEST: self._handle_register_player,
            MessageType.MATCH_RESULT_REPORT: self._handle_match_result,
            MessageType.QUERY_STANDINGS: self._handle_query_standings,
        }

    def start(self):
        """Start the League Manager server."""
        # Initialize league state
        self.league_state.initialize()

        # Start HTTP server
        self.http_server.start()
        logger.info(f"League Manager started on {self.host}:{self.port}")
        logger.info(f"League ID: {self.league_state.league_id}, Status: {self.league_state.status}")

    def stop(self):
        """Stop the League Manager server."""
        self.http_server.stop()
        self.database.close()
        logger.info("League Manager stopped")

    def _handle_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle incoming JSON-RPC request.

        Args:
            request: Validated JSON-RPC request

        Returns:
            JSON-RPC response
        """
        try:
            # Extract and validate envelope
            envelope = Envelope.from_dict(request.params['envelope'])
            payload = request.params.get('payload', {})

            # Log request
            self.audit_logger.log_request(
                request,
                envelope.sender,
                "league_manager"
            )

            # Validate authentication (except for registration requests)
            message_type = MessageType(envelope.message_type)
            if message_type not in [MessageType.REGISTER_REFEREE_REQUEST, MessageType.REGISTER_PLAYER_REQUEST]:
                if not envelope.auth_token:
                    raise ValidationError("Missing auth_token", field="auth_token")
                self.auth_manager.verify_sender(envelope.auth_token, envelope.sender)

            # Dispatch to handler
            handler = self._handlers.get(message_type)
            if not handler:
                raise ValidationError(f"Unsupported message type: {message_type}")

            # Call handler
            response_payload = handler(envelope, payload)

            # Create response envelope
            response_envelope = Envelope(
                protocol="league.v2",
                message_type=self._get_response_type(message_type),
                sender="league_manager",
                timestamp=utc_now(),
                conversation_id=envelope.conversation_id,
                league_id=self.league_state.league_id
            )

            # Create response
            response = create_success_response(
                response_envelope,
                response_payload,
                request.id
            )

            # Log response
            self.audit_logger.log_response(
                response,
                "league_manager",
                envelope.sender,
                envelope.conversation_id
            )

            return response

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

    def _handle_register_referee(
        self,
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle referee registration request."""
        referee_id = payload.get('referee_id')
        if not referee_id:
            raise ValidationError("Missing referee_id", field="referee_id")

        return self.registration_handler.register_referee(referee_id, envelope)

    def _handle_register_player(
        self,
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle player registration request."""
        player_id = payload.get('player_id')
        if not player_id:
            raise ValidationError("Missing player_id", field="player_id")

        return self.registration_handler.register_player(player_id, envelope)

    def _handle_match_result(
        self,
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle match result report."""
        match_id = envelope.match_id
        if not match_id:
            raise ValidationError("Missing match_id in envelope", field="match_id")

        # Validate match exists
        match = self.database.get_match(match_id)
        if not match:
            raise ValidationError(f"Unknown match_id: {match_id}", field="match_id")

        # Check for duplicate result
        existing_result = self.database.get_result(match_id)
        if existing_result:
            raise ValidationError(
                f"Result already reported for match {match_id}",
                field="match_id"
            )

        # Extract result data
        outcome = payload.get('outcome', {})
        points = payload.get('points', {})
        game_metadata = payload.get('game_metadata')

        # Store result
        result_id = f"result-{uuid.uuid4()}"
        self.database.store_result(
            result_id,
            match_id,
            outcome,
            points,
            game_metadata,
            utc_now()
        )

        # Update match status
        self.database.update_match_status(match_id, 'COMPLETED')

        # Recompute standings
        self.standings_engine.publish_standings(
            self.league_state.league_id,
            envelope.round_id
        )

        logger.info(f"Match result recorded: {match_id}")

        return {
            'status': 'acknowledged',
            'match_id': match_id
        }

    def _handle_query_standings(
        self,
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle standings query."""
        round_id = payload.get('round_id')

        standings = self.standings_engine.get_standings(
            self.league_state.league_id,
            round_id
        )

        if standings:
            return standings
        else:
            # Return empty standings if none computed yet
            return {
                'round_id': round_id,
                'updated_at': utc_now(),
                'standings': []
            }

    def _get_response_type(self, request_type: MessageType) -> str:
        """Get response message type for a request type."""
        response_map = {
            MessageType.REGISTER_REFEREE_REQUEST: MessageType.REGISTER_REFEREE_RESPONSE.value,
            MessageType.REGISTER_PLAYER_REQUEST: MessageType.REGISTER_PLAYER_RESPONSE.value,
            MessageType.MATCH_RESULT_REPORT: MessageType.MATCH_RESULT_ACK.value,
            MessageType.QUERY_STANDINGS: MessageType.STANDINGS_RESPONSE.value,
        }
        return response_map.get(request_type, "UNKNOWN_RESPONSE")

    def _get_status(self) -> Dict[str, Any]:
        """Get server status for health endpoint."""
        return {
            'status': self.league_state.status.value,
            'league_id': self.league_state.league_id,
            'referees': self.league_state.get_referee_count(),
            'players': self.league_state.get_player_count()
        }

    def close_registration_and_schedule(self):
        """Close registration and generate schedule."""
        if not self.league_state.can_close_registration():
            logger.warning("Cannot close registration: minimum requirements not met")
            return False

        # Transition to scheduling
        if not self.league_state.transition_to(LeagueStatus.SCHEDULING):
            return False

        # Get all players
        players = self.league_state.get_active_players()
        player_ids = [p['player_id'] for p in players]

        # Generate schedule
        game_type = "tic_tac_toe"  # Default game type
        schedule = self.scheduler.generate_schedule(
            self.league_state.league_id,
            player_ids,
            game_type
        )

        logger.info(f"Generated schedule: {schedule['total_rounds']} rounds, {schedule['total_matches']} matches")

        # Transition to active
        self.league_state.transition_to(LeagueStatus.ACTIVE)

        # Assign matches
        self.match_assigner.assign_pending_matches(self.league_state.league_id)

        return True
