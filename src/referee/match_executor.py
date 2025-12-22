"""Game-agnostic match execution for the Agent League System.

This module orchestrates match execution following the protocol
specified in the PRD, delegating game-specific logic to game engines.
"""

import logging
from typing import Dict, Any

from ..common.protocol import (
    Envelope,
    MessageType,
    generate_conversation_id,
    utc_now
)
from ..common.transport import LeagueHTTPClient
from ..common.errors import OperationalError, TimeoutError, ErrorCode

from .games import get_game

logger = logging.getLogger(__name__)


class MatchExecutor:
    """Executes matches in a game-agnostic manner."""

    def __init__(
        self,
        referee_id: str,
        http_client: LeagueHTTPClient,
        player_urls: Dict[str, str],
        timeout_ms: int = 30000
    ):
        """Initialize the match executor.

        Args:
            referee_id: Referee identifier
            http_client: HTTP client for communication
            player_urls: Mapping of player_id to URL
            timeout_ms: Move timeout in milliseconds
        """
        self.referee_id = referee_id
        self.http_client = http_client
        self.player_urls = player_urls
        self.timeout_ms = timeout_ms

    def execute_match(
        self,
        match_id: str,
        round_id: str,
        game_type: str,
        players: list,
        league_id: str
    ) -> Dict[str, Any]:
        """Execute a complete match.

        Args:
            match_id: Match identifier
            round_id: Round identifier
            game_type: Game type
            players: List of player IDs
            league_id: League identifier

        Returns:
            Match result dictionary
        """
        logger.info(f"Starting match {match_id}: {players[0]} vs {players[1]}")

        # Initialize game using registry
        try:
            game = get_game(game_type, players)
            logger.info(f"Loaded game: {game.get_game_type()}")
        except ValueError as e:
            raise OperationalError(
                ErrorCode.MATCH_EXECUTION_FAILED,
                f"Unsupported game type: {game_type}. Error: {e}"
            )

        # Send game invitations
        for player_id in players:
            self._send_game_invitation(
                player_id,
                match_id,
                game_type,
                [p for p in players if p != player_id]  # opponents
            )

        # Execute game loop
        while not game.is_terminal():
            current_player = game.get_current_player()
            step_context = game.get_step_context()

            # Request move from current player
            try:
                move = self._request_move(
                    current_player,
                    match_id,
                    game_type,
                    game.move_count + 1,
                    step_context
                )

                # Validate and apply move using the game interface
                if not game.validate_move(move):
                    raise ValueError(f"Invalid move: {move}")

                game.apply_move(move)

                logger.debug(f"Player {current_player} played move: {move}")

            except Exception as e:
                logger.error(f"Move error for player {current_player}: {e}")
                # Forfeit - opponent wins
                return self._create_forfeit_result(game, current_player)

        # Game completed normally
        result = game.get_result()

        # Send game over notifications
        for player_id in players:
            self._send_game_over(player_id, match_id, game_type, result)

        # Create result report
        return {
            'match_id': match_id,
            'round_id': round_id,
            'game_type': game_type,
            'players': players,
            'outcome': result['outcome'],
            'points': result['points'],
            'game_metadata': game.get_metadata()
        }

    def _send_game_invitation(
        self,
        player_id: str,
        match_id: str,
        game_type: str,
        opponents: list
    ):
        """Send game invitation to a player.

        Args:
            player_id: Player identifier
            match_id: Match identifier
            game_type: Game type
            opponents: List of opponent IDs
        """
        url = self.player_urls.get(player_id)
        if not url:
            logger.warning(f"No URL for player {player_id}")
            return

        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.GAME_INVITATION.value,
            sender=f"referee:{self.referee_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            match_id=match_id,
            game_type=game_type
        )

        payload = {
            'match_id': match_id,
            'game_type': game_type,
            'opponents': opponents
        }

        try:
            self.http_client.send_request(url, envelope, payload)
            logger.info(f"Sent game invitation to {player_id}")
        except Exception as e:
            logger.error(f"Failed to send invitation to {player_id}: {e}")

    def _request_move(
        self,
        player_id: str,
        match_id: str,
        game_type: str,
        step_number: int,
        step_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request a move from a player.

        Args:
            player_id: Player identifier
            match_id: Match identifier
            game_type: Game type
            step_number: Current step number
            step_context: Game-specific context

        Returns:
            Move payload from player

        Raises:
            TimeoutError: If player doesn't respond in time
        """
        url = self.player_urls.get(player_id)
        if not url:
            raise OperationalError(
                ErrorCode.MATCH_EXECUTION_FAILED,
                f"No URL for player {player_id}"
            )

        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REQUEST_MOVE.value,
            sender=f"referee:{self.referee_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            match_id=match_id,
            game_type=game_type
        )

        payload = {
            'step_number': step_number,
            'step_context': step_context
        }

        try:
            result = self.http_client.send_request(url, envelope, payload)
            move_response = result.get('payload', {})
            return move_response.get('move_payload', {})
        except Exception as e:
            raise TimeoutError(f"Player {player_id} failed to respond: {e}")

    def _send_game_over(
        self,
        player_id: str,
        match_id: str,
        game_type: str,
        result: Dict[str, Any]
    ):
        """Send game over notification to a player.

        Args:
            player_id: Player identifier
            match_id: Match identifier
            game_type: Game type
            result: Game result
        """
        url = self.player_urls.get(player_id)
        if not url:
            return

        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.GAME_OVER.value,
            sender=f"referee:{self.referee_id}",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            match_id=match_id,
            game_type=game_type
        )

        payload = {
            'outcome': result['outcome'][player_id],
            'final_state': result.get('game_metadata', {})
        }

        try:
            self.http_client.send_request_no_response(url, envelope, payload)
        except Exception as e:
            logger.warning(f"Failed to send game over to {player_id}: {e}")

    def _create_forfeit_result(
        self,
        game,
        forfeiting_player: str
    ) -> Dict[str, Any]:
        """Create result for a forfeited match.

        Args:
            game: Game instance (GameInterface)
            forfeiting_player: Player who forfeited

        Returns:
            Match result with forfeit
        """
        # Determine winner (the other player)
        winner = None
        for player_id in game.players:
            if player_id != forfeiting_player:
                winner = player_id
                break

        if winner is None:
            # Fallback - shouldn't happen
            winner = game.players[0] if game.players[0] != forfeiting_player else game.players[1]

        result = {
            'outcome': {
                winner: 'win',
                forfeiting_player: 'loss'
            },
            'points': {
                winner: 3,
                forfeiting_player: 0
            },
            'game_metadata': {
                'forfeit': True,
                'forfeiting_player': forfeiting_player
            }
        }

        # Add any additional game metadata
        result['game_metadata'].update(game.get_metadata())

        return result
