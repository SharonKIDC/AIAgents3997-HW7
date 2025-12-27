"""Base class for agent servers (Player and Referee).

This module provides common functionality for agent registration,
ready signaling, and HTTP server initialization.
"""

import logging
from typing import Any, Dict

from .errors import LeagueError
from .protocol import (
    Envelope,
    MessageType,
    generate_conversation_id,
    utc_now,
)
from .transport import LeagueHTTPClient, LeagueHTTPServer

logger = logging.getLogger(__name__)


class AgentServerBase:
    """Base class for agent servers providing common registration logic."""

    def __init__(
        self, agent_id: str, agent_type: str, *, host: str, port: int, league_manager_url: str
    ):
        """Initialize the agent server base.

        Args:
            agent_id: Agent identifier
            agent_type: Agent type ("player" or "referee")
            host: Host to bind to
            port: Port to bind to
            league_manager_url: URL of League Manager
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.host = host
        self.port = port
        self.league_manager_url = league_manager_url
        self.auth_token = None
        self.league_id = None

        # HTTP client
        self.http_client = LeagueHTTPClient()
        # HTTP server will be initialized by subclass

    def _create_http_server(self, request_handler, status_handler) -> LeagueHTTPServer:
        """Create HTTP server instance.

        Args:
            request_handler: Function to handle requests
            status_handler: Function to get status

        Returns:
            Configured LeagueHTTPServer
        """
        return LeagueHTTPServer(self.host, self.port, request_handler, status_handler)

    def register(self) -> bool:
        """Register with the League Manager.

        Must be implemented by subclass.

        Returns:
            True if registration successful
        """
        raise NotImplementedError("Subclass must implement register()")

    def _do_register(self, message_type: MessageType, payload_key: str) -> bool:
        """Perform registration with the League Manager.

        Args:
            message_type: Message type for registration request
            payload_key: Payload key for agent ID (e.g., 'player_id' or 'referee_id')

        Returns:
            True if registration successful
        """
        envelope = Envelope(
            protocol="league.v2",
            message_type=message_type.value,
            sender=f"{self.agent_type}:{self.agent_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )

        payload = {
            payload_key: self.agent_id,
            "endpoint_url": f"http://{self.host}:{self.port}/mcp",
        }

        try:
            result = self.http_client.send_request(self.league_manager_url, envelope, payload)
            response_payload = result.get("payload", {})
            self.auth_token = response_payload.get("auth_token")
            self.league_id = response_payload.get("league_id")
            logger.info(
                "%s registered successfully. League ID: %s",
                self.agent_type.capitalize(),
                self.league_id,
            )
            return True
        except LeagueError as e:
            logger.error("Registration failed: %s", e)
            return False
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Unexpected error during registration")
            return False

    def send_ready(self) -> bool:
        """Send ready signal to League Manager.

        Signals that the agent has completed initialization and is ready
        to participate in the league.

        Returns:
            True if ready signal acknowledged
        """
        if not self.auth_token:
            logger.error("Cannot send ready signal: not registered")
            return False

        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.AGENT_READY_REQUEST.value,
            sender=f"{self.agent_type}:{self.agent_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            auth_token=self.auth_token,
        )

        payload = {}

        try:
            result = self.http_client.send_request(self.league_manager_url, envelope, payload)
            response_payload = result.get("payload", {})
            agent_state = response_payload.get("agent_state")
            logger.info(
                "%s ready signal acknowledged. Status: %s",
                self.agent_type.capitalize(),
                agent_state,
            )
            return True
        except LeagueError as e:
            logger.error("Failed to send ready signal: %s", e)
            return False
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Unexpected error sending ready signal")
            return False

    def _create_response_envelope(
        self, message_type: str, conversation_id: str, match_id: str = None
    ) -> Envelope:
        """Create a response envelope with standard fields.

        Args:
            message_type: Response message type
            conversation_id: Conversation ID from request
            match_id: Optional match ID

        Returns:
            Configured Envelope
        """
        return Envelope(
            protocol="league.v2",
            message_type=message_type,
            sender=f"{self.agent_type}:{self.agent_id}",
            timestamp=utc_now(),
            conversation_id=conversation_id,
            match_id=match_id,
        )

    def _get_base_status(self) -> Dict[str, Any]:
        """Get base status information.

        Returns:
            Status dictionary with common fields
        """
        return {
            f"{self.agent_type}_id": self.agent_id,
            "status": "ACTIVE" if self.auth_token else "INIT",
            "league_id": self.league_id,
        }
