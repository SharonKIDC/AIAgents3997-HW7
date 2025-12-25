"""Tests for match executor.

This module tests match execution orchestration.
"""

from unittest.mock import Mock

import pytest

from src.common.errors import OperationalError
from src.common.transport import LeagueHTTPClient
from src.referee.match_executor import MatchExecutor


class TestMatchExecutor:
    """Tests for MatchExecutor class."""

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=LeagueHTTPClient)

    @pytest.fixture
    def player_urls(self):
        """Sample player URLs."""
        return {
            'alice': 'http://localhost:8001/mcp',
            'bob': 'http://localhost:8002/mcp'
        }

    @pytest.fixture
    def match_executor(self, mock_http_client, player_urls):
        """Create a match executor."""
        return MatchExecutor(
            referee_id='ref-1',
            http_client=mock_http_client,
            player_urls=player_urls,
            timeout_ms=30000
        )

    def test_executor_initialization(self, match_executor):
        """Test executor initialization."""
        assert match_executor.referee_id == 'ref-1'
        assert match_executor.timeout_ms == 30000

    def test_execute_match_tic_tac_toe(self, match_executor, mock_http_client):
        """Test executing a tic tac toe match."""
        # Mock move responses
        mock_http_client.send_request.side_effect = [
            # Invitations (no response needed)
            {},
            {},
            # Move responses
            {'payload': {'move_payload': {'row': 0, 'col': 0}}},  # alice
            {'payload': {'move_payload': {'row': 0, 'col': 1}}},  # bob
            {'payload': {'move_payload': {'row': 1, 'col': 0}}},  # alice
            {'payload': {'move_payload': {'row': 1, 'col': 1}}},  # bob
            {'payload': {'move_payload': {'row': 2, 'col': 0}}},  # alice wins
        ]

        mock_http_client.send_request_no_response = Mock()

        result = match_executor.execute_match(
            match_id='match-1',
            round_id='round-1',
            game_type='tic_tac_toe',
            players=['alice', 'bob'],
            league_id='league-1'
        )

        # Verify result structure
        assert result['match_id'] == 'match-1'
        assert result['game_type'] == 'tic_tac_toe'
        assert 'outcome' in result
        assert 'points' in result
        assert result['outcome']['alice'] == 'win'
        assert result['outcome']['bob'] == 'loss'
        assert result['points']['alice'] == 3
        assert result['points']['bob'] == 0

    def test_execute_match_draw(self, match_executor, mock_http_client):
        """Test executing a match that ends in a draw."""
        # Mock moves that result in a draw
        # Corrected sequence to actually produce a draw
        mock_http_client.send_request.side_effect = [
            {}, {},  # Invitations
            {'payload': {'move_payload': {'row': 0, 'col': 0}}},  # alice: X
            {'payload': {'move_payload': {'row': 0, 'col': 1}}},  # bob: O
            {'payload': {'move_payload': {'row': 0, 'col': 2}}},  # alice: X
            {'payload': {'move_payload': {'row': 1, 'col': 1}}},  # bob: O
            {'payload': {'move_payload': {'row': 1, 'col': 0}}},  # alice: X
            {'payload': {'move_payload': {'row': 1, 'col': 2}}},  # bob: O
            {'payload': {'move_payload': {'row': 2, 'col': 1}}},  # alice: X
            {'payload': {'move_payload': {'row': 2, 'col': 0}}},  # bob: O
            {'payload': {'move_payload': {'row': 2, 'col': 2}}},  # alice: X - draw
        ]

        mock_http_client.send_request_no_response = Mock()

        result = match_executor.execute_match(
            match_id='match-1',
            round_id='round-1',
            game_type='tic_tac_toe',
            players=['alice', 'bob'],
            league_id='league-1'
        )

        assert result['outcome']['alice'] == 'draw'
        assert result['outcome']['bob'] == 'draw'
        assert result['points']['alice'] == 1
        assert result['points']['bob'] == 1

    def test_execute_match_invalid_move_forfeits(self, match_executor, mock_http_client):
        """Test that invalid move results in forfeit."""
        # Mock invalid move response
        mock_http_client.send_request.side_effect = [
            {}, {},  # Invitations
            {'payload': {'move_payload': {'row': 5, 'col': 5}}},  # alice: invalid
        ]

        mock_http_client.send_request_no_response = Mock()

        result = match_executor.execute_match(
            match_id='match-1',
            round_id='round-1',
            game_type='tic_tac_toe',
            players=['alice', 'bob'],
            league_id='league-1'
        )

        # Alice forfeits, Bob wins
        assert result['outcome']['alice'] == 'loss'
        assert result['outcome']['bob'] == 'win'
        assert result['points']['bob'] == 3

    def test_execute_match_player_timeout_forfeits(self, match_executor, mock_http_client):
        """Test that player timeout results in forfeit."""
        # Mock timeout
        mock_http_client.send_request.side_effect = [
            {}, {},  # Invitations
            Exception('Timeout'),  # alice times out
        ]

        mock_http_client.send_request_no_response = Mock()

        result = match_executor.execute_match(
            match_id='match-1',
            round_id='round-1',
            game_type='tic_tac_toe',
            players=['alice', 'bob'],
            league_id='league-1'
        )

        # Alice forfeits, Bob wins
        assert result['outcome']['alice'] == 'loss'
        assert result['outcome']['bob'] == 'win'

    def test_execute_match_unsupported_game_type(self, match_executor):
        """Test that unsupported game type raises error."""
        with pytest.raises(OperationalError) as exc_info:
            match_executor.execute_match(
                match_id='match-1',
                round_id='round-1',
                game_type='chess',  # Not supported
                players=['alice', 'bob'],
                league_id='league-1'
            )

        assert 'Unsupported game type' in str(exc_info.value)

    def test_execute_match_sends_game_invitations(self, match_executor, mock_http_client):
        """Test that game invitations are sent to both players."""
        mock_http_client.send_request.side_effect = [
            {}, {},  # Invitations
            {'payload': {'move_payload': {'row': 0, 'col': 0}}},
            {'payload': {'move_payload': {'row': 0, 'col': 1}}},
            {'payload': {'move_payload': {'row': 1, 'col': 0}}},
            {'payload': {'move_payload': {'row': 1, 'col': 1}}},
            {'payload': {'move_payload': {'row': 2, 'col': 0}}},
        ]

        mock_http_client.send_request_no_response = Mock()

        match_executor.execute_match(
            match_id='match-1',
            round_id='round-1',
            game_type='tic_tac_toe',
            players=['alice', 'bob'],
            league_id='league-1'
        )

        # Verify invitations were sent
        assert mock_http_client.send_request.call_count >= 2

    def test_execute_match_sends_game_over_notifications(self, match_executor, mock_http_client):
        """Test that game over notifications are sent."""
        mock_http_client.send_request.side_effect = [
            {}, {},  # Invitations
            {'payload': {'move_payload': {'row': 0, 'col': 0}}},
            {'payload': {'move_payload': {'row': 0, 'col': 1}}},
            {'payload': {'move_payload': {'row': 1, 'col': 0}}},
            {'payload': {'move_payload': {'row': 1, 'col': 1}}},
            {'payload': {'move_payload': {'row': 2, 'col': 0}}},
        ]

        mock_http_client.send_request_no_response = Mock()

        match_executor.execute_match(
            match_id='match-1',
            round_id='round-1',
            game_type='tic_tac_toe',
            players=['alice', 'bob'],
            league_id='league-1'
        )

        # Verify game over messages were sent
        assert mock_http_client.send_request_no_response.call_count == 2

    def test_execute_match_includes_metadata(self, match_executor, mock_http_client):
        """Test that result includes game metadata."""
        mock_http_client.send_request.side_effect = [
            {}, {},  # Invitations
            {'payload': {'move_payload': {'row': 0, 'col': 0}}},
            {'payload': {'move_payload': {'row': 0, 'col': 1}}},
            {'payload': {'move_payload': {'row': 1, 'col': 0}}},
            {'payload': {'move_payload': {'row': 1, 'col': 1}}},
            {'payload': {'move_payload': {'row': 2, 'col': 0}}},
        ]

        mock_http_client.send_request_no_response = Mock()

        result = match_executor.execute_match(
            match_id='match-1',
            round_id='round-1',
            game_type='tic_tac_toe',
            players=['alice', 'bob'],
            league_id='league-1'
        )

        assert 'game_metadata' in result
        assert 'final_state' in result['game_metadata']
        assert 'total_moves' in result['game_metadata']
