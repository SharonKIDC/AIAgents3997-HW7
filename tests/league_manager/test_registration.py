"""Tests for registration handler.

This module tests referee and player registration flows.
"""

import pytest

from src.common.auth import AgentType
from src.common.errors import (
    DuplicateRegistrationError,
    PreconditionFailedError,
    RegistrationClosedError,
)
from src.common.protocol import Envelope, MessageType, generate_conversation_id, utc_now
from src.league_manager.registration import RegistrationHandler
from src.league_manager.state import LeagueState, LeagueStatus


class TestRegistrationHandler:
    """Tests for RegistrationHandler class."""

    @pytest.fixture
    def league_state(self, temp_db, sample_league_id, config_manager):
        """Create a league state for testing."""
        state = LeagueState(sample_league_id, temp_db, config_manager)
        state.initialize()
        return state

    @pytest.fixture
    def registration_handler(self, league_state, temp_db, auth_manager):
        """Create a registration handler."""
        return RegistrationHandler(league_state, temp_db, auth_manager)

    @pytest.fixture
    def sample_referee_envelope(self):
        """Create a sample referee registration envelope."""
        return Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_REFEREE_REQUEST.value,
            sender="referee:ref-1",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )

    @pytest.fixture
    def sample_player_envelope(self):
        """Create a sample player registration envelope."""
        return Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
            sender="player:alice",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )

    def test_register_referee_success(self, registration_handler, sample_referee_envelope):
        """Test successful referee registration."""
        result = registration_handler.register_referee("ref-1", sample_referee_envelope)

        assert result["status"] == "registered"
        assert "auth_token" in result
        assert "league_id" in result

    def test_register_referee_duplicate(self, registration_handler, sample_referee_envelope):
        """Test that duplicate referee registration raises error."""
        registration_handler.register_referee("ref-1", sample_referee_envelope)

        with pytest.raises(DuplicateRegistrationError):
            registration_handler.register_referee("ref-1", sample_referee_envelope)

    def test_register_referee_closed(
        self, registration_handler, league_state, sample_referee_envelope
    ):
        """Test that registering when closed raises error."""
        league_state.transition_to(LeagueStatus.SCHEDULING)

        with pytest.raises(RegistrationClosedError):
            registration_handler.register_referee("ref-1", sample_referee_envelope)

    def test_register_player_success(
        self, registration_handler, sample_player_envelope, sample_referee_envelope
    ):
        """Test successful player registration."""
        # Register a referee first (required)
        registration_handler.register_referee("ref-1", sample_referee_envelope)

        result = registration_handler.register_player("alice", sample_player_envelope)

        assert result["status"] == "registered"
        assert "auth_token" in result
        assert "league_id" in result

    def test_register_player_no_referee(self, registration_handler, sample_player_envelope):
        """Test that player registration requires at least one referee."""
        with pytest.raises(PreconditionFailedError) as exc_info:
            registration_handler.register_player("alice", sample_player_envelope)

        assert "referee" in str(exc_info.value).lower()

    def test_register_player_duplicate(
        self, registration_handler, sample_player_envelope, sample_referee_envelope
    ):
        """Test that duplicate player registration raises error."""
        registration_handler.register_referee("ref-1", sample_referee_envelope)
        registration_handler.register_player("alice", sample_player_envelope)

        with pytest.raises(DuplicateRegistrationError):
            registration_handler.register_player("alice", sample_player_envelope)

    def test_register_player_closed(
        self, registration_handler, league_state, sample_player_envelope
    ):
        """Test that registering when closed raises error."""
        league_state.transition_to(LeagueStatus.SCHEDULING)

        with pytest.raises(RegistrationClosedError):
            registration_handler.register_player("alice", sample_player_envelope)

    def test_multiple_registrations(self, registration_handler, sample_referee_envelope):
        """Test registering multiple referees and players."""

        # Register referees
        def ref_envelope(ref_id):
            return Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_REFEREE_REQUEST.value,
                sender=f"referee:{ref_id}",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )

        for ref_id in ["ref-1", "ref-2"]:
            registration_handler.register_referee(ref_id, ref_envelope(ref_id))

        # Register players
        def player_envelope(player_id):
            return Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
                sender=f"player:{player_id}",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )

        for player_id in ["alice", "bob", "charlie"]:
            result = registration_handler.register_player(player_id, player_envelope(player_id))
            assert result["status"] == "registered"

    def test_auth_tokens_are_valid(
        self, registration_handler, auth_manager, sample_player_envelope, sample_referee_envelope
    ):
        """Test that issued auth tokens are valid."""
        # Register referee
        ref_result = registration_handler.register_referee("ref-1", sample_referee_envelope)
        ref_token = ref_result["auth_token"]

        # Verify token
        ref_info = auth_manager.validate_token(ref_token)
        assert ref_info["agent_id"] == "ref-1"
        assert ref_info["agent_type"] == AgentType.REFEREE.value

        # Register player
        player_result = registration_handler.register_player("alice", sample_player_envelope)
        player_token = player_result["auth_token"]

        # Verify token
        player_info = auth_manager.validate_token(player_token)
        assert player_info["agent_id"] == "alice"
        assert player_info["agent_type"] == AgentType.PLAYER.value
