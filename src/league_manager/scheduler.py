"""Round-robin scheduling for the Agent League System.

This module implements deterministic round-robin scheduling as specified
in ADR-002, ensuring each player plays every other player exactly once.
"""

import itertools
import logging
import uuid
from typing import Any, Dict, List, Tuple

from ..common.persistence import LeagueDatabase

logger = logging.getLogger(__name__)


class RoundRobinScheduler:
    """Implements deterministic round-robin scheduling.

    The algorithm ensures:
    - Each player plays every other player exactly once
    - Matches are grouped into rounds where no player appears twice
    - Schedule is deterministic (same players -> same schedule)
    """

    def __init__(self, database: LeagueDatabase):
        """Initialize the scheduler.

        Args:
            database: Database connection
        """
        self.database = database

    def generate_schedule(
        self,
        league_id: str,
        player_ids: List[str],
        game_type: str
    ) -> Dict[str, Any]:
        """Generate a complete round-robin schedule.

        Args:
            league_id: League identifier
            player_ids: List of player IDs (will be sorted for determinism)
            game_type: Type of game to be played

        Returns:
            Dictionary with schedule information
        """
        # Sort player IDs for determinism
        sorted_players = sorted(player_ids)
        n = len(sorted_players)

        if n < 2:
            logger.warning("Need at least 2 players for scheduling")
            return {
                'rounds': [],
                'total_matches': 0,
                'total_rounds': 0
            }

        # Generate all unique pairs
        all_matches = list(itertools.combinations(sorted_players, 2))
        total_matches = len(all_matches)

        logger.info("Generating schedule for %s players: %s total matches", n, total_matches)

        # Group matches into rounds using round-robin algorithm
        rounds = self._group_into_rounds(sorted_players, all_matches)

        # Store rounds and matches in database
        schedule_info = {
            'rounds': [],
            'total_matches': total_matches,
            'total_rounds': len(rounds)
        }

        for round_number, round_matches in enumerate(rounds, 1):
            round_id = f"round-{uuid.uuid4()}"

            # Create round in database
            self.database.create_round(
                round_id,
                league_id,
                round_number,
                status='PENDING'
            )

            # Create matches
            match_infos = []
            for player_a, player_b in round_matches:
                match_id = f"match-{uuid.uuid4()}"

                self.database.create_match(
                    match_id,
                    round_id,
                    game_type,
                    players=[player_a, player_b],
                    status='PENDING'
                )

                match_infos.append({
                    'match_id': match_id,
                    'players': [player_a, player_b]
                })

            schedule_info['rounds'].append({
                'round_id': round_id,
                'round_number': round_number,
                'matches': match_infos
            })

        logger.info("Created schedule with %s rounds and %s matches", len(rounds), total_matches)
        return schedule_info

    def _group_into_rounds(
        self,
        _players: List[str],
        matches: List[Tuple[str, str]]
    ) -> List[List[Tuple[str, str]]]:
        """Group matches into rounds where no player appears twice.

        This uses a greedy algorithm to create rounds with maximum
        concurrent matches.

        Args:
            _players: List of player IDs (unused, inferred from matches)
            matches: List of match pairs

        Returns:
            List of rounds, where each round is a list of match pairs
        """
        rounds = []
        remaining_matches = matches.copy()

        while remaining_matches:
            # Create a new round
            current_round = []
            players_in_round = set()

            # Greedy selection: add matches that don't conflict
            matches_to_remove = []
            for match in remaining_matches:
                player_a, player_b = match
                if player_a not in players_in_round and player_b not in players_in_round:
                    current_round.append(match)
                    players_in_round.add(player_a)
                    players_in_round.add(player_b)
                    matches_to_remove.append(match)

            # Remove assigned matches
            for match in matches_to_remove:
                remaining_matches.remove(match)

            rounds.append(current_round)

        return rounds

    def get_schedule(self, _league_id: str) -> Dict[str, Any]:
        """Retrieve the generated schedule for a league.

        Args:
            _league_id: League identifier (unused, placeholder implementation)

        Returns:
            Schedule information
        """
        # This would query the database for the existing schedule
        # For now, return a placeholder
        return {
            'rounds': [],
            'total_matches': 0,
            'total_rounds': 0
        }
