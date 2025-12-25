"""Persistence layer for the Agent League System.

This module provides SQLite database access and abstracts all
database operations for the league system.
"""

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from .errors import DatabaseError


class LeagueDatabase:
    """SQLite database wrapper for league persistence."""

    def __init__(self, db_path: str):
        """Initialize the database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()

    @property
    def conn(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self.conn
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Transaction failed: {str(e)}", error=str(e))

    def initialize_schema(self):
        """Create all database tables if they don't exist."""
        with self.transaction() as conn:
            cursor = conn.cursor()

            # Leagues table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leagues (
                    league_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL CHECK(status IN ('INIT', 'REGISTRATION', 'SCHEDULING', 'ACTIVE', 'COMPLETED')),
                    created_at TEXT NOT NULL,
                    config TEXT NOT NULL
                )
            ''')

            # Referees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS referees (
                    referee_id TEXT PRIMARY KEY,
                    league_id TEXT NOT NULL,
                    auth_token TEXT NOT NULL UNIQUE,
                    endpoint_url TEXT,
                    status TEXT NOT NULL CHECK(status IN ('REGISTERED', 'ACTIVE', 'SUSPENDED', 'SHUTDOWN')),
                    registered_at TEXT NOT NULL,
                    FOREIGN KEY (league_id) REFERENCES leagues(league_id)
                )
            ''')

            # Players table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    player_id TEXT PRIMARY KEY,
                    league_id TEXT NOT NULL,
                    auth_token TEXT NOT NULL UNIQUE,
                    endpoint_url TEXT,
                    status TEXT NOT NULL CHECK(status IN ('REGISTERED', 'ACTIVE', 'SUSPENDED', 'SHUTDOWN')),
                    registered_at TEXT NOT NULL,
                    FOREIGN KEY (league_id) REFERENCES leagues(league_id)
                )
            ''')

            # Rounds table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rounds (
                    round_id TEXT PRIMARY KEY,
                    league_id TEXT NOT NULL,
                    round_number INTEGER NOT NULL,
                    scheduled_at TEXT,
                    status TEXT NOT NULL CHECK(status IN ('PENDING', 'ACTIVE', 'COMPLETED')),
                    FOREIGN KEY (league_id) REFERENCES leagues(league_id)
                )
            ''')

            # Matches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    match_id TEXT PRIMARY KEY,
                    round_id TEXT NOT NULL,
                    referee_id TEXT,
                    game_type TEXT NOT NULL,
                    players TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FAILED')),
                    assigned_at TEXT,
                    FOREIGN KEY (round_id) REFERENCES rounds(round_id),
                    FOREIGN KEY (referee_id) REFERENCES referees(referee_id)
                )
            ''')

            # Match results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS match_results (
                    result_id TEXT PRIMARY KEY,
                    match_id TEXT NOT NULL UNIQUE,
                    outcome TEXT NOT NULL,
                    points TEXT NOT NULL,
                    game_metadata TEXT,
                    reported_at TEXT NOT NULL,
                    FOREIGN KEY (match_id) REFERENCES matches(match_id)
                )
            ''')

            # Standings snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS standings_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    league_id TEXT NOT NULL,
                    round_id TEXT,
                    computed_at TEXT NOT NULL,
                    FOREIGN KEY (league_id) REFERENCES leagues(league_id),
                    FOREIGN KEY (round_id) REFERENCES rounds(round_id)
                )
            ''')

            # Player rankings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_rankings (
                    snapshot_id TEXT NOT NULL,
                    player_id TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    points INTEGER NOT NULL DEFAULT 0,
                    wins INTEGER NOT NULL DEFAULT 0,
                    draws INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    matches_played INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (snapshot_id, player_id),
                    FOREIGN KEY (snapshot_id) REFERENCES standings_snapshots(snapshot_id),
                    FOREIGN KEY (player_id) REFERENCES players(player_id)
                )
            ''')

    # League operations
    def create_league(self, league_id: str, status: str, created_at: str, config: Dict[str, Any]):
        """Create a new league record."""
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO leagues (league_id, status, created_at, config) VALUES (?, ?, ?, ?)',
                (league_id, status, created_at, json.dumps(config))
            )

    def update_league_status(self, league_id: str, status: str):
        """Update league status."""
        with self.transaction() as conn:
            conn.execute(
                'UPDATE leagues SET status = ? WHERE league_id = ?',
                (status, league_id)
            )

    def get_league(self, league_id: str) -> Optional[Dict[str, Any]]:
        """Get league information."""
        cursor = self.conn.execute(
            'SELECT * FROM leagues WHERE league_id = ?',
            (league_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    # Referee operations
    def register_referee(self, referee_id: str, league_id: str, auth_token: str, registered_at: str, endpoint_url: str = None):
        """Register a new referee."""
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO referees (referee_id, league_id, auth_token, endpoint_url, status, registered_at) VALUES (?, ?, ?, ?, ?, ?)',
                (referee_id, league_id, auth_token, endpoint_url, 'REGISTERED', registered_at)
            )

    def get_referee(self, referee_id: str) -> Optional[Dict[str, Any]]:
        """Get referee information."""
        cursor = self.conn.execute(
            'SELECT * FROM referees WHERE referee_id = ?',
            (referee_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_referees(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all referees for a league."""
        cursor = self.conn.execute(
            'SELECT * FROM referees WHERE league_id = ?',
            (league_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def update_referee_status(self, referee_id: str, status: str):
        """Update referee status."""
        with self.transaction() as conn:
            conn.execute(
                'UPDATE referees SET status = ? WHERE referee_id = ?',
                (status, referee_id)
            )

    # Player operations
    def register_player(self, player_id: str, league_id: str, auth_token: str, registered_at: str, endpoint_url: str = None):
        """Register a new player."""
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO players (player_id, league_id, auth_token, endpoint_url, status, registered_at) VALUES (?, ?, ?, ?, ?, ?)',
                (player_id, league_id, auth_token, endpoint_url, 'REGISTERED', registered_at)
            )

    def get_player(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get player information."""
        cursor = self.conn.execute(
            'SELECT * FROM players WHERE player_id = ?',
            (player_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_players(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all players for a league."""
        cursor = self.conn.execute(
            'SELECT * FROM players WHERE league_id = ?',
            (league_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def update_player_status(self, player_id: str, status: str):
        """Update player status."""
        with self.transaction() as conn:
            conn.execute(
                'UPDATE players SET status = ? WHERE player_id = ?',
                (status, player_id)
            )

    # Round operations
    def create_round(self, round_id: str, league_id: str, round_number: int, status: str = 'PENDING'):
        """Create a new round."""
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO rounds (round_id, league_id, round_number, status) VALUES (?, ?, ?, ?)',
                (round_id, league_id, round_number, status)
            )

    def update_round_status(self, round_id: str, status: str):
        """Update round status."""
        with self.transaction() as conn:
            conn.execute(
                'UPDATE rounds SET status = ? WHERE round_id = ?',
                (status, round_id)
            )

    # Match operations
    def create_match(
        self,
        match_id: str,
        round_id: str,
        game_type: str,
        players: List[str],
        status: str = 'PENDING'
    ):
        """Create a new match."""
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO matches (match_id, round_id, game_type, players, status) VALUES (?, ?, ?, ?, ?)',
                (match_id, round_id, game_type, json.dumps(players), status)
            )

    def assign_match(self, match_id: str, referee_id: str, assigned_at: str):
        """Assign a match to a referee."""
        with self.transaction() as conn:
            conn.execute(
                'UPDATE matches SET referee_id = ?, status = ?, assigned_at = ? WHERE match_id = ?',
                (referee_id, 'ASSIGNED', assigned_at, match_id)
            )

    def update_match_status(self, match_id: str, status: str):
        """Update match status."""
        with self.transaction() as conn:
            conn.execute(
                'UPDATE matches SET status = ? WHERE match_id = ?',
                (status, match_id)
            )

    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get match information."""
        cursor = self.conn.execute(
            'SELECT * FROM matches WHERE match_id = ?',
            (match_id,)
        )
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result['players'] = json.loads(result['players'])
            return result
        return None

    def get_pending_matches(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all pending matches for a league."""
        cursor = self.conn.execute('''
            SELECT m.* FROM matches m
            JOIN rounds r ON m.round_id = r.round_id
            WHERE r.league_id = ? AND m.status = 'PENDING'
        ''', (league_id,))
        results = []
        for row in cursor.fetchall():
            match = dict(row)
            match['players'] = json.loads(match['players'])
            results.append(match)
        return results

    # Result operations
    def store_result(
        self,
        result_id: str,
        match_id: str,
        outcome: Dict[str, str],
        points: Dict[str, int],
        game_metadata: Optional[Dict[str, Any]],
        reported_at: str
    ):
        """Store a match result."""
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO match_results (result_id, match_id, outcome, points, game_metadata, reported_at) VALUES (?, ?, ?, ?, ?, ?)',
                (result_id, match_id, json.dumps(outcome), json.dumps(points), json.dumps(game_metadata) if game_metadata else None, reported_at)
            )

    def get_result(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get result for a match."""
        cursor = self.conn.execute(
            'SELECT * FROM match_results WHERE match_id = ?',
            (match_id,)
        )
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result['outcome'] = json.loads(result['outcome'])
            result['points'] = json.loads(result['points'])
            if result['game_metadata']:
                result['game_metadata'] = json.loads(result['game_metadata'])
            return result
        return None

    def get_all_results(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all results for a league."""
        cursor = self.conn.execute('''
            SELECT mr.* FROM match_results mr
            JOIN matches m ON mr.match_id = m.match_id
            JOIN rounds r ON m.round_id = r.round_id
            WHERE r.league_id = ?
        ''', (league_id,))
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            result['outcome'] = json.loads(result['outcome'])
            result['points'] = json.loads(result['points'])
            if result['game_metadata']:
                result['game_metadata'] = json.loads(result['game_metadata'])
            results.append(result)
        return results

    # Standings operations
    def create_standings_snapshot(self, snapshot_id: str, league_id: str, round_id: Optional[str], computed_at: str):
        """Create a standings snapshot."""
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO standings_snapshots (snapshot_id, league_id, round_id, computed_at) VALUES (?, ?, ?, ?)',
                (snapshot_id, league_id, round_id, computed_at)
            )

    def store_player_ranking(
        self,
        snapshot_id: str,
        player_id: str,
        rank: int,
        points: int,
        wins: int,
        draws: int,
        losses: int,
        matches_played: int
    ):
        """Store a player ranking in a snapshot."""
        with self.transaction() as conn:
            conn.execute(
                'INSERT INTO player_rankings (snapshot_id, player_id, rank, points, wins, draws, losses, matches_played) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (snapshot_id, player_id, rank, points, wins, draws, losses, matches_played)
            )

    def get_standings(self, league_id: str, round_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get standings for a league or specific round."""
        # Find the most recent snapshot
        if round_id:
            cursor = self.conn.execute(
                'SELECT * FROM standings_snapshots WHERE league_id = ? AND round_id = ? ORDER BY computed_at DESC LIMIT 1',
                (league_id, round_id)
            )
        else:
            cursor = self.conn.execute(
                'SELECT * FROM standings_snapshots WHERE league_id = ? ORDER BY computed_at DESC LIMIT 1',
                (league_id,)
            )

        snapshot = cursor.fetchone()
        if not snapshot:
            return None

        snapshot_id = snapshot['snapshot_id']

        # Get rankings
        cursor = self.conn.execute(
            'SELECT * FROM player_rankings WHERE snapshot_id = ? ORDER BY rank',
            (snapshot_id,)
        )
        rankings = [dict(row) for row in cursor.fetchall()]

        return {
            'snapshot_id': snapshot_id,
            'league_id': snapshot['league_id'],
            'round_id': snapshot['round_id'],
            'computed_at': snapshot['computed_at'],
            'rankings': rankings
        }

    def close(self):
        """Close database connection."""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
