"""Game implementations with registry.

This module provides the game registry and exports all available
games for easy importing and discovery.
"""

from ...common.registry import GameRegistry
from .tic_tac_toe import TicTacToeGame

# Create global game registry
game_registry = GameRegistry()

# Register available games
game_registry.register_game("tic_tac_toe", TicTacToeGame)

# Export for convenient importing
__all__ = [
    "game_registry",
    "TicTacToeGame",
]


def get_game(game_type: str, players: list):
    """Convenience function to get a game instance.

    Args:
        game_type: Type of game ('tic_tac_toe', etc.)
        players: List of player IDs

    Returns:
        Game instance (already initialized)

    Raises:
        ValueError: If game type is not registered
    """
    return game_registry.create_game(game_type, players)


def list_available_games() -> list:
    """List all available game types.

    Returns:
        List of registered game type identifiers
    """
    return game_registry.list_keys()
