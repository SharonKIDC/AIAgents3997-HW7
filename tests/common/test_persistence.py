"""Tests for database persistence layer.

This module tests all database operations for the league system.
"""

from src.common.persistence import PlayerRanking
from src.common.protocol import utc_now


class TestLeagueDatabase:
    """Tests for LeagueDatabase class."""

    def test_database_initialization(self, temp_db):
        """Test database schema creation."""
        # Schema should be created automatically
        cursor = temp_db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = [
            "leagues",
            "referees",
            "players",
            "rounds",
            "matches",
            "match_results",
            "standings_snapshots",
            "player_rankings",
        ]

        for table in expected_tables:
            assert table in tables


class TestLeagueOperations:
    """Tests for league CRUD operations."""

    def test_create_league(self, temp_db):
        """Test creating a league."""
        temp_db.create_league("league-1", "REGISTRATION", utc_now(), {"name": "Test League"})

        league = temp_db.get_league("league-1")
        assert league is not None
        assert league["league_id"] == "league-1"
        assert league["status"] == "REGISTRATION"

    def test_update_league_status(self, temp_db):
        """Test updating league status."""
        temp_db.create_league("league-1", "REGISTRATION", utc_now(), {})

        temp_db.update_league_status("league-1", "ACTIVE")

        league = temp_db.get_league("league-1")
        assert league["status"] == "ACTIVE"

    def test_get_nonexistent_league(self, temp_db):
        """Test getting non-existent league returns None."""
        league = temp_db.get_league("nonexistent")
        assert league is None


class TestRefereeOperations:
    """Tests for referee CRUD operations."""

    def test_register_referee(self, temp_db, sample_league_id):
        """Test registering a referee."""
        temp_db.create_league(sample_league_id, "REGISTRATION", utc_now(), {})

        temp_db.register_referee(
            "ref-1", sample_league_id, auth_token="token-123", registered_at=utc_now()
        )

        referee = temp_db.get_referee("ref-1")
        assert referee is not None
        assert referee["referee_id"] == "ref-1"
        assert referee["status"] == "REGISTERED"

    def test_get_all_referees(self, temp_db, sample_league_id):
        """Test getting all referees for a league."""
        temp_db.create_league(sample_league_id, "REGISTRATION", utc_now(), {})

        temp_db.register_referee(
            "ref-1", sample_league_id, auth_token="token-1", registered_at=utc_now()
        )
        temp_db.register_referee(
            "ref-2", sample_league_id, auth_token="token-2", registered_at=utc_now()
        )

        referees = temp_db.get_all_referees(sample_league_id)
        assert len(referees) == 2
        assert {r["referee_id"] for r in referees} == {"ref-1", "ref-2"}

    def test_update_referee_status(self, temp_db, sample_league_id):
        """Test updating referee status."""
        temp_db.create_league(sample_league_id, "REGISTRATION", utc_now(), {})
        temp_db.register_referee(
            "ref-1", sample_league_id, auth_token="token-1", registered_at=utc_now()
        )

        temp_db.update_referee_status("ref-1", "ACTIVE")

        referee = temp_db.get_referee("ref-1")
        assert referee["status"] == "ACTIVE"


class TestPlayerOperations:
    """Tests for player CRUD operations."""

    def test_register_player(self, temp_db, sample_league_id):
        """Test registering a player."""
        temp_db.create_league(sample_league_id, "REGISTRATION", utc_now(), {})

        temp_db.register_player(
            "alice", sample_league_id, auth_token="token-abc", registered_at=utc_now()
        )

        player = temp_db.get_player("alice")
        assert player is not None
        assert player["player_id"] == "alice"
        assert player["status"] == "REGISTERED"

    def test_get_all_players(self, temp_db, sample_league_id):
        """Test getting all players for a league."""
        temp_db.create_league(sample_league_id, "REGISTRATION", utc_now(), {})

        temp_db.register_player(
            "alice", sample_league_id, auth_token="token-1", registered_at=utc_now()
        )
        temp_db.register_player(
            "bob", sample_league_id, auth_token="token-2", registered_at=utc_now()
        )
        temp_db.register_player(
            "charlie", sample_league_id, auth_token="token-3", registered_at=utc_now()
        )

        players = temp_db.get_all_players(sample_league_id)
        assert len(players) == 3
        assert {p["player_id"] for p in players} == {"alice", "bob", "charlie"}

    def test_update_player_status(self, temp_db, sample_league_id):
        """Test updating player status."""
        temp_db.create_league(sample_league_id, "REGISTRATION", utc_now(), {})
        temp_db.register_player(
            "alice", sample_league_id, auth_token="token-1", registered_at=utc_now()
        )

        temp_db.update_player_status("alice", "SUSPENDED")

        player = temp_db.get_player("alice")
        assert player["status"] == "SUSPENDED"


