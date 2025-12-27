"""Registry pattern for dynamic loading of strategies and games.

This module provides a registry mechanism for discovering and loading
strategies and games at runtime, enabling true pluggability.
"""

import logging
from typing import Dict, Optional, Type

logger = logging.getLogger(__name__)


class Registry:
    """Generic registry for dynamically loading classes."""

    def __init__(self, name: str):
        """Initialize the registry.

        Args:
            name: Registry name for logging
        """
        self.name = name
        self._registry: Dict[str, Type] = {}

    def register(self, key: str, cls: Type) -> None:
        """Register a class with the registry.

        Args:
            key: Unique identifier for this class
            cls: Class to register

        Raises:
            ValueError: If key is already registered
        """
        if key in self._registry:
            logger.warning("%s: Overwriting existing registration for '%s'", self.name, key)

        self._registry[key] = cls
        logger.debug("%s: Registered '%s' -> %s", self.name, key, cls.__name__)

    def get(self, key: str) -> Optional[Type]:
        """Get a registered class.

        Args:
            key: Identifier to look up

        Returns:
            Registered class or None if not found
        """
        return self._registry.get(key)

    def get_or_raise(self, key: str) -> Type:
        """Get a registered class or raise an error.

        Args:
            key: Identifier to look up

        Returns:
            Registered class

        Raises:
            ValueError: If key not found
        """
        cls = self._registry.get(key)
        if cls is None:
            raise ValueError(
                f"{self.name}: No registration found for '{key}'. "
                f"Available: {list(self._registry.keys())}"
            )
        return cls

    def list_keys(self) -> list:
        """List all registered keys.

        Returns:
            List of registered identifiers
        """
        return list(self._registry.keys())

    def is_registered(self, key: str) -> bool:
        """Check if a key is registered.

        Args:
            key: Identifier to check

        Returns:
            True if key is registered
        """
        return key in self._registry

    def clear(self) -> None:
        """Clear all registrations."""
        self._registry.clear()
        logger.debug("%s: Cleared all registrations", self.name)


class StrategyRegistry(Registry):
    """Registry specifically for player strategies."""

    def __init__(self):
        """Initialize the strategy registry."""
        super().__init__("StrategyRegistry")

    def register_strategy(self, name: str, strategy_class: Type) -> None:
        """Register a strategy.

        Args:
            name: Strategy name (e.g., 'smart', 'random')
            strategy_class: Strategy class implementing StrategyInterface
        """
        self.register(name, strategy_class)

    def get_strategy(self, name: str) -> Type:
        """Get a strategy class by name.

        Args:
            name: Strategy name

        Returns:
            Strategy class

        Raises:
            ValueError: If strategy not found
        """
        return self.get_or_raise(name)

    def create_strategy(self, name: str, player_id: str):
        """Create a strategy instance.

        Args:
            name: Strategy name
            player_id: Player identifier

        Returns:
            Strategy instance

        Raises:
            ValueError: If strategy not found
        """
        strategy_class = self.get_strategy(name)
        return strategy_class(player_id)


class GameRegistry(Registry):
    """Registry specifically for game engines."""

    def __init__(self):
        """Initialize the game registry."""
        super().__init__("GameRegistry")

    def register_game(self, game_type: str, game_class: Type) -> None:
        """Register a game.

        Args:
            game_type: Game type identifier (e.g., 'tic_tac_toe')
            game_class: Game class implementing GameInterface
        """
        self.register(game_type, game_class)

    def get_game(self, game_type: str) -> Type:
        """Get a game class by type.

        Args:
            game_type: Game type identifier

        Returns:
            Game class

        Raises:
            ValueError: If game type not found
        """
        return self.get_or_raise(game_type)

    def create_game(self, game_type: str, players: list):
        """Create a game instance.

        Args:
            game_type: Game type identifier
            players: List of player IDs

        Returns:
            Game instance

        Raises:
            ValueError: If game type not found
        """
        game_class = self.get_game(game_type)
        game = game_class(players)
        game.initialize()
        return game
