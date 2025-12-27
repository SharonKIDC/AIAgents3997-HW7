"""Player strategies module with registry.

This module provides the strategy registry and exports all available
strategies for easy importing and discovery.
"""

from ...common.registry import StrategyRegistry
from .tic_tac_toe_random import TicTacToeRandomStrategy
from .tic_tac_toe_smart import TicTacToeSmartStrategy

# Create global strategy registry
strategy_registry = StrategyRegistry()

# Register available strategies
strategy_registry.register_strategy("smart", TicTacToeSmartStrategy)
strategy_registry.register_strategy("random", TicTacToeRandomStrategy)

# Also register with full game-specific names for clarity
strategy_registry.register_strategy("tic_tac_toe_smart", TicTacToeSmartStrategy)
strategy_registry.register_strategy("tic_tac_toe_random", TicTacToeRandomStrategy)

# Export for convenient importing
__all__ = [
    "strategy_registry",
    "TicTacToeSmartStrategy",
    "TicTacToeRandomStrategy",
]


def get_strategy(strategy_name: str, player_id: str):
    """Convenience function to get a strategy instance.

    Args:
        strategy_name: Name of the strategy ('smart', 'random', etc.)
        player_id: Player identifier

    Returns:
        Strategy instance

    Raises:
        ValueError: If strategy name is not registered
    """
    return strategy_registry.create_strategy(strategy_name, player_id)


def list_available_strategies() -> list:
    """List all available strategy names.

    Returns:
        List of registered strategy names
    """
    return strategy_registry.list_keys()
