"""Configuration management for the Agent League System.

This module handles loading and providing access to league configuration.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml

from .errors import ConfigurationError


@dataclass
class LeagueConfig:
    """League configuration settings."""

    league_id: str
    name: str
    registration_window_seconds: int
    min_players: int
    max_players: int
    min_referees: int


@dataclass
class SchedulingConfig:
    """Scheduling configuration settings."""

    algorithm: str
    concurrent_matches_per_round: bool


@dataclass
class TimeoutConfig:
    """Timeout configuration settings."""

    registration_response_ms: int
    match_join_ack_ms: int
    move_response_ms: int
    result_report_ms: int


@dataclass
class RetryConfig:
    """Retry configuration settings."""

    max_attempts: int
    backoff_ms: int


@dataclass
class LoggingConfig:
    """Logging configuration settings."""

    audit_log_path: str
    application_log_path: str
    log_level: str


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    path: str


@dataclass
class GameConfig:
    """Game type configuration."""

    game_type: str
    name: str
    description: str
    referee_implementation: str
    scoring: Dict[str, int]


class ConfigManager:
    """Manages configuration loading and access."""

    def __init__(self, config_dir: str = "./config"):
        """Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.league: Optional[LeagueConfig] = None
        self.scheduling: Optional[SchedulingConfig] = None
        self.timeouts: Optional[TimeoutConfig] = None
        self.retries: Optional[RetryConfig] = None
        self.logging: Optional[LoggingConfig] = None
        self.database: Optional[DatabaseConfig] = None
        self.games: Dict[str, GameConfig] = {}

    def load_all(self):
        """Load all configuration files."""
        self.load_league_config()
        self.load_game_registry()

    def load_league_config(self, filename: str = "league.yaml"):
        """Load league configuration.

        Args:
            filename: Configuration file name

        Raises:
            ConfigurationError: If configuration is invalid
        """
        config_path = self.config_dir / filename
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}", path=str(config_path))

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Parse league settings
            league_data = data.get("league", {})
            self.league = LeagueConfig(
                league_id=league_data.get("league_id", "default-league"),
                name=league_data.get("name", "Agent League"),
                registration_window_seconds=data.get("registration", {}).get("window_seconds", 60),
                min_players=data.get("registration", {}).get("min_players", 2),
                max_players=data.get("registration", {}).get("max_players", 100),
                min_referees=data.get("registration", {}).get("min_referees", 1),
            )

            # Parse scheduling settings
            scheduling_data = data.get("scheduling", {})
            self.scheduling = SchedulingConfig(
                algorithm=scheduling_data.get("algorithm", "round_robin"),
                concurrent_matches_per_round=scheduling_data.get("concurrent_matches_per_round", True),
            )

            # Parse timeout settings
            timeout_data = data.get("timeouts", {})
            self.timeouts = TimeoutConfig(
                registration_response_ms=timeout_data.get("registration_response_ms", 5000),
                match_join_ack_ms=timeout_data.get("match_join_ack_ms", 10000),
                move_response_ms=timeout_data.get("move_response_ms", 30000),
                result_report_ms=timeout_data.get("result_report_ms", 60000),
            )

            # Parse retry settings
            retry_data = data.get("retries", {})
            self.retries = RetryConfig(
                max_attempts=retry_data.get("max_attempts", 3), backoff_ms=retry_data.get("backoff_ms", 1000)
            )

            # Parse logging settings
            logging_data = data.get("logging", {})
            self.logging = LoggingConfig(
                audit_log_path=logging_data.get("audit_log_path", "./logs/audit.jsonl"),
                application_log_path=logging_data.get("application_log_path", "./logs/league_manager.log"),
                log_level=logging_data.get("log_level", "INFO"),
            )

            # Parse database settings
            db_data = data.get("database", {})
            self.database = DatabaseConfig(path=db_data.get("path", "./data/league.db"))

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in configuration: {str(e)}", path=str(config_path)) from e
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {str(e)}", path=str(config_path)) from e

    def load_game_registry(self, filename: str = "game_registry.yaml"):
        """Load game registry configuration.

        Args:
            filename: Game registry file name

        Raises:
            ConfigurationError: If configuration is invalid
        """
        config_path = self.config_dir / filename
        if not config_path.exists():
            # Game registry is optional, create default
            self.games = {
                "tic_tac_toe": GameConfig(
                    game_type="tic_tac_toe",
                    name="Tic Tac Toe",
                    description="Classic 3x3 grid game",
                    referee_implementation="src.referee.games.tic_tac_toe.TicTacToeReferee",
                    scoring={"win": 3, "draw": 1, "loss": 0},
                )
            }
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            games_data = data.get("games", [])
            for game_data in games_data:
                game = GameConfig(
                    game_type=game_data["game_type"],
                    name=game_data["name"],
                    description=game_data.get("description", ""),
                    referee_implementation=game_data["referee_implementation"],
                    scoring=game_data.get("scoring", {"win": 3, "draw": 1, "loss": 0}),
                )
                self.games[game.game_type] = game

        except Exception as e:
            raise ConfigurationError(f"Error loading game registry: {str(e)}", path=str(config_path)) from e

    def get_game_config(self, game_type: str) -> Optional[GameConfig]:
        """Get configuration for a specific game type.

        Args:
            game_type: Game type identifier

        Returns:
            GameConfig or None if not found
        """
        return self.games.get(game_type)

    def get_scoring(self, game_type: str) -> Dict[str, int]:
        """Get scoring rules for a game type.

        Args:
            game_type: Game type identifier

        Returns:
            Scoring dictionary (win/draw/loss -> points)
        """
        game = self.get_game_config(game_type)
        if game:
            return game.scoring
        return {"win": 3, "draw": 1, "loss": 0}  # Default


def load_config(config_dir: str = "./config") -> ConfigManager:
    """Load configuration from directory.

    Args:
        config_dir: Directory containing configuration files

    Returns:
        ConfigManager instance

    Raises:
        ConfigurationError: If configuration cannot be loaded
    """
    manager = ConfigManager(config_dir)
    manager.load_all()
    return manager
