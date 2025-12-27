"""Random Tic Tac Toe strategy implementation.

This module implements a random strategy that picks
any valid move at random.
"""

import logging
import random
from typing import Any, Dict

from ...common.strategy_interface import StrategyInterface
from ...common.tic_tac_toe_utils import get_available_moves

logger = logging.getLogger(__name__)


class TicTacToeRandomStrategy(StrategyInterface):
    """Random move selection strategy for Tic Tac Toe.

    This strategy simply picks a random valid move from
    all available positions.
    """

    def compute_move(self, step_context: Dict[str, Any]) -> Dict[str, Any]:
        """Compute random move.

        Args:
            step_context: Game-specific context

        Returns:
            Move payload

        Raises:
            ValueError: If no valid moves available
        """
        board = step_context.get('board', [])

        # Find available moves using shared utility
        available_moves = get_available_moves(board)

        if not available_moves:
            raise ValueError("No available moves")

        move = random.choice(available_moves)

        logger.debug("Player %s chose random move: %s", self.player_id, move)

        return {
            'row': move[0],
            'col': move[1]
        }

    def get_strategy_name(self) -> str:
        """Get the name of this strategy.

        Returns:
            Human-readable strategy name
        """
        return "Random Tic Tac Toe"

    def get_supported_games(self) -> list:
        """Get list of game types this strategy supports.

        Returns:
            List of game type identifiers
        """
        return ['tic_tac_toe']
