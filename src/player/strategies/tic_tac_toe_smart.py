"""Smart Tic Tac Toe strategy implementation.

This module implements a smart strategy that tries to win,
blocks opponent wins, and makes strategic moves.
"""

import logging
import random
from typing import Any, Dict, Optional, Tuple

from ...common.strategy_interface import StrategyInterface

logger = logging.getLogger(__name__)


class TicTacToeSmartStrategy(StrategyInterface):
    """Smart strategy for playing Tic Tac Toe.

    This strategy:
    1. Takes winning moves when available
    2. Blocks opponent's winning moves
    3. Makes random valid moves otherwise
    """

    def __init__(self, player_id: str):
        """Initialize the strategy.

        Args:
            player_id: Player identifier
        """
        super().__init__(player_id)

    def compute_move(self, step_context: Dict[str, Any]) -> Dict[str, Any]:
        """Compute next move based on game state.

        Args:
            step_context: Game-specific context from referee

        Returns:
            Move payload

        Raises:
            ValueError: If no valid moves available
        """
        board = step_context.get('board', [])
        my_mark = step_context.get('your_mark')

        logger.debug("Computing move for %s (mark: %s)", self.player_id, my_mark)

        # Find available moves
        available_moves = []
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":
                    available_moves.append((row, col))

        if not available_moves:
            raise ValueError("No available moves")

        # Simple strategy: check for winning move, blocking move, or random
        move = (
            self._find_winning_move(board, my_mark) or
            self._find_blocking_move(board, my_mark) or
            random.choice(available_moves)
        )

        logger.info("Player %s chose move: %s", self.player_id, move)

        return {
            'row': move[0],
            'col': move[1]
        }

    def get_strategy_name(self) -> str:
        """Get the name of this strategy.

        Returns:
            Human-readable strategy name
        """
        return "Smart Tic Tac Toe"

    def get_supported_games(self) -> list:
        """Get list of game types this strategy supports.

        Returns:
            List of game type identifiers
        """
        return ['tic_tac_toe']

    def _find_winning_move(
        self,
        board: list,
        my_mark: str
    ) -> Optional[Tuple[int, int]]:
        """Find a move that wins the game.

        Args:
            board: Current board state
            my_mark: Player's mark (X or O)

        Returns:
            Winning move or None
        """
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":
                    # Try this move
                    if self._would_win(board, row, col, my_mark):
                        return (row, col)
        return None

    def _find_blocking_move(
        self,
        board: list,
        my_mark: str
    ) -> Optional[Tuple[int, int]]:
        """Find a move that blocks opponent from winning.

        Args:
            board: Current board state
            my_mark: Player's mark

        Returns:
            Blocking move or None
        """
        opponent_mark = "O" if my_mark == "X" else "X"
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":
                    # Check if opponent would win here
                    if self._would_win(board, row, col, opponent_mark):
                        return (row, col)
        return None

    def _would_win(
        self,
        board: list,
        row: int,
        col: int,
        mark: str
    ) -> bool:
        """Check if placing mark at (row, col) would win.

        Args:
            board: Current board state
            row: Row index
            col: Column index
            mark: Mark to place

        Returns:
            True if this move wins
        """
        # Create temporary board
        temp_board = [row[:] for row in board]
        temp_board[row][col] = mark

        # Check row
        if all(temp_board[row][c] == mark for c in range(3)):
            return True

        # Check column
        if all(temp_board[r][col] == mark for r in range(3)):
            return True

        # Check diagonal
        if row == col and all(temp_board[i][i] == mark for i in range(3)):
            return True

        # Check anti-diagonal
        if row + col == 2 and all(temp_board[i][2-i] == mark for i in range(3)):
            return True

        return False
