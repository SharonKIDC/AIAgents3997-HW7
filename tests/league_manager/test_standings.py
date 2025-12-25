"""Tests for standings computation.

This module tests standings calculation and tie-breaking rules.
"""

import pytest

from src.common.protocol import utc_now
from src.league_manager.standings import StandingsEngine


class TestStandingsEngine:
    """Tests for StandingsEngine class."""

    @pytest.fixture
    def standings_engine(self, temp_db):
        """Create a standings engine instance."""
        return StandingsEngine(temp_db)

    @pytest.fixture
    def league_with_results(self, temp_db, sample_league_id):
        """Create a league with players and match results."""
        # Create league
        temp_db.create_league(sample_league_id, 'ACTIVE', utc_now(), {})

        # Register players
        players = ['alice', 'bob', 'charlie', 'dave']
        for player_id in players:
            temp_db.register_player(player_id, sample_league_id, f'token-{player_id}', utc_now())

        # Create round and matches
        temp_db.create_round('round-1', sample_league_id, 1)
        temp_db.create_match('match-1', 'round-1', 'tic_tac_toe', ['alice', 'bob'])
        temp_db.create_match('match-2', 'round-1', 'tic_tac_toe', ['charlie', 'dave'])

        # Add results
        # Alice beats Bob
        temp_db.store_result(
            'result-1', 'match-1',
            {'alice': 'win', 'bob': 'loss'},
            {'alice': 3, 'bob': 0},
            None, utc_now()
        )

        # Charlie and Dave draw
        temp_db.store_result(
            'result-2', 'match-2',
            {'charlie': 'draw', 'dave': 'draw'},
            {'charlie': 1, 'dave': 1},
            None, utc_now()
        )

        return sample_league_id

    def test_compute_standings_basic(self, standings_engine, league_with_results):
        """Test basic standings computation."""
        standings = standings_engine.compute_standings(league_with_results)

        assert standings is not None
        assert 'standings' in standings
        assert len(standings['standings']) == 4

    def test_standings_sorting_by_points(self, standings_engine, league_with_results):
        """Test that standings are sorted by points."""
        standings = standings_engine.compute_standings(league_with_results)

        rankings = standings['standings']

        # Alice should be first (3 points from win)
        assert rankings[0]['player_id'] == 'alice'
        assert rankings[0]['points'] == 3
        assert rankings[0]['rank'] == 1

        # Charlie and Dave should be tied (1 point each from draw)
        charlie_rank = next(r['rank'] for r in rankings if r['player_id'] == 'charlie')
        dave_rank = next(r['rank'] for r in rankings if r['player_id'] == 'dave')
        assert charlie_rank in [2, 3]
        assert dave_rank in [2, 3]

        # Bob should be last (0 points from loss)
        assert rankings[-1]['player_id'] == 'bob'
        assert rankings[-1]['points'] == 0

    def test_standings_statistics(self, standings_engine, league_with_results):
        """Test that standings include correct statistics."""
        standings = standings_engine.compute_standings(league_with_results)

        alice = next(r for r in standings['standings'] if r['player_id'] == 'alice')
        assert alice['wins'] == 1
        assert alice['draws'] == 0
        assert alice['losses'] == 0
        assert alice['matches_played'] == 1

        bob = next(r for r in standings['standings'] if r['player_id'] == 'bob')
        assert bob['wins'] == 0
        assert bob['draws'] == 0
        assert bob['losses'] == 1
        assert bob['matches_played'] == 1

        charlie = next(r for r in standings['standings'] if r['player_id'] == 'charlie')
        assert charlie['wins'] == 0
        assert charlie['draws'] == 1
        assert charlie['losses'] == 0
        assert charlie['matches_played'] == 1

    def test_standings_tie_breaking_by_wins(self, temp_db, standings_engine, sample_league_id):
        """Test tie-breaking by wins when points are equal."""
        # Create league and players
        temp_db.create_league(sample_league_id, 'ACTIVE', utc_now(), {})
        for player_id in ['alice', 'bob', 'charlie']:
            temp_db.register_player(player_id, sample_league_id, f'token-{player_id}', utc_now())

        # Create matches
        temp_db.create_round('round-1', sample_league_id, 1)
        temp_db.create_match('match-1', 'round-1', 'tic_tac_toe', ['alice', 'charlie'])
        temp_db.create_match('match-2', 'round-1', 'tic_tac_toe', ['bob', 'charlie'])

        # Alice: 1 win (3 points)
        temp_db.store_result(
            'result-1', 'match-1',
            {'alice': 'win', 'charlie': 'loss'},
            {'alice': 3, 'charlie': 0},
            None, utc_now()
        )

        # Bob: 3 draws (3 points, but 0 wins)
        temp_db.store_result(
            'result-2', 'match-2',
            {'bob': 'draw', 'charlie': 'draw'},
            {'bob': 1, 'charlie': 1},
            None, utc_now()
        )

        # Add more draws for Bob to get 3 points
        temp_db.create_match('match-3', 'round-1', 'tic_tac_toe', ['bob', 'alice'])
        temp_db.create_match('match-4', 'round-1', 'tic_tac_toe', ['bob', 'alice'])
        temp_db.store_result(
            'result-3', 'match-3',
            {'bob': 'draw', 'alice': 'draw'},
            {'bob': 1, 'alice': 1},
            None, utc_now()
        )
        temp_db.store_result(
            'result-4', 'match-4',
            {'bob': 'draw', 'alice': 'draw'},
            {'bob': 1, 'alice': 1},
            None, utc_now()
        )

        standings = standings_engine.compute_standings(sample_league_id)

        # Alice should rank higher than Bob (both have points, but Alice has more wins)
        alice_rank = next(r['rank'] for r in standings['standings'] if r['player_id'] == 'alice')
        bob_rank = next(r['rank'] for r in standings['standings'] if r['player_id'] == 'bob')
        assert alice_rank < bob_rank

    def test_standings_tie_breaking_by_player_id(self, temp_db, standings_engine, sample_league_id):
        """Test tie-breaking by player ID when all else is equal."""
        # Create league and players with alphabetically different IDs
        temp_db.create_league(sample_league_id, 'ACTIVE', utc_now(), {})
        for player_id in ['zebra', 'alpha', 'beta']:
            temp_db.register_player(player_id, sample_league_id, f'token-{player_id}', utc_now())

        # No matches played - all have 0 points
        standings = standings_engine.compute_standings(sample_league_id)

        # Should be sorted by player_id alphabetically
        player_ids = [r['player_id'] for r in standings['standings']]
        assert player_ids == ['alpha', 'beta', 'zebra']

    def test_publish_standings(self, standings_engine, league_with_results, temp_db):
        """Test publishing standings to database."""
        snapshot_id = standings_engine.publish_standings(league_with_results)

        assert snapshot_id is not None

        # Verify snapshot exists in database
        cursor = temp_db.conn.execute(
            'SELECT * FROM standings_snapshots WHERE snapshot_id = ?',
            (snapshot_id,)
        )
        assert cursor.fetchone() is not None

        # Verify rankings exist
        cursor = temp_db.conn.execute(
            'SELECT * FROM player_rankings WHERE snapshot_id = ?',
            (snapshot_id,)
        )
        rankings = cursor.fetchall()
        assert len(rankings) == 4

    def test_get_standings(self, standings_engine, league_with_results):
        """Test retrieving published standings."""
        # Publish first
        standings_engine.publish_standings(league_with_results)

        # Retrieve
        standings = standings_engine.get_standings(league_with_results)

        assert standings is not None
        assert 'standings' in standings
        assert len(standings['standings']) == 4

    def test_standings_with_no_results(self, temp_db, standings_engine, sample_league_id):
        """Test computing standings with no match results."""
        # Create league and players but no results
        temp_db.create_league(sample_league_id, 'ACTIVE', utc_now(), {})
        for player_id in ['alice', 'bob']:
            temp_db.register_player(player_id, sample_league_id, f'token-{player_id}', utc_now())

        standings = standings_engine.compute_standings(sample_league_id)

        assert len(standings['standings']) == 2
        for ranking in standings['standings']:
            assert ranking['points'] == 0
            assert ranking['wins'] == 0
            assert ranking['matches_played'] == 0

    def test_standings_include_all_players(self, temp_db, standings_engine, sample_league_id):
        """Test that standings include players with no matches."""
        # Create league
        temp_db.create_league(sample_league_id, 'ACTIVE', utc_now(), {})

        # Register 4 players
        for player_id in ['alice', 'bob', 'charlie', 'dave']:
            temp_db.register_player(player_id, sample_league_id, f'token-{player_id}', utc_now())

        # Only alice and bob play a match
        temp_db.create_round('round-1', sample_league_id, 1)
        temp_db.create_match('match-1', 'round-1', 'tic_tac_toe', ['alice', 'bob'])
        temp_db.store_result(
            'result-1', 'match-1',
            {'alice': 'win', 'bob': 'loss'},
            {'alice': 3, 'bob': 0},
            None, utc_now()
        )

        standings = standings_engine.compute_standings(sample_league_id)

        # All 4 players should be in standings
        assert len(standings['standings']) == 4
        player_ids = {r['player_id'] for r in standings['standings']}
        assert player_ids == {'alice', 'bob', 'charlie', 'dave'}

    def test_standings_multiple_rounds(self, temp_db, standings_engine, sample_league_id):
        """Test standings accumulation across multiple rounds."""
        # Create league and players
        temp_db.create_league(sample_league_id, 'ACTIVE', utc_now(), {})
        for player_id in ['alice', 'bob']:
            temp_db.register_player(player_id, sample_league_id, f'token-{player_id}', utc_now())

        # Round 1: Alice wins
        temp_db.create_round('round-1', sample_league_id, 1)
        temp_db.create_match('match-1', 'round-1', 'tic_tac_toe', ['alice', 'bob'])
        temp_db.store_result(
            'result-1', 'match-1',
            {'alice': 'win', 'bob': 'loss'},
            {'alice': 3, 'bob': 0},
            None, utc_now()
        )

        # Round 2: Alice wins again
        temp_db.create_round('round-2', sample_league_id, 2)
        temp_db.create_match('match-2', 'round-2', 'tic_tac_toe', ['alice', 'bob'])
        temp_db.store_result(
            'result-2', 'match-2',
            {'alice': 'win', 'bob': 'loss'},
            {'alice': 3, 'bob': 0},
            None, utc_now()
        )

        standings = standings_engine.compute_standings(sample_league_id)

        alice = next(r for r in standings['standings'] if r['player_id'] == 'alice')
        assert alice['points'] == 6  # 2 wins
        assert alice['wins'] == 2
        assert alice['matches_played'] == 2

        bob = next(r for r in standings['standings'] if r['player_id'] == 'bob')
        assert bob['points'] == 0
        assert bob['losses'] == 2
        assert bob['matches_played'] == 2
