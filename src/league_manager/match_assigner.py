"""Match assignment for the Agent League System.

This module handles assigning pending matches to available referees.
"""

import logging
from typing import Any, Dict, List

from ..common.errors import ErrorCode, OperationalError
from ..common.persistence import LeagueDatabase
from ..common.protocol import Envelope, MessageType, generate_conversation_id, utc_now
from ..common.transport import LeagueHTTPClient

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
            # Find next available referee (round-robin with wraparound)
            referee = active_referees[referee_idx % len(active_referees)]
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
            except OperationalError as e:
                logger.error("Failed to assign match %s to referee %s: %s", match['match_id'], referee_id, e)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Unexpected error assigning match %s to referee %s", match['match_id'], referee_id)

        logger.info("Assigned %s matches to referees", len(assignments))
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
        referee = self.database.get_referee(referee_id)
        if not referee or not referee.get('endpoint_url'):
            raise OperationalError(
                ErrorCode.INVALID_REFEREE_ID,
                f"Referee {referee_id} not found or has no endpoint URL"
            )

        referee_url = referee['endpoint_url']

        # Create MATCH_ASSIGNMENT envelope
        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.MATCH_ASSIGNMENT.value,
            sender="league_manager",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            match_id=match_id,
            round_id=match['round_id'],
            game_type=game_type
        )

        # Get player endpoint URLs
        player_endpoints = {}
        for player_id in players:
            player = self.database.get_player(player_id)
            if player and player.get('endpoint_url'):
                player_endpoints[player_id] = player['endpoint_url']
            else:
                logger.warning("Player %s has no endpoint URL", player_id)

        payload = {
            'match_id': match_id,
            'round_id': match['round_id'],
            'game_type': game_type,
            'players': players,
            'player_endpoints': player_endpoints
        }

        # Send to referee
        try:
            self.http_client.send_request(referee_url, envelope, payload)
            logger.info("Sent match assignment %s to referee %s at %s", match_id, referee_id, referee_url)
        except Exception as e:
            logger.error("Failed to send match assignment to referee %s: %s", referee_id, e)
            raise OperationalError(
                ErrorCode.COMMUNICATION_ERROR,
                f"Failed to send assignment to referee: {str(e)}"
            ) from e

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
        logger.debug("Referee %s marked as busy", referee_id)

    def mark_referee_idle(self, referee_id: str):
        """Mark a referee as idle (available for assignment).

        Args:
            referee_id: Referee identifier
        """
        self._referee_availability[referee_id] = True
        logger.debug("Referee %s marked as idle", referee_id)

    def is_referee_available(self, referee_id: str) -> bool:
        """Check if a referee is available for assignment.

        Args:
            referee_id: Referee identifier

        Returns:
            True if referee is idle and available
        """
        return self._referee_availability.get(referee_id, True)
