"""Tests for player strategies.

This module tests player move computation strategies.
"""

import pytest

from src.player.strategies.tic_tac_toe_random import TicTacToeRandomStrategy
from src.player.strategies.tic_tac_toe_smart import TicTacToeSmartStrategy

# Backward compatibility aliases
TicTacToeStrategy = TicTacToeSmartStrategy
RandomStrategy = TicTacToeRandomStrategy


class TestTicTacToeStrategy:
    """Tests for TicTacToeStrategy class."""

    def test_strategy_initialization(self):
        """Test creating a strategy."""
        strategy = TicTacToeStrategy('alice')
        assert strategy.player_id == 'alice'

    def test_compute_move_returns_valid_format(self):
        """Test that computed move has correct format."""
        strategy = TicTacToeStrategy('alice')

        context = {
            'board': [['', '', ''], ['', '', ''], ['', '', '']],
            'your_mark': 'X',
            'move_number': 1
        }

        move = strategy.compute_move(context)

        assert 'row' in move
        assert 'col' in move
        assert isinstance(move['row'], int)
        assert isinstance(move['col'], int)

    def test_compute_move_on_empty_board(self):
        """Test computing move on empty board."""
        strategy = TicTacToeStrategy('alice')

        context = {
            'board': [['', '', ''], ['', '', ''], ['', '', '']],
            'your_mark': 'X',
            'move_number': 1
        }

        move = strategy.compute_move(context)

        # Should return a valid position
        assert 0 <= move['row'] < 3
        assert 0 <= move['col'] < 3

    def test_compute_move_finds_winning_move(self):
        """Test that strategy finds winning move."""
        strategy = TicTacToeStrategy('alice')

        # X X _
        # O O _
        # _ _ _
        context = {
            'board': [
                ['X', 'X', ''],
                ['O', 'O', ''],
                ['', '', '']
            ],
            'your_mark': 'X',
            'move_number': 5
        }

        move = strategy.compute_move(context)

        # Should play at (0, 2) to win
        assert move['row'] == 0
        assert move['col'] == 2

    def test_compute_move_blocks_opponent(self):
        """Test that strategy blocks opponent's winning move."""
        strategy = TicTacToeStrategy('alice')

        # O O _
        # X _ _
        # _ _ _
        context = {
            'board': [
                ['O', 'O', ''],
                ['X', '', ''],
                ['', '', '']
            ],
            'your_mark': 'X',
            'move_number': 4
        }

        move = strategy.compute_move(context)

        # Should block at (0, 2)
        assert move['row'] == 0
        assert move['col'] == 2

    def test_compute_move_prioritizes_win_over_block(self):
        """Test that strategy prioritizes winning over blocking."""
        strategy = TicTacToeStrategy('alice')

        # X X _
        # O O _
        # _ _ _
        context = {
            'board': [
                ['X', 'X', ''],
                ['O', 'O', ''],
                ['', '', '']
            ],
            'your_mark': 'X',
            'move_number': 5
        }

        move = strategy.compute_move(context)

        # Should take win at (0, 2) rather than block at (1, 2)
        assert move['row'] == 0
        assert move['col'] == 2

    def test_compute_move_on_nearly_full_board(self):
        """Test computing move on nearly full board."""
        strategy = TicTacToeStrategy('alice')

        # X O X
        # X O O
        # O X _
        context = {
            'board': [
                ['X', 'O', 'X'],
                ['X', 'O', 'O'],
                ['O', 'X', '']
            ],
            'your_mark': 'X',
            'move_number': 9
        }

        move = strategy.compute_move(context)

        # Only one move left
        assert move['row'] == 2
        assert move['col'] == 2

    def test_compute_move_no_available_moves_raises_error(self):
        """Test that error is raised when no moves available."""
        strategy = TicTacToeStrategy('alice')

        # Full board
        context = {
            'board': [
                ['X', 'O', 'X'],
                ['O', 'X', 'O'],
                ['O', 'X', 'O']
            ],
            'your_mark': 'X',
            'move_number': 10
        }

        with pytest.raises(ValueError):
            strategy.compute_move(context)

    def test_would_win_horizontal(self):
        """Test detecting horizontal win."""
        strategy = TicTacToeStrategy('alice')

        board = [
            ['X', 'X', ''],
            ['', '', ''],
            ['', '', '']
        ]

        assert strategy._would_win(board, 0, 2, 'X')

    def test_would_win_vertical(self):
        """Test detecting vertical win."""
        strategy = TicTacToeStrategy('alice')

        board = [
            ['X', '', ''],
            ['X', '', ''],
            ['', '', '']
        ]

        assert strategy._would_win(board, 2, 0, 'X')

    def test_would_win_diagonal(self):
        """Test detecting diagonal win."""
        strategy = TicTacToeStrategy('alice')

        board = [
            ['X', '', ''],
            ['', 'X', ''],
            ['', '', '']
        ]

        assert strategy._would_win(board, 2, 2, 'X')

    def test_would_win_anti_diagonal(self):
        """Test detecting anti-diagonal win."""
        strategy = TicTacToeStrategy('alice')

        board = [
            ['', '', 'X'],
            ['', 'X', ''],
            ['', '', '']
        ]

        assert strategy._would_win(board, 2, 0, 'X')

    def test_different_players_get_different_marks(self):
        """Test that strategy works for both X and O."""
        strategy_x = TicTacToeStrategy('alice')
        strategy_o = TicTacToeStrategy('bob')

        context_x = {
            'board': [['', '', ''], ['', '', ''], ['', '', '']],
            'your_mark': 'X',
            'move_number': 1
        }

        context_o = {
            'board': [['X', '', ''], ['', '', ''], ['', '', '']],
            'your_mark': 'O',
            'move_number': 2
        }

        move_x = strategy_x.compute_move(context_x)
        move_o = strategy_o.compute_move(context_o)

        # Both should return valid moves
        assert 0 <= move_x['row'] < 3
        assert 0 <= move_o['row'] < 3


