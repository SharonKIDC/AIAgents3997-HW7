"""Integration tests for full league execution.

This module tests the complete league workflow from registration
through match execution to final standings.
"""

import pytest

from src.common.auth import AgentType, AuthManager
from src.common.protocol import Envelope, MessageType, generate_conversation_id, utc_now
from src.league_manager.registration import RegistrationHandler
from src.league_manager.scheduler import RoundRobinScheduler
from src.league_manager.standings import StandingsEngine
from src.league_manager.state import LeagueState, LeagueStatus


@pytest.mark.integration
class TestFullLeagueWorkflow:
    """Integration tests for complete league workflow."""

    def test_complete_league_lifecycle(self, temp_db, config_manager):
        """Test complete league from initialization to completion."""
        league_id = "integration-league-001"

        # 1. Initialize league
        auth_manager = AuthManager()
        league_state = LeagueState(league_id, temp_db, config_manager)
        league_state.initialize()

        assert league_state.status == LeagueStatus.REGISTRATION

        # 2. Registration phase
        registration_handler = RegistrationHandler(league_state, temp_db, auth_manager)

        # Register referees
        ref_ids = ["ref-1", "ref-2"]
        for ref_id in ref_ids:
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_REFEREE_REQUEST.value,
                sender=f"referee:{ref_id}",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            result = registration_handler.register_referee(ref_id, envelope)
            assert result["status"] == "registered"

        # Register players
        player_ids = ["alice", "bob", "charlie", "dave"]
        for player_id in player_ids:
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
                sender=f"player:{player_id}",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            result = registration_handler.register_player(player_id, envelope)
            assert result["status"] == "registered"

        # Verify registration counts
        assert league_state.get_referee_count() == 2
        assert league_state.get_player_count() == 4

        # 3. Transition to scheduling
        assert league_state.transition_to(LeagueStatus.SCHEDULING)

        # 4. Generate schedule
        scheduler = RoundRobinScheduler(temp_db)
        schedule = scheduler.generate_schedule(league_id, player_ids, "tic_tac_toe")

        # Verify schedule
        assert schedule["total_matches"] == 6  # C(4,2) = 6
        assert schedule["total_rounds"] >= 3

        # 5. Transition to active
        assert league_state.transition_to(LeagueStatus.ACTIVE)

        # 6. Simulate match results
        # For integration test, we'll directly store results
        match_count = 0
        for round_info in schedule["rounds"]:
            for match_info in round_info["matches"]:
                match_id = match_info["match_id"]
                players = match_info["players"]

                # Simulate a result (first player wins)
                temp_db.store_result(
                    f"result-{match_count}",
                    match_id,
                    outcome={players[0]: "win", players[1]: "loss"},
                    points={players[0]: 3, players[1]: 0},
                    game_metadata={"moves": 5},
                    reported_at=utc_now(),
                )

                temp_db.update_match_status(match_id, "COMPLETED")
                match_count += 1

        # 7. Compute standings
        standings_engine = StandingsEngine(temp_db)
        standings = standings_engine.compute_standings(league_id)

        # Verify standings
        assert len(standings["standings"]) == 4
        for ranking in standings["standings"]:
            assert "player_id" in ranking
            assert "points" in ranking
            assert "wins" in ranking
            assert "rank" in ranking

        # Publish standings
        snapshot_id = standings_engine.publish_standings(league_id)
        assert snapshot_id is not None

        # 8. Verify final state
        final_standings = standings_engine.get_standings(league_id)
        assert final_standings is not None
        assert len(final_standings["standings"]) == 4

        # 9. Transition to completed
        assert league_state.transition_to(LeagueStatus.COMPLETED)

    def test_league_with_minimum_players(self, temp_db, config_manager):
        """Test league with minimum number of players (2)."""
        league_id = "min-players-league"

        auth_manager = AuthManager()
        league_state = LeagueState(league_id, temp_db, config_manager)
        league_state.initialize()

        registration_handler = RegistrationHandler(league_state, temp_db, auth_manager)

        # Register one referee
        ref_envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_REFEREE_REQUEST.value,
            sender="referee:ref-1",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )
        registration_handler.register_referee("ref-1", ref_envelope)

        # Register two players
        for player_id in ["alice", "bob"]:
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
                sender=f"player:{player_id}",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            registration_handler.register_player(player_id, envelope)

        # Generate schedule
        league_state.transition_to(LeagueStatus.SCHEDULING)
        scheduler = RoundRobinScheduler(temp_db)
        schedule = scheduler.generate_schedule(league_id, ["alice", "bob"], "tic_tac_toe")

        # Should have exactly 1 match
        assert schedule["total_matches"] == 1
        assert schedule["total_rounds"] == 1

    def test_league_state_persistence(self, temp_db, config_manager):
        """Test that league state persists across instances."""
        league_id = "persistence-test-league"

        # Create first instance
        auth_manager1 = AuthManager()
        league_state1 = LeagueState(league_id, temp_db, config_manager)
        league_state1.initialize()

        registration_handler1 = RegistrationHandler(league_state1, temp_db, auth_manager1)

        # Register a referee
        ref_envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_REFEREE_REQUEST.value,
            sender="referee:ref-1",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )
        registration_handler1.register_referee("ref-1", ref_envelope)

        # Create second instance (simulating restart)
        _auth_manager2 = AuthManager()  # noqa: F841
        league_state2 = LeagueState(league_id, temp_db, config_manager)
        league_state2.initialize()

        # Should have loaded existing league
        assert league_state2.status == LeagueStatus.REGISTRATION
        assert league_state2.get_referee_count() == 1

    def test_standings_reflect_all_match_results(self, temp_db, config_manager):
        """Test that standings correctly reflect all match outcomes."""
        league_id = "standings-test-league"

        # Setup
        auth_manager = AuthManager()
        league_state = LeagueState(league_id, temp_db, config_manager)
        league_state.initialize()

        # Register players
        registration_handler = RegistrationHandler(league_state, temp_db, auth_manager)

        ref_envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_REFEREE_REQUEST.value,
            sender="referee:ref-1",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )
        registration_handler.register_referee("ref-1", ref_envelope)

        players = ["alice", "bob", "charlie"]
        for player_id in players:
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
                sender=f"player:{player_id}",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            registration_handler.register_player(player_id, envelope)

        # Create round and matches
        league_state.transition_to(LeagueStatus.ACTIVE)
        temp_db.create_round("round-1", league_id, 1)

        # Match 1: alice vs bob (alice wins)
        temp_db.create_match("match-1", "round-1", "tic_tac_toe", players=["alice", "bob"])
        temp_db.store_result(
            "result-1",
            "match-1",
            outcome={"alice": "win", "bob": "loss"},
            points={"alice": 3, "bob": 0},
            game_metadata=None,
            reported_at=utc_now(),
        )

        # Match 2: alice vs charlie (draw)
        temp_db.create_match("match-2", "round-1", "tic_tac_toe", players=["alice", "charlie"])
        temp_db.store_result(
            "result-2",
            "match-2",
            outcome={"alice": "draw", "charlie": "draw"},
            points={"alice": 1, "charlie": 1},
            game_metadata=None,
            reported_at=utc_now(),
        )

        # Match 3: bob vs charlie (charlie wins)
        temp_db.create_match("match-3", "round-1", "tic_tac_toe", players=["bob", "charlie"])
        temp_db.store_result(
            "result-3",
            "match-3",
            outcome={"bob": "loss", "charlie": "win"},
            points={"bob": 0, "charlie": 3},
            game_metadata=None,
            reported_at=utc_now(),
        )

        # Compute standings
        standings_engine = StandingsEngine(temp_db)
        standings = standings_engine.compute_standings(league_id)

        # Verify points
        alice = next(r for r in standings["standings"] if r["player_id"] == "alice")
        bob = next(r for r in standings["standings"] if r["player_id"] == "bob")
        charlie = next(r for r in standings["standings"] if r["player_id"] == "charlie")

        # Alice: 1 win (3) + 1 draw (1) = 4 points
        assert alice["points"] == 4
        assert alice["wins"] == 1
        assert alice["draws"] == 1

        # Charlie: 1 win (3) + 1 draw (1) = 4 points
        assert charlie["points"] == 4
        assert charlie["wins"] == 1
        assert charlie["draws"] == 1

        # Bob: 2 losses = 0 points
        assert bob["points"] == 0
        assert bob["losses"] == 2

        # Ranking: alice and charlie tied at 4 points (alice should be first alphabetically)
        assert standings["standings"][0]["player_id"] in ["alice", "charlie"]
        assert standings["standings"][1]["player_id"] in ["alice", "charlie"]
        assert standings["standings"][2]["player_id"] == "bob"

    def test_authentication_throughout_lifecycle(self, temp_db, config_manager):
        """Test that authentication works throughout league lifecycle."""
        league_id = "auth-test-league"

        auth_manager = AuthManager()
        league_state = LeagueState(league_id, temp_db, config_manager)
        league_state.initialize()

        registration_handler = RegistrationHandler(league_state, temp_db, auth_manager)

        # Register referee and get token
        ref_envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_REFEREE_REQUEST.value,
            sender="referee:ref-1",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )
        ref_result = registration_handler.register_referee("ref-1", ref_envelope)
        ref_token = ref_result["auth_token"]

        # Register player and get token
        player_envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
            sender="player:alice",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )
        player_result = registration_handler.register_player("alice", player_envelope)
        player_token = player_result["auth_token"]

        # Verify tokens work
        ref_info = auth_manager.validate_token(ref_token)
        assert ref_info["agent_id"] == "ref-1"
        assert ref_info["agent_type"] == AgentType.REFEREE.value

        player_info = auth_manager.validate_token(player_token)
        assert player_info["agent_id"] == "alice"
        assert player_info["agent_type"] == AgentType.PLAYER.value

        # Verify sender verification works
        auth_manager.verify_sender(ref_token, "referee:ref-1")
        auth_manager.verify_sender(player_token, "player:alice")

    def test_schedule_determinism_across_runs(self, temp_db, config_manager):
        """Test that schedule is deterministic across multiple runs."""
        league_id1 = "determinism-test-1"
        league_id2 = "determinism-test-2"

        players = ["alice", "bob", "charlie", "dave"]

        # Generate schedule for first league
        scheduler = RoundRobinScheduler(temp_db)
        temp_db.create_league(league_id1, "SCHEDULING", utc_now(), {})
        schedule1 = scheduler.generate_schedule(league_id1, players, "tic_tac_toe")

        # Generate schedule for second league (same players)
        temp_db.create_league(league_id2, "SCHEDULING", utc_now(), {})
        schedule2 = scheduler.generate_schedule(league_id2, players, "tic_tac_toe")

        # Should have same structure
        assert schedule1["total_matches"] == schedule2["total_matches"]
        assert schedule1["total_rounds"] == schedule2["total_rounds"]

        # Extract all pairs from both schedules
        pairs1 = set()
        for round_info in schedule1["rounds"]:
            for match in round_info["matches"]:
                pairs1.add(tuple(sorted(match["players"])))

        pairs2 = set()
        for round_info in schedule2["rounds"]:
            for match in round_info["matches"]:
                pairs2.add(tuple(sorted(match["players"])))

        # Same pairs should be scheduled
        assert pairs1 == pairs2
