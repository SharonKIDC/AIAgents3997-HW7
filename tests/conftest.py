"""Shared pytest fixtures for Agent League System tests.

This module provides common fixtures used across the test suite.
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.common.auth import AgentType, AuthManager
from src.common.config import ConfigManager
from src.common.persistence import LeagueDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing.

    Yields:
        LeagueDatabase: Database instance with temporary file
    """
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Create database
    db = LeagueDatabase(path)
    db.initialize_schema()

    yield db

    # Cleanup
    db.close()
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def auth_manager():
    """Create a fresh AuthManager instance.

    Returns:
        AuthManager: Authentication manager
    """
    return AuthManager()


@pytest.fixture
def config_manager(tmp_path):
    """Create a ConfigManager with test configuration.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        ConfigManager: Configuration manager with test config
    """
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(
        """
league:
  name: "Test League"
  min_players: 2
  max_players: 10
  min_referees: 1

server:
  host: "localhost"
  port: 8000

timeouts:
  move_timeout_ms: 30000
  match_timeout_ms: 300000
"""
    )
    return ConfigManager(str(config_file))


@pytest.fixture
def sample_league_id():
    """Provide a consistent league ID for tests.

    Returns:
        str: Sample league ID
    """
    return "test-league-001"


@pytest.fixture
def sample_referee_ids():
    """Provide sample referee IDs.

    Returns:
        list: List of referee IDs
    """
    return ["referee-1", "referee-2", "referee-3"]


@pytest.fixture
def sample_player_ids():
    """Provide sample player IDs.

    Returns:
        list: List of player IDs
    """
    return ["alice", "bob", "charlie", "dave"]


@pytest.fixture
def registered_league(temp_db, sample_league_id, auth_manager):
    """Create a league with registered referees and players.

    Args:
        temp_db: Temporary database fixture
        sample_league_id: League ID fixture
        auth_manager: Auth manager fixture

    Returns:
        dict: Dictionary with db, league_id, auth_manager, referee_ids, player_ids, tokens
    """
    from src.common.protocol import utc_now

    # Create league
    temp_db.create_league(
        sample_league_id, "REGISTRATION", utc_now(), {"name": "Test League", "min_players": 2}
    )

    # Register referees
    referee_ids = ["ref-1", "ref-2"]
    referee_tokens = {}
    for ref_id in referee_ids:
        token = auth_manager.issue_token(ref_id, AgentType.REFEREE)
        temp_db.register_referee(
            ref_id, sample_league_id, auth_token=token, registered_at=utc_now()
        )
        referee_tokens[ref_id] = token

    # Register players
    player_ids = ["alice", "bob", "charlie", "dave"]
    player_tokens = {}
    for player_id in player_ids:
        token = auth_manager.issue_token(player_id, AgentType.PLAYER)
        temp_db.register_player(
            player_id, sample_league_id, auth_token=token, registered_at=utc_now()
        )
        player_tokens[player_id] = token

    return {
        "db": temp_db,
        "league_id": sample_league_id,
        "auth_manager": auth_manager,
        "referee_ids": referee_ids,
        "player_ids": player_ids,
        "referee_tokens": referee_tokens,
        "player_tokens": player_tokens,
    }


@pytest.fixture
def sample_envelope_data():
    """Provide sample envelope data for testing.

    Returns:
        dict: Valid envelope dictionary
    """
    from src.common.protocol import generate_conversation_id, utc_now

    return {
        "protocol": "league.v2",
        "message_type": "REGISTER_PLAYER_REQUEST",
        "sender": "player:alice",
        "timestamp": utc_now(),
        "conversation_id": generate_conversation_id(),
    }


@pytest.fixture
def sample_jsonrpc_request():
    """Provide sample JSON-RPC request for testing.

    Returns:
        dict: Valid JSON-RPC request
    """
    from src.common.protocol import (
        generate_conversation_id,
        generate_message_id,
        utc_now,
    )

    return {
        "jsonrpc": "2.0",
        "method": "league.handle",
        "params": {
            "envelope": {
                "protocol": "league.v2",
                "message_type": "REGISTER_PLAYER_REQUEST",
                "sender": "player:alice",
                "timestamp": utc_now(),
                "conversation_id": generate_conversation_id(),
            },
            "payload": {"player_id": "alice"},
        },
        "id": generate_message_id(),
    }
