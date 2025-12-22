"""Tests for authentication and authorization.

This module tests token generation, validation, and authorization checks.
"""

import pytest
from src.common.auth import AuthManager, AgentType
from src.common.errors import AuthenticationError, AuthorizationError


class TestAuthManager:
    """Tests for AuthManager class."""

    def test_issue_token(self, auth_manager):
        """Test issuing a new token."""
        token = auth_manager.issue_token('player-1', AgentType.PLAYER)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_issue_token_idempotent(self, auth_manager):
        """Test that issuing token for same agent returns same token."""
        token1 = auth_manager.issue_token('player-1', AgentType.PLAYER)
        token2 = auth_manager.issue_token('player-1', AgentType.PLAYER)

        assert token1 == token2

    def test_validate_token_success(self, auth_manager):
        """Test validating a valid token."""
        token = auth_manager.issue_token('referee-1', AgentType.REFEREE)

        result = auth_manager.validate_token(token)

        assert result['agent_id'] == 'referee-1'
        assert result['agent_type'] == AgentType.REFEREE.value

    def test_validate_token_invalid(self, auth_manager):
        """Test validating an invalid token."""
        with pytest.raises(AuthenticationError):
            auth_manager.validate_token('invalid-token')

    def test_verify_sender_league_manager(self, auth_manager):
        """Test verifying league manager sender."""
        token = auth_manager.issue_token('league', AgentType.LEAGUE_MANAGER)

        # Should not raise
        auth_manager.verify_sender(token, 'league_manager')

    def test_verify_sender_referee(self, auth_manager):
        """Test verifying referee sender."""
        token = auth_manager.issue_token('ref-1', AgentType.REFEREE)

        # Should not raise
        auth_manager.verify_sender(token, 'referee:ref-1')

    def test_verify_sender_player(self, auth_manager):
        """Test verifying player sender."""
        token = auth_manager.issue_token('alice', AgentType.PLAYER)

        # Should not raise
        auth_manager.verify_sender(token, 'player:alice')

    def test_verify_sender_mismatch(self, auth_manager):
        """Test that sender mismatch raises error."""
        token = auth_manager.issue_token('alice', AgentType.PLAYER)

        with pytest.raises(AuthorizationError):
            auth_manager.verify_sender(token, 'player:bob')

    def test_verify_sender_invalid_token(self, auth_manager):
        """Test that invalid token raises AuthenticationError."""
        with pytest.raises(AuthenticationError):
            auth_manager.verify_sender('invalid-token', 'player:alice')

    def test_invalidate_token(self, auth_manager):
        """Test invalidating a token."""
        token = auth_manager.issue_token('player-1', AgentType.PLAYER)

        # Verify token works
        auth_manager.validate_token(token)

        # Invalidate
        auth_manager.invalidate_token(token)

        # Should now fail
        with pytest.raises(AuthenticationError):
            auth_manager.validate_token(token)

    def test_invalidate_agent(self, auth_manager):
        """Test invalidating all tokens for an agent."""
        token = auth_manager.issue_token('player-1', AgentType.PLAYER)

        # Verify token works
        auth_manager.validate_token(token)

        # Invalidate agent
        auth_manager.invalidate_agent('player-1')

        # Should now fail
        with pytest.raises(AuthenticationError):
            auth_manager.validate_token(token)

    def test_get_agent_id(self, auth_manager):
        """Test getting agent ID from token."""
        token = auth_manager.issue_token('referee-1', AgentType.REFEREE)

        agent_id = auth_manager.get_agent_id(token)
        assert agent_id == 'referee-1'

    def test_get_agent_type(self, auth_manager):
        """Test getting agent type from token."""
        token = auth_manager.issue_token('player-1', AgentType.PLAYER)

        agent_type = auth_manager.get_agent_type(token)
        assert agent_type == AgentType.PLAYER.value

    def test_has_token(self, auth_manager):
        """Test checking if agent has token."""
        assert not auth_manager.has_token('player-1')

        auth_manager.issue_token('player-1', AgentType.PLAYER)

        assert auth_manager.has_token('player-1')

    def test_multiple_agents(self, auth_manager):
        """Test managing tokens for multiple agents."""
        # Issue tokens for different agents
        token1 = auth_manager.issue_token('player-1', AgentType.PLAYER)
        token2 = auth_manager.issue_token('player-2', AgentType.PLAYER)
        token3 = auth_manager.issue_token('ref-1', AgentType.REFEREE)

        # All should be different
        assert token1 != token2
        assert token1 != token3
        assert token2 != token3

        # All should validate correctly
        assert auth_manager.validate_token(token1)['agent_id'] == 'player-1'
        assert auth_manager.validate_token(token2)['agent_id'] == 'player-2'
        assert auth_manager.validate_token(token3)['agent_id'] == 'ref-1'

    def test_thread_safety(self, auth_manager):
        """Test that auth manager is thread-safe."""
        import threading

        tokens = {}
        errors = []

        def issue_token(agent_id):
            try:
                token = auth_manager.issue_token(agent_id, AgentType.PLAYER)
                tokens[agent_id] = token
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=issue_token, args=(f'player-{i}',))
            for i in range(10)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should have occurred
        assert len(errors) == 0
        # All tokens should be issued
        assert len(tokens) == 10