class TestRoundOperations:
    """Tests for round CRUD operations."""

    def test_create_round(self, temp_db, sample_league_id):
        """Test creating a round."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})

        temp_db.create_round("round-1", sample_league_id, 1, "PENDING")

        # Verify round exists
        cursor = temp_db.conn.execute("SELECT * FROM rounds WHERE round_id = ?", ("round-1",))
        round_row = cursor.fetchone()
        assert round_row is not None
        assert round_row["round_number"] == 1

    def test_update_round_status(self, temp_db, sample_league_id):
        """Test updating round status."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.create_round("round-1", sample_league_id, 1, "PENDING")

        temp_db.update_round_status("round-1", "ACTIVE")

        cursor = temp_db.conn.execute("SELECT status FROM rounds WHERE round_id = ?", ("round-1",))
        row = cursor.fetchone()
        assert row["status"] == "ACTIVE"


class TestMatchOperations:
    """Tests for match CRUD operations."""

    def test_create_match(self, temp_db, sample_league_id):
        """Test creating a match."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.create_round("round-1", sample_league_id, 1)

        temp_db.create_match(
            "match-1", "round-1", "tic_tac_toe", players=["alice", "bob"], status="PENDING"
        )

        match = temp_db.get_match("match-1")
        assert match is not None
        assert match["match_id"] == "match-1"
        assert match["players"] == ["alice", "bob"]
        assert match["game_type"] == "tic_tac_toe"

    def test_assign_match(self, temp_db, sample_league_id):
        """Test assigning a match to a referee."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.register_referee(
            "ref-1", sample_league_id, auth_token="token", registered_at=utc_now()
        )
        temp_db.create_round("round-1", sample_league_id, 1)
        temp_db.create_match("match-1", "round-1", "tic_tac_toe", players=["alice", "bob"])

        temp_db.assign_match("match-1", "ref-1", utc_now())

        match = temp_db.get_match("match-1")
        assert match["referee_id"] == "ref-1"
        assert match["status"] == "ASSIGNED"

    def test_update_match_status(self, temp_db, sample_league_id):
        """Test updating match status."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.create_round("round-1", sample_league_id, 1)
        temp_db.create_match("match-1", "round-1", "tic_tac_toe", players=["alice", "bob"])

        temp_db.update_match_status("match-1", "IN_PROGRESS")

        match = temp_db.get_match("match-1")
        assert match["status"] == "IN_PROGRESS"

    def test_get_pending_matches(self, temp_db, sample_league_id):
        """Test getting pending matches."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.create_round("round-1", sample_league_id, 1)
        temp_db.create_match(
            "match-1", "round-1", "tic_tac_toe", players=["alice", "bob"], status="PENDING"
        )
        temp_db.create_match(
            "match-2", "round-1", "tic_tac_toe", players=["charlie", "dave"], status="PENDING"
        )
        temp_db.create_match(
            "match-3", "round-1", "tic_tac_toe", players=["alice", "charlie"], status="COMPLETED"
        )

        pending = temp_db.get_pending_matches(sample_league_id)
        assert len(pending) == 2
        assert {m["match_id"] for m in pending} == {"match-1", "match-2"}


