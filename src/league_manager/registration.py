"""Registration handler for the Agent League System.

This module handles referee and player registration with the league.
"""

import logging
from typing import Dict, Any

from ..common.persistence import LeagueDatabase
from ..common.auth import AuthManager, AgentType
from ..common.protocol import Envelope, utc_now
from ..common.errors import (
    DuplicateRegistrationError,
    RegistrationClosedError,
    PreconditionFailedError
)
from .state import LeagueState

logger = logging.getLogger(__name__)


class RegistrationHandler:
    """Handles agent registration requests."""

    def __init__(
        self,
        league_state: LeagueState,
        database: LeagueDatabase,
        auth_manager: AuthManager
    ):
        """Initialize the registration handler.

        Args:
            league_state: League state manager
            database: Database connection
            auth_manager: Authentication manager
        """
        self.league_state = league_state
        self.database = database
        self.auth_manager = auth_manager

    def register_referee(
        self,
        referee_id: str,
        envelope: Envelope,
        endpoint_url: str = None
    ) -> Dict[str, Any]:
        """Register a referee with the league.

        Args:
            referee_id: Unique referee identifier
            envelope: Request envelope
            endpoint_url: Referee's endpoint URL for receiving match assignments

        Returns:
            Registration response payload

        Raises:
            DuplicateRegistrationError: If referee already registered
            RegistrationClosedError: If registration is closed
        """
        # Check registration is open
        if not self.league_state.is_registration_open():
            raise RegistrationClosedError()

        # Check for duplicate registration
        existing = self.database.get_referee(referee_id)
        if existing:
            raise DuplicateRegistrationError(referee_id)

        # Issue authentication token
        auth_token = self.auth_manager.issue_token(referee_id, AgentType.REFEREE)

        # Store registration
        self.database.register_referee(
            referee_id,
            self.league_state.league_id,
            auth_token,
            utc_now(),
            endpoint_url
        )

        logger.info(f"Registered referee: {referee_id} at {endpoint_url}")

        return {
            'status': 'registered',
            'auth_token': auth_token,
            'league_id': self.league_state.league_id
        }

    def register_player(
        self,
        player_id: str,
        envelope: Envelope,
        endpoint_url: str = None
    ) -> Dict[str, Any]:
        """Register a player with the league.

        Args:
            player_id: Unique player identifier
            envelope: Request envelope
            endpoint_url: Player's endpoint URL for receiving game invitations

        Returns:
            Registration response payload

        Raises:
            DuplicateRegistrationError: If player already registered
            RegistrationClosedError: If registration is closed
            PreconditionFailedError: If no referees registered
        """
        # Check registration is open
        if not self.league_state.is_registration_open():
            raise RegistrationClosedError()

        # Check at least one referee is registered (PRD Section 3.3)
        if self.league_state.get_referee_count() == 0:
            raise PreconditionFailedError(
                "At least one referee must be registered before players can register",
                referee_count=0
            )

        # Check for duplicate registration
        existing = self.database.get_player(player_id)
        if existing:
            raise DuplicateRegistrationError(player_id)

        # Issue authentication token
        auth_token = self.auth_manager.issue_token(player_id, AgentType.PLAYER)

        # Store registration
        self.database.register_player(
            player_id,
            self.league_state.league_id,
            auth_token,
            utc_now(),
            endpoint_url
        )

        logger.info(f"Registered player: {player_id} at {endpoint_url}")

        return {
            'status': 'registered',
            'auth_token': auth_token,
            'league_id': self.league_state.league_id
        }
