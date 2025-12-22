"""Tic Tac Toe game implementation for the Agent League System.

This module implements game-specific logic for Tic Tac Toe,
implementing the GameInterface for pluggability.
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import copy

from ...common.game_interface import GameInterface


class Mark(str, Enum):
    """Board marks."""
    X = "X"
    O = "O"
    EMPTY = ""


class GameOutcome(str, Enum):
    """Game outcomes."""
    X_WINS = "X_WINS"
    O_WINS = "O_WINS"
    DRAW = "DRAW"
    IN_PROGRESS = "IN_PROGRESS"


class TicTacToeGame(GameInterface):
    """Tic Tac Toe game engine implementing GameInterface."""

    def __init__(self, players: list):
        """Initialize a new game.

        Args:
            players: List of player IDs (must have exactly 2 players)
        """
        if len(players) != 2:
            raise ValueError("Tic Tac Toe requires exactly 2 players")

        super().__init__(players)
        self.player_x = players[0]
        self.player_o = players[1]
        self.board = [[Mark.EMPTY.value for _ in range(3)] for _ in range(3)]
        self.current_player = None
        self.move_count = 0

    def initialize(self) -> None:
        """Initialize the game state."""
        self.current_player = self.player_x
        self.board = [[Mark.EMPTY.value for _ in range(3)] for _ in range(3)]
        self.move_count = 0

    def get_current_player(self) -> str:
        """Get the player who should make the next move.

        Returns:
            Player ID of the current player
        """
        return self.current_player

    def get_game_type(self) -> str:
        """Get the game type identifier.

        Returns:
            Game type string
        """
        return 'tic_tac_toe'

    def get_current_mark(self) -> str:
        """Get mark for current player."""
        return Mark.X.value if self.current_player == self.player_x else Mark.O.value

    def validate_move(self, move_payload: Dict[str, Any]) -> bool:
        """Validate whether a move is legal.

        Args:
            move_payload: Move data from player

        Returns:
            True if move is valid, False otherwise
        """
        row = move_payload.get('row')
        col = move_payload.get('col')

        if row is None or col is None:
            return False

        if not isinstance(row, int) or not isinstance(col, int):
            return False

        if not (0 <= row < 3 and 0 <= col < 3):
            return False

        return self.board[row][col] == Mark.EMPTY.value

    def apply_move(self, move_payload: Dict[str, Any]) -> bool:
        """Apply a validated move to the game state.

        Args:
            move_payload: Move data from player

        Returns:
            True if move was successfully applied

        Raises:
            ValueError: If move is invalid
        """
        if not self.validate_move(move_payload):
            raise ValueError(f"Invalid move: {move_payload}")

        row = move_payload['row']
        col = move_payload['col']

        mark = self.get_current_mark()
        self.board[row][col] = mark
        self.move_count += 1

        # Switch player
        self.current_player = (
            self.player_o if self.current_player == self.player_x else self.player_x
        )

        return True

    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid (legacy method for backward compatibility).

        Args:
            row: Row index (0-2)
            col: Column index (0-2)

        Returns:
            True if move is valid
        """
        return self.validate_move({'row': row, 'col': col})

    def make_move(self, row: int, col: int) -> bool:
        """Make a move on the board (legacy method for backward compatibility).

        Args:
            row: Row index (0-2)
            col: Column index (0-2)

        Returns:
            True if move was successful
        """
        try:
            return self.apply_move({'row': row, 'col': col})
        except ValueError:
            return False

    def check_winner(self) -> Optional[str]:
        """Check if there is a winner.

        Returns:
            Mark of winner (X or O) or None
        """
        # Check rows
        for row in self.board:
            if row[0] != Mark.EMPTY.value and row[0] == row[1] == row[2]:
                return row[0]

        # Check columns
        for col in range(3):
            if (self.board[0][col] != Mark.EMPTY.value and
                self.board[0][col] == self.board[1][col] == self.board[2][col]):
                return self.board[0][col]

        # Check diagonals
        if (self.board[0][0] != Mark.EMPTY.value and
            self.board[0][0] == self.board[1][1] == self.board[2][2]):
            return self.board[0][0]

        if (self.board[0][2] != Mark.EMPTY.value and
            self.board[0][2] == self.board[1][1] == self.board[2][0]):
            return self.board[0][2]

        return None

    def is_board_full(self) -> bool:
        """Check if board is full."""
        return self.move_count >= 9

    def get_outcome(self) -> GameOutcome:
        """Get current game outcome.

        Returns:
            Game outcome
        """
        winner = self.check_winner()
        if winner == Mark.X.value:
            return GameOutcome.X_WINS
        elif winner == Mark.O.value:
            return GameOutcome.O_WINS
        elif self.is_board_full():
            return GameOutcome.DRAW
        else:
            return GameOutcome.IN_PROGRESS

    def is_terminal(self) -> bool:
        """Check if game is in terminal state.

        Returns:
            True if game is over
        """
        return self.get_outcome() != GameOutcome.IN_PROGRESS

    def get_state_summary(self) -> Dict[str, Any]:
        """Get current game state summary.

        Returns:
            Dictionary with game state
        """
        return {
            'board': copy.deepcopy(self.board),
            'current_player': self.current_player,
            'move_count': self.move_count,
            'outcome': self.get_outcome().value
        }

    def get_step_context(self) -> Dict[str, Any]:
        """Get context for next move request.

        Returns:
            Step context for player
        """
        return {
            'board': copy.deepcopy(self.board),
            'your_mark': self.get_current_mark(),
            'move_number': self.move_count + 1
        }

    def get_available_moves(self) -> List[Tuple[int, int]]:
        """Get list of available moves.

        Returns:
            List of (row, col) tuples
        """
        moves = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == Mark.EMPTY.value:
                    moves.append((row, col))
        return moves

    def get_result(self) -> Dict[str, Any]:
        """Get final game result.

        Returns:
            Result dictionary with outcome and points
        """
        outcome = self.get_outcome()

        if outcome == GameOutcome.X_WINS:
            return {
                'outcome': {
                    self.player_x: 'win',
                    self.player_o: 'loss'
                },
                'points': {
                    self.player_x: 3,
                    self.player_o: 0
                },
                'winner': self.player_x
            }
        elif outcome == GameOutcome.O_WINS:
            return {
                'outcome': {
                    self.player_x: 'loss',
                    self.player_o: 'win'
                },
                'points': {
                    self.player_x: 0,
                    self.player_o: 3
                },
                'winner': self.player_o
            }
        else:  # Draw
            return {
                'outcome': {
                    self.player_x: 'draw',
                    self.player_o: 'draw'
                },
                'points': {
                    self.player_x: 1,
                    self.player_o: 1
                },
                'winner': None
            }

    def get_metadata(self) -> Dict[str, Any]:
        """Get additional game metadata.

        Returns:
            Dictionary with game-specific metadata
        """
        return {
            'final_state': self.get_state_summary(),
            'total_moves': self.move_count
        }