class TestResultOperations:
    """Tests for match result operations."""

    def test_store_result(self, temp_db, sample_league_id):
        """Test storing a match result."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.create_round("round-1", sample_league_id, 1)
        temp_db.create_match("match-1", "round-1", "tic_tac_toe", players=["alice", "bob"])

        temp_db.store_result(
            "result-1",
            "match-1",
            outcome={"alice": "win", "bob": "loss"},
            points={"alice": 3, "bob": 0},
            game_metadata={"moves": 5},
            reported_at=utc_now(),
        )

        result = temp_db.get_result("match-1")
        assert result is not None
        assert result["outcome"] == {"alice": "win", "bob": "loss"}
        assert result["points"] == {"alice": 3, "bob": 0}

    def test_get_all_results(self, temp_db, sample_league_id):
        """Test getting all results for a league."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.create_round("round-1", sample_league_id, 1)
        temp_db.create_match("match-1", "round-1", "tic_tac_toe", players=["alice", "bob"])
        temp_db.create_match("match-2", "round-1", "tic_tac_toe", players=["charlie", "dave"])

        temp_db.store_result(
            "result-1",
            "match-1",
            outcome={"alice": "win", "bob": "loss"},
            points={"alice": 3, "bob": 0},
            game_metadata=None,
            reported_at=utc_now(),
        )
        temp_db.store_result(
            "result-2",
            "match-2",
            outcome={"charlie": "draw", "dave": "draw"},
            points={"charlie": 1, "dave": 1},
            game_metadata=None,
            reported_at=utc_now(),
        )

        results = temp_db.get_all_results(sample_league_id)
        assert len(results) == 2


class TestStandingsOperations:
    """Tests for standings operations."""

    def test_create_standings_snapshot(self, temp_db, sample_league_id):
        """Test creating a standings snapshot."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.create_round("round-1", sample_league_id, 1)

        temp_db.create_standings_snapshot("snapshot-1", sample_league_id, "round-1", utc_now())

        # Verify snapshot exists
        cursor = temp_db.conn.execute(
            "SELECT * FROM standings_snapshots WHERE snapshot_id = ?", ("snapshot-1",)
        )
        row = cursor.fetchone()
        assert row is not None

    def test_store_player_ranking(self, temp_db, sample_league_id):
        """Test storing player rankings."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.register_player(
            "alice", sample_league_id, auth_token="token", registered_at=utc_now()
        )
        temp_db.create_standings_snapshot("snapshot-1", sample_league_id, None, utc_now())

        temp_db.store_player_ranking(
            "snapshot-1",
            "alice",
            PlayerRanking(rank=1, points=6, wins=2, draws=0, losses=0, matches_played=2),
        )

        # Verify ranking exists
        cursor = temp_db.conn.execute(
            "SELECT * FROM player_rankings WHERE snapshot_id = ? AND player_id = ?",
            ("snapshot-1", "alice"),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["points"] == 6
        assert row["wins"] == 2

    def test_get_standings(self, temp_db, sample_league_id):
        """Test getting standings."""
        temp_db.create_league(sample_league_id, "ACTIVE", utc_now(), {})
        temp_db.register_player(
            "alice", sample_league_id, auth_token="token-1", registered_at=utc_now()
        )
        temp_db.register_player(
            "bob", sample_league_id, auth_token="token-2", registered_at=utc_now()
        )

        temp_db.create_standings_snapshot("snapshot-1", sample_league_id, None, utc_now())
        temp_db.store_player_ranking(
            "snapshot-1",
            "alice",
            PlayerRanking(rank=1, points=6, wins=2, draws=0, losses=0, matches_played=2),
        )
        temp_db.store_player_ranking(
            "snapshot-1",
            "bob",
            PlayerRanking(rank=2, points=3, wins=1, draws=0, losses=1, matches_played=2),
        )

        standings = temp_db.get_standings(sample_league_id)
        assert standings is not None
        assert len(standings["rankings"]) == 2
        assert standings["rankings"][0]["player_id"] == "alice"
        assert standings["rankings"][1]["player_id"] == "bob"


class TestTransactions:
    """Tests for database transactions."""

    def test_transaction_commit(self, temp_db, sample_league_id):
        """Test that transaction commits on success."""
        with temp_db.transaction():
            temp_db.conn.execute(
                "INSERT INTO leagues (league_id, status, created_at, config) VALUES (?, ?, ?, ?)",
                (sample_league_id, "REGISTRATION", utc_now(), "{}"),
            )

        # Verify data was committed
        league = temp_db.get_league(sample_league_id)
        assert league is not None

    def test_transaction_rollback_on_error(self, temp_db, sample_league_id):
        """Test that transaction rolls back on error."""
        from src.common.errors import DatabaseError

        try:
            with temp_db.transaction():
                temp_db.conn.execute(
                    "INSERT INTO leagues (league_id, status, created_at, config) VALUES (?, ?, ?, ?)",
                    (sample_league_id, "REGISTRATION", utc_now(), "{}"),
                )
                # Force an error
                raise ValueError("Test error")
        except DatabaseError:
            pass

        # Verify data was NOT committed
        league = temp_db.get_league(sample_league_id)
        assert league is None