class TestRandomStrategy:
    """Tests for RandomStrategy class."""

    def test_random_strategy_initialization(self):
        """Test creating a random strategy."""
        strategy = RandomStrategy('alice')
        assert strategy.player_id == 'alice'

    def test_random_strategy_returns_valid_move(self):
        """Test that random strategy returns valid move."""
        strategy = RandomStrategy('alice')

        context = {
            'board': [['', '', ''], ['', '', ''], ['', '', '']],
            'your_mark': 'X',
            'move_number': 1
        }

        move = strategy.compute_move(context)

        assert 'row' in move
        assert 'col' in move
        assert 0 <= move['row'] < 3
        assert 0 <= move['col'] < 3

    def test_random_strategy_only_picks_empty_squares(self):
        """Test that random strategy only picks empty squares."""
        strategy = RandomStrategy('alice')

        # Board with only one empty square
        context = {
            'board': [
                ['X', 'O', 'X'],
                ['O', 'X', 'O'],
                ['O', 'X', '']
            ],
            'your_mark': 'X',
            'move_number': 9
        }

        move = strategy.compute_move(context)

        # Should pick the only empty square
        assert move['row'] == 2
        assert move['col'] == 2

    def test_random_strategy_no_available_moves(self):
        """Test that random strategy raises error when no moves available."""
        strategy = RandomStrategy('alice')

        context = {
            'board': [
                ['X', 'O', 'X'],
                ['O', 'X', 'O'],
                ['O', 'X', 'O']
            ],
            'your_mark': 'X',
            'move_number': 10
        }

        with pytest.raises(ValueError):
            strategy.compute_move(context)

    def test_random_strategy_produces_variety(self):
        """Test that random strategy produces different moves."""
        strategy = RandomStrategy('alice')

        context = {
            'board': [['', '', ''], ['', '', ''], ['', '', '']],
            'your_mark': 'X',
            'move_number': 1
        }

        # Generate multiple moves
        moves = [strategy.compute_move(context) for _ in range(20)]

        # Should have some variety (not all the same)
        unique_moves = set((m['row'], m['col']) for m in moves)
        assert len(unique_moves) > 1  # Should have at least 2 different moves
