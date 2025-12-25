"""Tests for round-robin scheduler.

This module tests deterministic round-robin scheduling.
"""

import pytest

from src.common.protocol import utc_now
from src.league_manager.scheduler import RoundRobinScheduler


class TestRoundRobinScheduler:
    """Tests for RoundRobinScheduler class."""

    @pytest.fixture
    def scheduler(self, temp_db):
        """Create a scheduler instance."""
        return RoundRobinScheduler(temp_db)

    @pytest.fixture
    def league_with_players(self, temp_db, sample_league_id, sample_player_ids):
        """Create a league with registered players."""
        temp_db.create_league(sample_league_id, 'SCHEDULING', utc_now(), {})
        for player_id in sample_player_ids:
            temp_db.register_player(player_id, sample_league_id, f'token-{player_id}', utc_now())
        return sample_league_id

    def test_schedule_generation_two_players(self, scheduler, league_with_players, temp_db):
        """Test scheduling with minimum players (2)."""
        players = ['alice', 'bob']
        schedule = scheduler.generate_schedule(
            league_with_players,
            players,
            'tic_tac_toe'
        )

        # Should have 1 match (1 combination of 2)
        assert schedule['total_matches'] == 1
        assert schedule['total_rounds'] == 1
        assert len(schedule['rounds']) == 1
        assert len(schedule['rounds'][0]['matches']) == 1

    def test_schedule_generation_four_players(self, scheduler, league_with_players):
        """Test scheduling with 4 players."""
        players = ['alice', 'bob', 'charlie', 'dave']
        schedule = scheduler.generate_schedule(
            league_with_players,
            players,
            'tic_tac_toe'
        )

        # 4 players = C(4,2) = 6 matches
        assert schedule['total_matches'] == 6
        assert schedule['total_rounds'] >= 3  # At least 3 rounds needed

    def test_schedule_determinism(self, scheduler, league_with_players):
        """Test that same players produce same schedule."""
        players = ['alice', 'bob', 'charlie', 'dave']

        schedule1 = scheduler.generate_schedule(
            league_with_players,
            players,
            'tic_tac_toe'
        )

        # Generate again with same players
        schedule2 = scheduler.generate_schedule(
            'league-2',  # Different league
            players,
            'tic_tac_toe'
        )

        # Should have same structure (same number of rounds and matches)
        assert schedule1['total_matches'] == schedule2['total_matches']
        assert schedule1['total_rounds'] == schedule2['total_rounds']

    def test_schedule_all_pairs_played(self, scheduler, league_with_players):
        """Test that every pair of players plays exactly once."""
        players = ['alice', 'bob', 'charlie', 'dave']
        schedule = scheduler.generate_schedule(
            league_with_players,
            players,
            'tic_tac_toe'
        )

        # Collect all pairs
        all_pairs = set()
        for round_info in schedule['rounds']:
            for match in round_info['matches']:
                pair = tuple(sorted(match['players']))
                assert pair not in all_pairs, f"Duplicate match: {pair}"
                all_pairs.add(pair)

        # Verify all pairs are present
        expected_pairs = {
            ('alice', 'bob'),
            ('alice', 'charlie'),
            ('alice', 'dave'),
            ('bob', 'charlie'),
            ('bob', 'dave'),
            ('charlie', 'dave')
        }
        assert all_pairs == expected_pairs

    def test_schedule_no_player_twice_in_round(self, scheduler, league_with_players):
        """Test that no player appears twice in the same round."""
        players = ['alice', 'bob', 'charlie', 'dave']
        schedule = scheduler.generate_schedule(
            league_with_players,
            players,
            'tic_tac_toe'
        )

        for round_info in schedule['rounds']:
            players_in_round = set()
            for match in round_info['matches']:
                for player in match['players']:
                    assert player not in players_in_round, \
                        f"Player {player} appears twice in round {round_info['round_number']}"
                    players_in_round.add(player)

    def test_schedule_empty_players(self, scheduler, league_with_players):
        """Test scheduling with no players."""
        schedule = scheduler.generate_schedule(
            league_with_players,
            [],
            'tic_tac_toe'
        )

        assert schedule['total_matches'] == 0
        assert schedule['total_rounds'] == 0

    def test_schedule_single_player(self, scheduler, league_with_players):
        """Test scheduling with single player."""
        schedule = scheduler.generate_schedule(
            league_with_players,
            ['alice'],
            'tic_tac_toe'
        )

        assert schedule['total_matches'] == 0
        assert schedule['total_rounds'] == 0

    def test_schedule_stored_in_database(self, scheduler, league_with_players, temp_db):
        """Test that schedule is properly stored in database."""
        players = ['alice', 'bob', 'charlie']
        schedule = scheduler.generate_schedule(
            league_with_players,
            players,
            'tic_tac_toe'
        )

        # Verify rounds are in database
        for round_info in schedule['rounds']:
            cursor = temp_db.conn.execute(
                'SELECT * FROM rounds WHERE round_id = ?',
                (round_info['round_id'],)
            )
            assert cursor.fetchone() is not None

            # Verify matches are in database
            for match in round_info['matches']:
                match_data = temp_db.get_match(match['match_id'])
                assert match_data is not None
                assert match_data['game_type'] == 'tic_tac_toe'
                assert set(match_data['players']) == set(match['players'])

    def test_schedule_large_group(self, scheduler, league_with_players):
        """Test scheduling with larger group of players."""
        players = [f'player-{i}' for i in range(10)]
        schedule = scheduler.generate_schedule(
            league_with_players,
            players,
            'tic_tac_toe'
        )

        # 10 players = C(10,2) = 45 matches
        assert schedule['total_matches'] == 45

        # Verify all pairs
        all_pairs = set()
        for round_info in schedule['rounds']:
            for match in round_info['matches']:
                pair = tuple(sorted(match['players']))
                all_pairs.add(pair)

        assert len(all_pairs) == 45

    def test_schedule_round_numbers_sequential(self, scheduler, league_with_players):
        """Test that round numbers are sequential starting from 1."""
        players = ['alice', 'bob', 'charlie', 'dave']
        schedule = scheduler.generate_schedule(
            league_with_players,
            players,
            'tic_tac_toe'
        )

        round_numbers = [r['round_number'] for r in schedule['rounds']]
        assert round_numbers == list(range(1, len(round_numbers) + 1))

    def test_schedule_player_order_independence(self, scheduler, league_with_players):
        """Test that player order doesn't affect schedule structure."""
        players1 = ['alice', 'bob', 'charlie', 'dave']
        players2 = ['dave', 'alice', 'charlie', 'bob']

        schedule1 = scheduler.generate_schedule(
            league_with_players,
            players1,
            'tic_tac_toe'
        )

        schedule2 = scheduler.generate_schedule(
            'league-2',
            players2,
            'tic_tac_toe'
        )

        # Should have same number of matches (sorted internally)
        assert schedule1['total_matches'] == schedule2['total_matches']
        assert schedule1['total_rounds'] == schedule2['total_rounds']
