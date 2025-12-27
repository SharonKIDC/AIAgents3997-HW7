"""Standings computation for the Agent League System.

This module implements deterministic standings calculation with
tie-breaking rules as specified in the PRD.
"""

import logging
import uuid
from collections import defaultdict
from typing import Any, Dict

from ..common.persistence import LeagueDatabase, PlayerRanking
from ..common.protocol import utc_now

logger = logging.getLogger(__name__)


class StandingsEngine:
    """Computes and manages league standings."""

    def __init__(self, database: LeagueDatabase):
        """Initialize the standings engine.

        Args:
            database: Database connection
        """
        self.database = database

    def compute_standings(self, league_id: str, round_id: str = None) -> Dict[str, Any]:
        """Compute current standings from match results.

        Standings are sorted by:
        1. Total points (DESC)
        2. Wins (DESC)
        3. Draws (DESC)
        4. Player ID (ASC) - for deterministic tie-breaking

        Args:
            league_id: League identifier
            round_id: Optional round ID for round-specific standings

        Returns:
            Dictionary with standings information
        """
        # Get all match results for the league
        all_results = self.database.get_all_results(league_id)

        # Aggregate statistics per player
        player_stats = defaultdict(lambda: {"points": 0, "wins": 0, "draws": 0, "losses": 0, "matches_played": 0})

        for result in all_results:
            outcome = result["outcome"]
            points = result["points"]

            for player_id, player_outcome in outcome.items():
                stats = player_stats[player_id]
                stats["points"] += points.get(player_id, 0)
                stats["matches_played"] += 1

                if player_outcome == "win":
                    stats["wins"] += 1
                elif player_outcome == "draw":
                    stats["draws"] += 1
                elif player_outcome == "loss":
                    stats["losses"] += 1

        # Sort players by standings rules
        sorted_players = sorted(
            player_stats.items(),
            key=lambda x: (
                -x[1]["points"],  # Points descending
                -x[1]["wins"],  # Wins descending
                -x[1]["draws"],  # Draws descending
                x[0],  # Player ID ascending (deterministic)
            ),
        )

        # Create rankings list
        rankings = []
        for rank, (player_id, stats) in enumerate(sorted_players, 1):
            rankings.append(
                {
                    "rank": rank,
                    "player_id": player_id,
                    "points": stats["points"],
                    "wins": stats["wins"],
                    "draws": stats["draws"],
                    "losses": stats["losses"],
                    "matches_played": stats["matches_played"],
                }
            )

        # Include players with no matches (sorted by player_id for determinism)
        all_players = self.database.get_all_players(league_id)
        players_without_matches = []
        for player in all_players:
            player_id = player["player_id"]
            if player_id not in player_stats:
                players_without_matches.append(player_id)

        # Sort players without matches alphabetically
        for player_id in sorted(players_without_matches):
            rankings.append(
                {
                    "rank": len(rankings) + 1,
                    "player_id": player_id,
                    "points": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "matches_played": 0,
                }
            )

        standings_data = {"league_id": league_id, "round_id": round_id, "updated_at": utc_now(), "standings": rankings}

        logger.info("Computed standings for league %s: %s players", league_id, len(rankings))
        return standings_data

    def publish_standings(self, league_id: str, round_id: str = None) -> str:
        """Compute and persist standings snapshot.

        Args:
            league_id: League identifier
            round_id: Optional round ID

        Returns:
            Snapshot ID
        """
        # Compute standings
        standings = self.compute_standings(league_id, round_id)

        # Create snapshot
        snapshot_id = f"snapshot-{uuid.uuid4()}"
        self.database.create_standings_snapshot(snapshot_id, league_id, round_id, standings["updated_at"])

        # Store rankings
        for ranking in standings["standings"]:
            self.database.store_player_ranking(
                snapshot_id,
                ranking["player_id"],
                PlayerRanking(
                    rank=ranking["rank"],
                    points=ranking["points"],
                    wins=ranking["wins"],
                    draws=ranking["draws"],
                    losses=ranking["losses"],
                    matches_played=ranking["matches_played"],
                ),
            )

        logger.info("Published standings snapshot %s", snapshot_id)
        return snapshot_id

    def get_standings(self, league_id: str, round_id: str = None) -> Dict[str, Any]:
        """Get published standings.

        Args:
            league_id: League identifier
            round_id: Optional round ID

        Returns:
            Standings data or None if not found
        """
        standings = self.database.get_standings(league_id, round_id)
        if standings:
            return {
                "round_id": standings["round_id"],
                "updated_at": standings["computed_at"],
                "standings": standings["rankings"],
            }
        return None
