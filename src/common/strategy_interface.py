"""Abstract base class for player strategies.

This module defines the interface that all player strategies must implement,
enabling complete separation between communication and game logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class StrategyInterface(ABC):
    """Abstract base class for all player strategies.

    This interface ensures that strategies are completely decoupled from
    the communication layer, making them pluggable and testable.
    """

    def __init__(self, player_id: str):
        """Initialize the strategy.

        Args:
            player_id: Player identifier
        """
        self.player_id = player_id

    @abstractmethod
    def compute_move(self, step_context: Dict[str, Any]) -> Dict[str, Any]:
        """Compute next move based on game state.

        This is the core method that every strategy must implement.
        The step_context is game-specific and provided by the game engine.

        Args:
            step_context: Game-specific context from referee containing
                         all necessary information to make a move

        Returns:
            Move payload as a dictionary. The format is game-specific
            and must match what the game engine expects.

        Raises:
            ValueError: If no valid moves are available or context is invalid
        """
        raise NotImplementedError()

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy.

        Returns:
            Human-readable strategy name
        """
        raise NotImplementedError()

    @abstractmethod
    def get_supported_games(self) -> list:
        """Get list of game types this strategy supports.

        Returns:
            List of game type identifiers (e.g., ['tic_tac_toe'])
        """
        raise NotImplementedError()
