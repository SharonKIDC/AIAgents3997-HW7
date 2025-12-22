"""Match assignment for the Agent League System.

This module handles assigning pending matches to available referees.
"""

import logging
from typing import Dict, Any, List

from ..common.persistence import LeagueDatabase
from ..common.protocol import utc_now, generate_conversation_id
from ..common.transport import LeagueHTTPClient
from ..common.errors import OperationalError, ErrorCode

logger = logging.getLogger(__name__)


class MatchAssigner:
    """Assigns matches to available referees."""

    def __init__(
        self,
        database: LeagueDatabase,
        http_client: LeagueHTTPClient
    ):
        """Initialize the match assigner.

        Args:
            database: Database connection
            http_client: HTTP client for sending assignments
        """
        self.database = database
        self.http_client = http_client
        self._referee_availability = {}  # referee_id -> is_idle

    def assign_pending_matches(
        self,
        league_id: str
    ) -> List[Dict[str, Any]]:
        """Assign all pending matches to available referees.

        Args:
            league_id: League identifier

        Returns:
            List of assignment information
        """
        # Get pending matches
        pending_matches = self.database.get_pending_matches(league_id)
        if not pending_matches:
            logger.debug("No pending matches to assign")
            return []

        # Get active referees
        referees = self.database.get_all_referees(league_id)
        active_referees = [r for r in referees if r['status'] == 'ACTIVE']

        if not active_referees:
            logger.warning("No active referees available for match assignment")
            return []

        assignments = []
        referee_idx = 0

        for match in pending_matches:
            # Find next available referee (simple round-robin)
            if referee_idx >= len(active_referees):
                logger.warning("No more available referees for remaining matches")
                break

            referee = active_referees[referee_idx]
            referee_id = referee['referee_id']

            # Assign match
            try:
                assignment_info = self.assign_match(
                    match['match_id'],
                    referee_id,
                    match['game_type'],
                    match['players']
                )
                assignments.append(assignment_info)
                referee_idx += 1
            except Exception as e:
                logger.error(f"Failed to assign match {match['match_id']} to referee {referee_id}: {e}")

        logger.info(f"Assigned {len(assignments)} matches to referees")
        return assignments

    def assign_match(
        self,
        match_id: str,
        referee_id: str,
        game_type: str,
        players: List[str]
    ) -> Dict[str, Any]:
        """Assign a specific match to a referee.

        Args:
            match_id: Match identifier
            referee_id: Referee identifier
            game_type: Game type
            players: List of player IDs

        Returns:
            Assignment information

        Raises:
            OperationalError: If assignment fails
        """
        # Update database
        self.database.assign_match(match_id, referee_id, utc_now())

        # Get match details
        match = self.database.get_match(match_id)
        if not match:
            raise OperationalError(
                ErrorCode.INVALID_MATCH_ID,
                f"Match not found: {match_id}"
            )

        # Send assignment to referee
        # Note: In a full implementation, we would look up referee endpoint
        # For now, we'll log the assignment
        logger.info(f"Assigned match {match_id} to referee {referee_id}")

        return {
            'match_id': match_id,
            'referee_id': referee_id,
            'round_id': match['round_id'],
            'game_type': game_type,
            'players': players,
            'assigned_at': match.get('assigned_at', utc_now())
        }

    def mark_referee_busy(self, referee_id: str):
        """Mark a referee as busy (executing a match).

        Args:
            referee_id: Referee identifier
        """
        self._referee_availability[referee_id] = False
        logger.debug(f"Referee {referee_id} marked as busy")

    def mark_referee_idle(self, referee_id: str):
        """Mark a referee as idle (available for assignment).

        Args:
            referee_id: Referee identifier
        """
        self._referee_availability[referee_id] = True
        logger.debug(f"Referee {referee_id} marked as idle")

    def is_referee_available(self, referee_id: str) -> bool:
        """Check if a referee is available for assignment.

        Args:
            referee_id: Referee identifier

        Returns:
            True if referee is idle and available
        """
        return self._referee_availability.get(referee_id, True)
