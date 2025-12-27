"""Tests for Tic Tac Toe game logic.

This module tests the game engine for Tic Tac Toe.
"""

from src.referee.games.tic_tac_toe import GameOutcome, Mark, TicTacToeGame


def create_game(player_x="alice", player_o="bob"):
    """Helper function to create and initialize a game."""
    game = TicTacToeGame([player_x, player_o])
    game.initialize()
    return game


class TestTicTacToeGame:
    """Tests for TicTacToeGame class."""

    def test_game_initialization(self):
        """Test game initialization."""
        game = create_game()

        assert game.player_x == "alice"
        assert game.player_o == "bob"
        assert game.current_player == "alice"  # X goes first
        assert game.move_count == 0
        assert not game.is_terminal()

    def test_valid_move(self):
        """Test making a valid move."""
        game = create_game()

        assert game.is_valid_move(0, 0)
        assert game.make_move(0, 0)
        assert game.board[0][0] == Mark.X.value
        assert game.move_count == 1
        assert game.current_player == "bob"  # Switches to O

    def test_invalid_move_out_of_bounds(self):
        """Test that out of bounds moves are invalid."""
        game = create_game()

        assert not game.is_valid_move(-1, 0)
        assert not game.is_valid_move(0, 3)
        assert not game.is_valid_move(3, 3)
        assert not game.make_move(5, 5)

    def test_invalid_move_occupied_square(self):
        """Test that occupied squares cannot be played."""
        game = create_game()

        game.make_move(0, 0)
        assert not game.is_valid_move(0, 0)
        assert not game.make_move(0, 0)

    def test_horizontal_win(self):
        """Test detecting horizontal win."""
        game = create_game()

        # X X X
        # O O _
        # _ _ _
        game.make_move(0, 0)  # X
        game.make_move(1, 0)  # O
        game.make_move(0, 1)  # X
        game.make_move(1, 1)  # O
        game.make_move(0, 2)  # X wins

        assert game.check_winner() == Mark.X.value
        assert game.get_outcome() == GameOutcome.X_WINS
        assert game.is_terminal()

    def test_vertical_win(self):
        """Test detecting vertical win."""
        game = create_game()

        # X O _
        # X O _
        # X _ _
        game.make_move(0, 0)  # X
        game.make_move(0, 1)  # O
        game.make_move(1, 0)  # X
        game.make_move(1, 1)  # O
        game.make_move(2, 0)  # X wins

        assert game.check_winner() == Mark.X.value
        assert game.get_outcome() == GameOutcome.X_WINS

    def test_diagonal_win_top_left_to_bottom_right(self):
        """Test detecting diagonal win (top-left to bottom-right)."""
        game = create_game()

        # X O _
        # O X _
        # _ _ X
        game.make_move(0, 0)  # X
        game.make_move(0, 1)  # O
        game.make_move(1, 1)  # X
        game.make_move(1, 0)  # O
        game.make_move(2, 2)  # X wins

        assert game.check_winner() == Mark.X.value

    def test_diagonal_win_top_right_to_bottom_left(self):
        """Test detecting diagonal win (top-right to bottom-left)."""
        game = create_game()

        # O _ X
        # _ X O
        # X _ _
        game.make_move(0, 2)  # X
        game.make_move(0, 0)  # O
        game.make_move(1, 1)  # X
        game.make_move(1, 2)  # O
        game.make_move(2, 0)  # X wins

        assert game.check_winner() == Mark.X.value

    def test_draw_game(self):
        """Test detecting a draw."""
        game = create_game()

        # X O X
        # X O O
        # O X X
        # Correct alternating sequence: X, O, X, O, X, O, X, O, X
        moves = [
            (0, 0),
            (0, 1),
            (0, 2),  # X, O, X - Row 1
            (1, 1),
            (1, 0),
            (1, 2),  # O, X, O - Row 2
            (2, 1),
            (2, 0),
            (2, 2),  # X, O, X - Row 3
        ]

        for row, col in moves:
            game.make_move(row, col)

        assert game.check_winner() is None
        assert game.is_board_full()
        assert game.get_outcome() == GameOutcome.DRAW
        assert game.is_terminal()

    def test_game_in_progress(self):
        """Test game in progress state."""
        game = create_game()

        game.make_move(0, 0)
        game.make_move(1, 1)

        assert not game.is_terminal()
        assert game.get_outcome() == GameOutcome.IN_PROGRESS

    def test_get_current_mark(self):
        """Test getting current player's mark."""
        game = create_game()

        assert game.get_current_mark() == Mark.X.value
        game.make_move(0, 0)
        assert game.get_current_mark() == Mark.O.value

    def test_get_state_summary(self):
        """Test getting game state summary."""
        game = create_game()
        game.make_move(0, 0)

        state = game.get_state_summary()

        assert "board" in state
        assert "current_player" in state
        assert "move_count" in state
        assert "outcome" in state
        assert state["move_count"] == 1
        assert state["current_player"] == "bob"

    def test_get_step_context(self):
        """Test getting step context for move request."""
        game = create_game()

        context = game.get_step_context()

        assert "board" in context
        assert "your_mark" in context
        assert "move_number" in context
        assert context["your_mark"] == Mark.X.value
        assert context["move_number"] == 1

    def test_get_available_moves(self):
        """Test getting available moves."""
        game = create_game()

        # Initially all 9 squares available
        moves = game.get_available_moves()
        assert len(moves) == 9

        # After one move, 8 available
        game.make_move(0, 0)
        moves = game.get_available_moves()
        assert len(moves) == 8
        assert (0, 0) not in moves

    def test_get_result_x_wins(self):
        """Test getting result when X wins."""
        game = create_game()

        # X wins
        game.make_move(0, 0)  # X
        game.make_move(1, 0)  # O
        game.make_move(0, 1)  # X
        game.make_move(1, 1)  # O
        game.make_move(0, 2)  # X wins

        result = game.get_result()

        assert result["outcome"]["alice"] == "win"
        assert result["outcome"]["bob"] == "loss"
        assert result["points"]["alice"] == 3
        assert result["points"]["bob"] == 0
        assert result["winner"] == "alice"

    def test_get_result_o_wins(self):
        """Test getting result when O wins."""
        game = create_game()

        # O wins
        game.make_move(0, 0)  # X
        game.make_move(1, 0)  # O
        game.make_move(0, 1)  # X
        game.make_move(1, 1)  # O
        game.make_move(2, 2)  # X
        game.make_move(1, 2)  # O wins

        result = game.get_result()

        assert result["outcome"]["alice"] == "loss"
        assert result["outcome"]["bob"] == "win"
        assert result["points"]["alice"] == 0
        assert result["points"]["bob"] == 3
        assert result["winner"] == "bob"

    def test_get_result_draw(self):
        """Test getting result when game is a draw."""
        game = create_game()

        # Create a draw - correct alternating sequence
        moves = [
            (0, 0),
            (0, 1),
            (0, 2),  # X, O, X
            (1, 1),
            (1, 0),
            (1, 2),  # O, X, O
            (2, 1),
            (2, 0),
            (2, 2),  # X, O, X
        ]
        for row, col in moves:
            game.make_move(row, col)

        result = game.get_result()

        assert result["outcome"]["alice"] == "draw"
        assert result["outcome"]["bob"] == "draw"
        assert result["points"]["alice"] == 1
        assert result["points"]["bob"] == 1
        assert result["winner"] is None

    def test_board_deep_copy_in_state(self):
        """Test that state summary returns deep copy of board."""
        game = create_game()
        game.make_move(0, 0)

        state = game.get_state_summary()
        board_copy = state["board"]

        # Modify the copy
        board_copy[0][0] = "MODIFIED"

        # Original should be unchanged
        assert game.board[0][0] == Mark.X.value

    def test_full_game_playthrough(self):
        """Test a complete game from start to finish."""
        game = create_game()

        # Play a complete game
        assert not game.is_terminal()

        game.make_move(1, 1)  # X center
        assert not game.is_terminal()

        game.make_move(0, 0)  # O corner
        game.make_move(0, 1)  # X
        game.make_move(2, 1)  # O
        game.make_move(2, 2)  # X
        game.make_move(0, 2)  # O
        game.make_move(1, 0)  # X
        game.make_move(1, 2)  # O
        game.make_move(2, 0)  # X

        # Game should be over (draw)
        assert game.is_terminal()
        assert game.get_outcome() == GameOutcome.DRAW
