"""Abstract base class for referee game engines.

This module defines the interface that all game implementations must follow,
enabling complete separation between communication and game logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class GameInterface(ABC):
    """Abstract base class for all game engines.

    This interface ensures that game logic is completely decoupled from
    the referee's communication layer, making games pluggable and testable.
    """

    def __init__(self, players: list):
        """Initialize a new game.

        Args:
            players: List of player IDs participating in this game
        """
        self.players = players
        self.current_player = None

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the game state.

        This method sets up the initial game state, including determining
        the starting player.
        """
        pass

    @abstractmethod
    def get_current_player(self) -> str:
        """Get the player who should make the next move.

        Returns:
            Player ID of the current player
        """
        pass

    @abstractmethod
    def get_step_context(self) -> Dict[str, Any]:
        """Get context for the next move request.

        This provides all information a player needs to compute their move.
        The format is game-specific.

        Returns:
            Step context dictionary for the current player
        """
        pass

    @abstractmethod
    def validate_move(self, move_payload: Dict[str, Any]) -> bool:
        """Validate whether a move is legal.

        Args:
            move_payload: Move data from player

        Returns:
            True if move is valid, False otherwise
        """
        pass

    @abstractmethod
    def apply_move(self, move_payload: Dict[str, Any]) -> bool:
        """Apply a validated move to the game state.

        Args:
            move_payload: Move data from player

        Returns:
            True if move was successfully applied

        Raises:
            ValueError: If move is invalid
        """
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        """Check if the game has reached a terminal state.

        Returns:
            True if game is over (win, loss, or draw)
        """
        pass

    @abstractmethod
    def get_result(self) -> Dict[str, Any]:
        """Get the final game result.

        Should only be called when is_terminal() returns True.

        Returns:
            Dictionary containing:
                - outcome: Dict mapping player_id to outcome ('win', 'loss', 'draw')
                - points: Dict mapping player_id to points earned
                - winner: Player ID of winner, or None for draw
        """
        pass

    @abstractmethod
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current game state summary.

        Returns:
            Dictionary with game state information for logging/debugging
        """
        pass

    @abstractmethod
    def get_game_type(self) -> str:
        """Get the game type identifier.

        Returns:
            Game type string (e.g., 'tic_tac_toe')
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get additional game metadata.

        This can be overridden by games that want to provide extra
        information in match results.

        Returns:
            Dictionary with game-specific metadata
        """
        return {}
