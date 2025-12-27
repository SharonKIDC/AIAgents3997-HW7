"""Tic Tac Toe game utilities.

This module provides common utility functions for working with
tic-tac-toe boards.
"""

from typing import List, Tuple


def get_available_moves(board: List[List[str]]) -> List[Tuple[int, int]]:
    """Get list of available moves on the board.

    Args:
        board: 3x3 tic-tac-toe board

    Returns:
        List of (row, col) tuples for empty positions
    """
    available_moves = []
    for row in range(3):
        for col in range(3):
            if board[row][col] == "":
                available_moves.append((row, col))
    return available_moves


def would_win(board: List[List[str]], row: int, col: int, mark: str) -> bool:
    """Check if placing mark at (row, col) would win the game.

    Args:
        board: Current board state
        row: Row index
        col: Column index
        mark: Mark to place (X or O)

    Returns:
        True if this move would result in a win
    """
    # Create temporary board
    temp_board = [row_list[:] for row_list in board]
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
    if row + col == 2 and all(temp_board[i][2 - i] == mark for i in range(3)):
        return True

    return False
