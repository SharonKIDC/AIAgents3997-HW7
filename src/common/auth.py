"""Authentication and authorization for the Agent League System.

This module handles token issuance, validation, and authorization checks.
"""

import threading
import uuid
from enum import Enum
from typing import Dict

from .errors import AuthenticationError, AuthorizationError


class AgentType(str, Enum):
    """Types of agents in the league."""
    LEAGUE_MANAGER = "league_manager"
    REFEREE = "referee"
    PLAYER = "player"


class AuthManager:
    """Manages authentication tokens and authorization."""

    def __init__(self):
        """Initialize the authentication manager."""
        self._tokens: Dict[str, Dict[str, str]] = {}  # token -> {agent_id, agent_type}
        self._agent_tokens: Dict[str, str] = {}  # agent_id -> token
        self._lock = threading.Lock()

    def issue_token(self, agent_id: str, agent_type: AgentType) -> str:
        """Issue a new authentication token.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent

        Returns:
            Opaque authentication token (UUID)
        """
        with self._lock:
            # Check if agent already has a token
            if agent_id in self._agent_tokens:
                return self._agent_tokens[agent_id]

            # Generate new token
            token = str(uuid.uuid4())

            # Store mappings
            self._tokens[token] = {
                'agent_id': agent_id,
                'agent_type': agent_type.value
            }
            self._agent_tokens[agent_id] = token

            return token

    def validate_token(self, token: str) -> Dict[str, str]:
        """Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            Dictionary with agent_id and agent_type

        Raises:
            AuthenticationError: If token is invalid
        """
        with self._lock:
            if token not in self._tokens:
                raise AuthenticationError("Invalid or expired token")
            return self._tokens[token].copy()

    def verify_sender(self, token: str, sender: str) -> None:
        """Verify that sender matches the authenticated agent.

        Args:
            token: Authentication token
            sender: Sender identity from envelope

        Raises:
            AuthenticationError: If token is invalid
            AuthorizationError: If sender doesn't match token
        """
        agent_info = self.validate_token(token)
        agent_id = agent_info['agent_id']
        agent_type = agent_info['agent_type']

        # Construct expected sender
        if agent_type == AgentType.LEAGUE_MANAGER:
            expected_sender = "league_manager"
        else:
            expected_sender = f"{agent_type}:{agent_id}"

        if sender != expected_sender:
            raise AuthorizationError(
                f"Sender mismatch: expected {expected_sender}, got {sender}",
                expected=expected_sender,
                actual=sender
            )

    def invalidate_token(self, token: str) -> None:
        """Invalidate a token (e.g., on suspension or shutdown).

        Args:
            token: Token to invalidate
        """
        with self._lock:
            if token in self._tokens:
                agent_id = self._tokens[token]['agent_id']
                del self._tokens[token]
                if agent_id in self._agent_tokens:
                    del self._agent_tokens[agent_id]

    def invalidate_agent(self, agent_id: str) -> None:
        """Invalidate all tokens for an agent.

        Args:
            agent_id: Agent identifier
        """
        with self._lock:
            if agent_id in self._agent_tokens:
                token = self._agent_tokens[agent_id]
                if token in self._tokens:
                    del self._tokens[token]
                del self._agent_tokens[agent_id]

    def get_agent_id(self, token: str) -> str:
        """Get agent ID for a token.

        Args:
            token: Authentication token

        Returns:
            Agent ID

        Raises:
            AuthenticationError: If token is invalid
        """
        return self.validate_token(token)['agent_id']

    def get_agent_type(self, token: str) -> str:
        """Get agent type for a token.

        Args:
            token: Authentication token

        Returns:
            Agent type

        Raises:
            AuthenticationError: If token is invalid
        """
        return self.validate_token(token)['agent_type']

    def has_token(self, agent_id: str) -> bool:
        """Check if an agent has a token.

        Args:
            agent_id: Agent identifier

        Returns:
            True if agent has a token
        """
        with self._lock:
            return agent_id in self._agent_tokens
