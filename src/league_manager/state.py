"""League state management for the Agent League System.

This module manages the lifecycle state of the league and provides
centralized access to league configuration and status.
"""

from enum import Enum
from typing import Dict, Any
import logging

from ..common.persistence import LeagueDatabase
from ..common.config import ConfigManager
from ..common.protocol import utc_now

logger = logging.getLogger(__name__)


class LeagueStatus(str, Enum):
    """League lifecycle states."""
    INIT = "INIT"
    REGISTRATION = "REGISTRATION"
    SCHEDULING = "SCHEDULING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class AgentStatus(str, Enum):
    """Agent lifecycle states."""
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    SHUTDOWN = "SHUTDOWN"


class LeagueState:
    """Manages league state and lifecycle transitions."""

    def __init__(
        self,
        league_id: str,
        database: LeagueDatabase,
        config: ConfigManager
    ):
        """Initialize league state manager.

        Args:
            league_id: Unique league identifier
            database: Database connection
            config: Configuration manager
        """
        self.league_id = league_id
        self.database = database
        self.config = config
        self._status = LeagueStatus.INIT

    def initialize(self):
        """Initialize the league in the database."""
        # Check if league already exists
        existing = self.database.get_league(self.league_id)
        if existing:
            self._status = LeagueStatus(existing['status'])
            logger.info(f"Loaded existing league {self.league_id} with status {self._status}")
        else:
            # Create new league
            config_data = {
                'league_id': self.league_id,
                'name': self.config.league.name if self.config.league else 'Agent League',
                'min_players': self.config.league.min_players if self.config.league else 2,
                'max_players': self.config.league.max_players if self.config.league else 100
            }
            self.database.create_league(
                self.league_id,
                LeagueStatus.REGISTRATION.value,
                utc_now(),
                config_data
            )
            self._status = LeagueStatus.REGISTRATION
            logger.info(f"Created new league {self.league_id}")

    def transition_to(self, new_status: LeagueStatus) -> bool:
        """Transition league to a new status.

        Args:
            new_status: Target status

        Returns:
            True if transition was successful
        """
        # Validate transition
        valid_transitions = {
            LeagueStatus.INIT: [LeagueStatus.REGISTRATION],
            LeagueStatus.REGISTRATION: [LeagueStatus.SCHEDULING],
            LeagueStatus.SCHEDULING: [LeagueStatus.ACTIVE],
            LeagueStatus.ACTIVE: [LeagueStatus.COMPLETED],
            LeagueStatus.COMPLETED: []
        }

        if new_status not in valid_transitions.get(self._status, []):
            logger.error(f"Invalid transition from {self._status} to {new_status}")
            return False

        # Update database
        self.database.update_league_status(self.league_id, new_status.value)
        old_status = self._status
        self._status = new_status
        logger.info(f"League {self.league_id} transitioned from {old_status} to {new_status}")
        return True

    @property
    def status(self) -> LeagueStatus:
        """Get current league status."""
        return self._status

    def is_registration_open(self) -> bool:
        """Check if registration is open."""
        return self._status == LeagueStatus.REGISTRATION

    def is_active(self) -> bool:
        """Check if league is active."""
        return self._status == LeagueStatus.ACTIVE

    def is_completed(self) -> bool:
        """Check if league is completed."""
        return self._status == LeagueStatus.COMPLETED

    def get_referee_count(self) -> int:
        """Get count of registered referees."""
        referees = self.database.get_all_referees(self.league_id)
        return len([r for r in referees if r['status'] in ['REGISTERED', 'ACTIVE']])

    def get_player_count(self) -> int:
        """Get count of registered players."""
        players = self.database.get_all_players(self.league_id)
        return len([p for p in players if p['status'] in ['REGISTERED', 'ACTIVE']])

    def get_active_referees(self) -> list:
        """Get list of active referees."""
        referees = self.database.get_all_referees(self.league_id)
        return [r for r in referees if r['status'] == 'ACTIVE']

    def get_active_players(self) -> list:
        """Get list of active players."""
        players = self.database.get_all_players(self.league_id)
        return [p for p in players if p['status'] in ['REGISTERED', 'ACTIVE']]

    def can_close_registration(self) -> bool:
        """Check if registration can be closed.

        Returns:
            True if minimum requirements are met
        """
        if not self.config.league:
            return False

        referee_count = self.get_referee_count()
        player_count = self.get_player_count()

        return (
            referee_count >= self.config.league.min_referees and
            player_count >= self.config.league.min_players
        )

    def to_dict(self) -> Dict[str, Any]:
        """Get league state as dictionary.

        Returns:
            Dictionary representation of league state
        """
        return {
            'league_id': self.league_id,
            'status': self._status.value,
            'referee_count': self.get_referee_count(),
            'player_count': self.get_player_count()
        }
