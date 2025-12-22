# Extensibility Guide

## Overview

This document provides comprehensive guidance on extending the Agent League System. The architecture is designed for extensibility at multiple levels: games, protocols, scheduling algorithms, player strategies, and infrastructure components.

## Document Control

- **Version**: 1.0
- **Last Updated**: 2025-12-21
- **Status**: Authoritative
- **Related Documents**: [Architecture.md](Architecture.md), [BUILDING_BLOCKS.md](BUILDING_BLOCKS.md)

---

## Table of Contents

1. [Adding New Game Types](#1-adding-new-game-types)
2. [Extending the Protocol](#2-extending-the-protocol)
3. [Adding New Scheduling Algorithms](#3-adding-new-scheduling-algorithms)
4. [Adding New Player Strategies](#4-adding-new-player-strategies)
5. [Plugin Architecture](#5-plugin-architecture)
6. [Custom Agent Types](#6-custom-agent-types)
7. [Configuration Extensions](#7-configuration-extensions)
8. [Testing Extensions](#8-testing-extensions)

---

## 1. Adding New Game Types

### 1.1 Overview

The Agent League System is game-agnostic at the league level. Game-specific logic is encapsulated in referee implementations, making it easy to add new games without modifying the core league infrastructure.

### 1.2 Game Interface Requirements

All game implementations must provide the following interface:

```python
class GameInterface:
    """Abstract interface for game implementations."""

    def __init__(self, match_id: str, players: List[str], config: Optional[Dict] = None):
        """Initialize game state.

        Args:
            match_id: Unique match identifier
            players: List of player IDs participating
            config: Optional game-specific configuration
        """
        pass

    def is_terminal(self) -> bool:
        """Check if game has reached a terminal state.

        Returns:
            True if game is over
        """
        pass

    def make_move(self, player_id: str, move_payload: Dict[str, Any]) -> None:
        """Apply a player's move to the game state.

        Args:
            player_id: Player making the move
            move_payload: Game-specific move data

        Raises:
            ValidationError: If move is invalid
        """
        pass

    def get_result(self) -> Dict[str, Any]:
        """Get the final game result.

        Returns:
            Dictionary with 'outcome' and 'points' keys
            {
                'outcome': {'player_id_1': 'win', 'player_id_2': 'loss'},
                'points': {'player_id_1': 3, 'player_id_2': 0}
            }
        """
        pass

    def get_step_context(self, player_id: str) -> Dict[str, Any]:
        """Get game state context for a player's move request.

        Args:
            player_id: Player requesting context

        Returns:
            Game-specific context dictionary (opaque to league protocol)
        """
        pass

    def validate_move(self, player_id: str, move_payload: Dict[str, Any]) -> bool:
        """Validate if a move is legal.

        Args:
            player_id: Player making the move
            move_payload: Move to validate

        Returns:
            True if move is valid
        """
        pass
```

### 1.3 Step-by-Step Guide: Adding Tic Tac Toe

**Step 1: Create Game Implementation**

Create `/root/Git/AIAgents3997-HW7/src/referee/games/tic_tac_toe.py`:

```python
"""Tic Tac Toe game implementation."""

from typing import Dict, Any, List, Optional
from src.common.errors import ValidationError

class TicTacToeGame:
    """Tic Tac Toe game engine."""

    def __init__(self, match_id: str, players: List[str], config: Optional[Dict] = None):
        self.match_id = match_id
        self.players = players
        self.board = [[None, None, None] for _ in range(3)]
        self.current_player_idx = 0
        self.move_count = 0
        self.winner = None

    def is_terminal(self) -> bool:
        """Check if game is over."""
        return self.winner is not None or self.move_count == 9

    def make_move(self, player_id: str, move_payload: Dict[str, Any]) -> None:
        """Apply a move."""
        if not self.validate_move(player_id, move_payload):
            raise ValidationError("Invalid move", move=move_payload)

        row = move_payload['row']
        col = move_payload['col']
        symbol = 'X' if self.current_player_idx == 0 else 'O'

        self.board[row][col] = symbol
        self.move_count += 1

        # Check for winner
        if self._check_win(symbol):
            self.winner = player_id

        # Switch player
        self.current_player_idx = 1 - self.current_player_idx

    def get_result(self) -> Dict[str, Any]:
        """Get final result."""
        if self.winner:
            outcome = {
                self.players[0]: 'win' if self.winner == self.players[0] else 'loss',
                self.players[1]: 'win' if self.winner == self.players[1] else 'loss'
            }
            points = {
                self.players[0]: 3 if self.winner == self.players[0] else 0,
                self.players[1]: 3 if self.winner == self.players[1] else 0
            }
        else:
            # Draw
            outcome = {self.players[0]: 'draw', self.players[1]: 'draw'}
            points = {self.players[0]: 1, self.players[1]: 1}

        return {
            'outcome': outcome,
            'points': points,
            'game_metadata': {
                'final_board': self.board,
                'total_moves': self.move_count
            }
        }

    def get_step_context(self, player_id: str) -> Dict[str, Any]:
        """Get game state for player."""
        return {
            'board': self.board,
            'your_symbol': 'X' if player_id == self.players[0] else 'O',
            'move_number': self.move_count,
            'valid_moves': self._get_valid_moves()
        }

    def validate_move(self, player_id: str, move_payload: Dict[str, Any]) -> bool:
        """Validate move."""
        # Check it's the right player's turn
        current_player = self.players[self.current_player_idx]
        if player_id != current_player:
            return False

        # Check move format
        if 'row' not in move_payload or 'col' not in move_payload:
            return False

        row, col = move_payload['row'], move_payload['col']

        # Check bounds
        if not (0 <= row < 3 and 0 <= col < 3):
            return False

        # Check cell is empty
        if self.board[row][col] is not None:
            return False

        return True

    def _check_win(self, symbol: str) -> bool:
        """Check if symbol has won."""
        # Check rows
        for row in self.board:
            if all(cell == symbol for cell in row):
                return True

        # Check columns
        for col in range(3):
            if all(self.board[row][col] == symbol for row in range(3)):
                return True

        # Check diagonals
        if all(self.board[i][i] == symbol for i in range(3)):
            return True
        if all(self.board[i][2-i] == symbol for i in range(3)):
            return True

        return False

    def _get_valid_moves(self) -> List[Dict[str, int]]:
        """Get list of valid moves."""
        moves = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] is None:
                    moves.append({'row': row, 'col': col})
        return moves
```

**Step 2: Register Game in Game Registry**

Add to `/root/Git/AIAgents3997-HW7/config/game_registry.yaml`:

```yaml
games:
  - game_type: "tic_tac_toe"
    name: "Tic Tac Toe"
    description: "Classic 3x3 grid game"
    referee_implementation: "src.referee.games.tic_tac_toe.TicTacToeGame"
    scoring:
      win: 3
      draw: 1
      loss: 0
    config:
      board_size: 3
      time_limit_per_move: 30
```

**Step 3: Update Referee to Load Game**

The referee server will dynamically load the game implementation:

```python
import importlib

def load_game_engine(game_type: str, match_id: str, players: List[str]):
    """Load game engine dynamically from registry."""
    game_config = config_manager.get_game_config(game_type)
    if not game_config:
        raise ValueError(f"Unknown game type: {game_type}")

    # Import module dynamically
    module_path, class_name = game_config.referee_implementation.rsplit('.', 1)
    module = importlib.import_module(module_path)
    game_class = getattr(module, class_name)

    # Instantiate game
    return game_class(match_id, players, game_config.config)
```

**Step 4: Write Tests**

Create `/root/Git/AIAgents3997-HW7/tests/referee/test_tic_tac_toe.py`:

```python
import pytest
from src.referee.games.tic_tac_toe import TicTacToeGame

def test_tic_tac_toe_win():
    """Test winning condition."""
    game = TicTacToeGame("match-1", ["alice", "bob"])

    # Alice plays X, wins with top row
    game.make_move("alice", {"row": 0, "col": 0})  # X
    game.make_move("bob", {"row": 1, "col": 0})    # O
    game.make_move("alice", {"row": 0, "col": 1})  # X
    game.make_move("bob", {"row": 1, "col": 1})    # O
    game.make_move("alice", {"row": 0, "col": 2})  # X wins

    assert game.is_terminal()
    result = game.get_result()
    assert result['outcome']['alice'] == 'win'
    assert result['outcome']['bob'] == 'loss'
    assert result['points']['alice'] == 3

def test_tic_tac_toe_draw():
    """Test draw condition."""
    game = TicTacToeGame("match-2", ["alice", "bob"])

    # Play to a draw
    moves = [
        ("alice", {"row": 0, "col": 0}),
        ("bob", {"row": 0, "col": 1}),
        ("alice", {"row": 0, "col": 2}),
        ("bob", {"row": 1, "col": 0}),
        ("alice", {"row": 1, "col": 1}),
        ("bob", {"row": 2, "col": 2}),
        ("alice", {"row": 1, "col": 2}),
        ("bob", {"row": 2, "col": 0}),
        ("alice", {"row": 2, "col": 1}),
    ]

    for player, move in moves:
        game.make_move(player, move)

    assert game.is_terminal()
    result = game.get_result()
    assert result['outcome']['alice'] == 'draw'
    assert result['points']['alice'] == 1

def test_invalid_move():
    """Test invalid move detection."""
    game = TicTacToeGame("match-3", ["alice", "bob"])

    # Valid move
    assert game.validate_move("alice", {"row": 0, "col": 0})
    game.make_move("alice", {"row": 0, "col": 0})

    # Invalid: same cell
    assert not game.validate_move("bob", {"row": 0, "col": 0})

    # Invalid: wrong player
    assert not game.validate_move("alice", {"row": 1, "col": 0})

    # Invalid: out of bounds
    assert not game.validate_move("bob", {"row": 3, "col": 0})
```

**Step 5: Verify Integration**

Run the full integration test to ensure the new game works end-to-end:

```bash
pytest tests/integration/test_full_league.py -v
```

---

## 2. Extending the Protocol

### 2.1 Adding New Message Types

To add a new message type for custom functionality:

**Step 1: Define Message Type**

Edit `/root/Git/AIAgents3997-HW7/src/common/protocol.py`:

```python
class MessageType(str, Enum):
    # ... existing types ...

    # New message type
    PLAYER_STATISTICS_REQUEST = "PLAYER_STATISTICS_REQUEST"
    PLAYER_STATISTICS_RESPONSE = "PLAYER_STATISTICS_RESPONSE"
```

**Step 2: Define Payload Schema**

Document the payload structure:

```python
# PLAYER_STATISTICS_REQUEST Payload
{
    "player_id": "alice",
    "include_history": true
}

# PLAYER_STATISTICS_RESPONSE Payload
{
    "player_id": "alice",
    "total_matches": 10,
    "wins": 7,
    "losses": 2,
    "draws": 1,
    "win_rate": 0.7,
    "history": [...]  # Optional
}
```

**Step 3: Implement Handler**

In the League Manager or appropriate agent:

```python
def handle_player_statistics_request(envelope, payload):
    """Handle player statistics request."""
    player_id = payload['player_id']
    include_history = payload.get('include_history', False)

    # Fetch statistics from database
    stats = db.get_player_statistics(player_id)

    response_payload = {
        "player_id": player_id,
        "total_matches": stats['total_matches'],
        "wins": stats['wins'],
        "losses": stats['losses'],
        "draws": stats['draws'],
        "win_rate": stats['wins'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
    }

    if include_history:
        response_payload['history'] = stats['match_history']

    return response_payload
```

**Step 4: Register Handler**

Add to message dispatcher:

```python
message_handlers = {
    MessageType.REGISTER_PLAYER_REQUEST: handle_register_player,
    MessageType.QUERY_STANDINGS: handle_query_standings,
    MessageType.PLAYER_STATISTICS_REQUEST: handle_player_statistics_request,  # New
}
```

### 2.2 Adding Contextual Envelope Fields

To add new contextual fields to the envelope:

**Step 1: Update Envelope Class**

```python
@dataclass
class Envelope:
    # Required fields
    protocol: str
    message_type: str
    sender: str
    timestamp: str
    conversation_id: str

    # Existing contextual fields
    auth_token: Optional[str] = None
    league_id: Optional[str] = None
    round_id: Optional[str] = None
    match_id: Optional[str] = None
    game_type: Optional[str] = None

    # New contextual field
    replay_id: Optional[str] = None  # For replay functionality
```

**Step 2: Update Validation (if needed)**

Add validation for the new field in appropriate message types.

---

## 3. Adding New Scheduling Algorithms

### 3.1 Scheduling Interface

Implement the following interface:

```python
class SchedulerInterface:
    """Abstract interface for scheduling algorithms."""

    def generate_schedule(
        self,
        players: List[str],
        config: SchedulingConfig
    ) -> List[Round]:
        """Generate match schedule.

        Args:
            players: List of player IDs
            config: Scheduling configuration

        Returns:
            List of Round objects with matches
        """
        pass
```

### 3.2 Example: Swiss System Scheduler

**Step 1: Implement Algorithm**

Create `/root/Git/AIAgents3997-HW7/src/league_manager/schedulers/swiss_system.py`:

```python
"""Swiss system tournament scheduler."""

from typing import List, Dict, Tuple
import random

class SwissSystemScheduler:
    """Implements Swiss system tournament scheduling.

    Players are paired each round based on current standings.
    Those with similar scores play each other.
    """

    def __init__(self, num_rounds: int):
        self.num_rounds = num_rounds
        self.pairings_history = []

    def generate_schedule(self, players: List[str], config: SchedulingConfig) -> List[Round]:
        """Generate Swiss system schedule."""
        rounds = []

        # Initialize standings (all players start at 0 points)
        standings = {player: 0 for player in players}

        for round_num in range(self.num_rounds):
            # Sort players by current standings
            sorted_players = sorted(
                standings.items(),
                key=lambda x: (-x[1], x[0])  # By points desc, then player_id
            )

            # Pair players with similar standings
            matches = self._pair_players([p[0] for p in sorted_players])

            # Create round
            round_id = f"swiss-round-{round_num + 1}"
            round_obj = Round(round_id, round_num + 1, matches)
            rounds.append(round_obj)

            # Simulate results for next round (in real implementation, wait for results)
            # This is just for planning purposes
            self._update_standings(matches, standings)

        return rounds

    def _pair_players(self, sorted_players: List[str]) -> List[Match]:
        """Pair players avoiding previous opponents."""
        matches = []
        available = sorted_players.copy()
        match_num = 0

        while len(available) >= 2:
            player1 = available[0]
            available.remove(player1)

            # Find best opponent (hasn't played before, similar standing)
            opponent = None
            for candidate in available:
                if not self._have_played(player1, candidate):
                    opponent = candidate
                    break

            if opponent is None:
                # If no new opponent, take next available
                opponent = available[0]

            available.remove(opponent)

            match_id = f"swiss-match-{match_num}"
            matches.append(Match(match_id, [player1, opponent]))
            self.pairings_history.append((player1, opponent))
            match_num += 1

        # Handle odd player (bye round)
        if len(available) == 1:
            # Player gets a bye (automatic win)
            pass

        return matches

    def _have_played(self, player1: str, player2: str) -> bool:
        """Check if two players have played before."""
        return (player1, player2) in self.pairings_history or \
               (player2, player1) in self.pairings_history

    def _update_standings(self, matches: List[Match], standings: Dict[str, int]):
        """Update standings (stub for planning)."""
        # In real implementation, this would happen after match results
        for match in matches:
            # Simulate random result
            winner = random.choice(match.players)
            standings[winner] += 3
```

**Step 2: Register in Configuration**

Update `/root/Git/AIAgents3997-HW7/config/league.yaml`:

```yaml
scheduling:
  algorithm: "swiss_system"  # or "round_robin"
  swiss_rounds: 5  # Number of rounds for Swiss system
  concurrent_matches_per_round: true
```

**Step 3: Update Scheduler Factory**

```python
def create_scheduler(config: SchedulingConfig):
    """Factory method to create scheduler based on config."""
    if config.algorithm == "round_robin":
        return RoundRobinScheduler()
    elif config.algorithm == "swiss_system":
        return SwissSystemScheduler(num_rounds=config.get('swiss_rounds', 5))
    else:
        raise ValueError(f"Unknown scheduling algorithm: {config.algorithm}")
```

---

## 4. Adding New Player Strategies

### 4.1 Strategy Interface

```python
class PlayerStrategy:
    """Abstract interface for player strategies."""

    def compute_move(
        self,
        step_context: Dict[str, Any],
        game_type: str
    ) -> Dict[str, Any]:
        """Compute next move.

        Args:
            step_context: Game state from referee
            game_type: Type of game being played

        Returns:
            Move payload
        """
        pass
```

### 4.2 Example: Minimax Strategy for Tic Tac Toe

Create `/root/Git/AIAgents3997-HW7/src/player/strategies/minimax.py`:

```python
"""Minimax strategy for turn-based games."""

from typing import Dict, Any

class MinimaxStrategy:
    """Implements minimax algorithm for optimal play."""

    def compute_move(self, step_context: Dict[str, Any], game_type: str) -> Dict[str, Any]:
        """Compute optimal move using minimax."""
        if game_type == "tic_tac_toe":
            return self._tic_tac_toe_minimax(step_context)
        else:
            # Fall back to random for unknown games
            return self._random_move(step_context)

    def _tic_tac_toe_minimax(self, step_context: Dict[str, Any]) -> Dict[str, Any]:
        """Minimax for tic tac toe."""
        board = step_context['board']
        my_symbol = step_context['your_symbol']
        valid_moves = step_context['valid_moves']

        best_score = float('-inf')
        best_move = None

        for move in valid_moves:
            # Simulate move
            score = self._minimax(board, move, my_symbol, False)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, board, move, my_symbol, is_maximizing):
        """Recursive minimax implementation."""
        # Implementation details...
        pass

    def _random_move(self, step_context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to random move."""
        import random
        return random.choice(step_context['valid_moves'])
```

### 4.3 Register Strategy

Update player initialization:

```python
strategy_map = {
    "random": RandomStrategy(),
    "smart": SmartStrategy(),
    "minimax": MinimaxStrategy(),
}

strategy = strategy_map.get(args.strategy, RandomStrategy())
```

---

## 5. Plugin Architecture

### 5.1 Plugin Discovery

Implement a plugin system for auto-discovering extensions:

```python
"""Plugin loader for dynamic game and strategy loading."""

import os
import importlib
from pathlib import Path
from typing import Dict, Type

class PluginLoader:
    """Loads plugins from specified directories."""

    def __init__(self, plugin_dir: str):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Type] = {}

    def discover_plugins(self, base_class: Type) -> Dict[str, Type]:
        """Discover all plugins of a given base class.

        Args:
            base_class: Base class that plugins must inherit from

        Returns:
            Dictionary mapping plugin names to plugin classes
        """
        plugins = {}

        # Scan plugin directory
        for file_path in self.plugin_dir.glob("*.py"):
            if file_path.stem.startswith("_"):
                continue

            # Import module
            module_name = f"plugins.{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin classes
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, base_class) and obj is not base_class:
                    plugins[name.lower()] = obj

        return plugins

# Usage
game_loader = PluginLoader("./plugins/games")
game_plugins = game_loader.discover_plugins(GameInterface)
```

### 5.2 Plugin Configuration

Define plugin metadata:

```yaml
# plugins/games/chess/plugin.yaml
plugin:
  name: "chess"
  version: "1.0.0"
  author: "Chess Plugin Team"
  description: "Full chess implementation"
  entry_point: "chess_game.ChessGame"
  dependencies:
    - "python-chess>=1.0.0"
  config:
    time_control: "blitz"
    starting_position: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
```

---

## 6. Custom Agent Types

### 6.1 Creating a Spectator Agent

Add a read-only spectator agent that observes matches:

**Step 1: Define New Agent Type**

```python
class AgentType(str, Enum):
    LEAGUE_MANAGER = "league_manager"
    REFEREE = "referee"
    PLAYER = "player"
    SPECTATOR = "spectator"  # New
```

**Step 2: Create Spectator Server**

Create `/root/Git/AIAgents3997-HW7/src/spectator/server.py`:

```python
"""Spectator agent for observing matches."""

from src.common.transport import LeagueHTTPServer, LeagueHTTPClient
from src.common.protocol import MessageType, Envelope

class SpectatorServer:
    """Spectator agent that observes and logs matches."""

    def __init__(self, spectator_id: str, host: str, port: int, league_url: str):
        self.spectator_id = spectator_id
        self.league_url = league_url
        self.client = LeagueHTTPClient()
        self.server = LeagueHTTPServer(host, port, self.handle_message)

    def handle_message(self, request):
        """Handle incoming messages (match updates)."""
        envelope = Envelope.from_dict(request.params['envelope'])

        if envelope.message_type == MessageType.MATCH_UPDATE:
            self._log_match_update(request.params['payload'])

        return create_success_response(...)

    def subscribe_to_matches(self):
        """Subscribe to match updates."""
        envelope = Envelope(...)
        payload = {"spectator_id": self.spectator_id, "match_filter": "all"}
        self.client.send_request(self.league_url, envelope, payload)
```

**Step 3: Add MATCH_UPDATE Message**

Follow protocol extension steps from Section 2.

---

## 7. Configuration Extensions

### 7.1 Custom Configuration Sections

Add new configuration sections for extensions:

```yaml
# config/league.yaml

# Existing sections...

# Custom extension: ELO ratings
elo:
  enabled: true
  initial_rating: 1500
  k_factor: 32
  rating_floor: 100

# Custom extension: Achievements
achievements:
  enabled: true
  definitions_file: "achievements.yaml"

# Custom extension: Webhooks
webhooks:
  enabled: true
  on_match_complete: "https://example.com/webhook/match"
  on_round_complete: "https://example.com/webhook/round"
  on_league_complete: "https://example.com/webhook/league"
```

### 7.2 Loading Custom Configuration

```python
@dataclass
class EloConfig:
    """ELO rating configuration."""
    enabled: bool
    initial_rating: int
    k_factor: int
    rating_floor: int

class ConfigManager:
    def __init__(self, config_dir: str):
        # ... existing ...
        self.elo: Optional[EloConfig] = None

    def load_league_config(self, filename: str = "league.yaml"):
        # ... existing ...

        # Parse ELO settings
        elo_data = data.get('elo', {})
        if elo_data.get('enabled', False):
            self.elo = EloConfig(
                enabled=True,
                initial_rating=elo_data.get('initial_rating', 1500),
                k_factor=elo_data.get('k_factor', 32),
                rating_floor=elo_data.get('rating_floor', 100)
            )
```

---

## 8. Testing Extensions

### 8.1 Testing New Games

Template for game tests:

```python
# tests/referee/test_<game_name>.py

import pytest
from src.referee.games.<game_name> import <GameClass>

class TestGameBasics:
    """Basic functionality tests."""

    def test_initialization(self):
        """Test game initializes correctly."""
        game = <GameClass>("match-1", ["player1", "player2"])
        assert not game.is_terminal()

    def test_valid_move(self):
        """Test valid move application."""
        game = <GameClass>("match-1", ["player1", "player2"])
        # Apply valid move
        # Assert state changed correctly

    def test_invalid_move(self):
        """Test invalid move detection."""
        game = <GameClass>("match-1", ["player1", "player2"])
        # Attempt invalid move
        with pytest.raises(ValidationError):
            game.make_move(...)

class TestGameTermination:
    """Terminal condition tests."""

    def test_win_condition(self):
        """Test win detection."""
        # Play sequence leading to win
        # Assert terminal and correct outcome

    def test_draw_condition(self):
        """Test draw detection."""
        # Play sequence leading to draw
        # Assert terminal and draw outcome

    def test_timeout(self):
        """Test timeout handling."""
        # Simulate timeout scenario

class TestGameState:
    """Game state tests."""

    def test_step_context(self):
        """Test step context generation."""
        game = <GameClass>("match-1", ["player1", "player2"])
        context = game.get_step_context("player1")
        assert 'valid_moves' in context

    def test_result_format(self):
        """Test result format."""
        game = <GameClass>("match-1", ["player1", "player2"])
        # Play to completion
        result = game.get_result()
        assert 'outcome' in result
        assert 'points' in result
```

### 8.2 Integration Testing

Test new extensions end-to-end:

```python
# tests/integration/test_new_game_integration.py

def test_full_league_with_new_game(league_manager, referee, players):
    """Test complete league workflow with new game."""
    # Register agents
    # Close registration
    # Run league
    # Verify all matches complete
    # Verify standings calculated correctly
```

---

## 9. Best Practices for Extensions

### 9.1 Design Principles

1. **Backward Compatibility**: New features should not break existing functionality
2. **Configuration Over Code**: Make extensions configurable without code changes
3. **Fail Gracefully**: Handle missing extensions without crashing
4. **Document Interfaces**: All extension points must be documented
5. **Test Coverage**: Extensions require >=90% test coverage

### 9.2 Checklist for Adding Extensions

- [ ] Interface is clearly defined and documented
- [ ] Implementation follows existing code style
- [ ] Configuration added to appropriate files
- [ ] Unit tests written with good coverage
- [ ] Integration tests verify end-to-end functionality
- [ ] Documentation updated (this file, README, etc.)
- [ ] Example usage provided
- [ ] Backward compatibility verified
- [ ] Error handling implemented
- [ ] Logging added for debugging

---

## 10. Common Extension Patterns

### 10.1 Observer Pattern

For adding monitoring and analytics:

```python
class MatchObserver:
    """Observer for match events."""

    def on_match_start(self, match_id, players):
        pass

    def on_move_made(self, match_id, player_id, move):
        pass

    def on_match_complete(self, match_id, result):
        pass

# Register observers
referee.add_observer(LoggingObserver())
referee.add_observer(MetricsObserver())
referee.add_observer(WebhookObserver(webhook_url))
```

### 10.2 Decorator Pattern

For adding cross-cutting concerns:

```python
def with_timing(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@with_timing
def make_move(self, player_id, move):
    # Original implementation
    pass
```

### 10.3 Factory Pattern

For creating configurable components:

```python
class GameFactory:
    """Factory for creating game instances."""

    _registry = {}

    @classmethod
    def register(cls, game_type: str, game_class: Type):
        cls._registry[game_type] = game_class

    @classmethod
    def create(cls, game_type: str, *args, **kwargs):
        game_class = cls._registry.get(game_type)
        if not game_class:
            raise ValueError(f"Unknown game type: {game_type}")
        return game_class(*args, **kwargs)

# Register games
GameFactory.register("tic_tac_toe", TicTacToeGame)
GameFactory.register("chess", ChessGame)

# Create game
game = GameFactory.create("tic_tac_toe", match_id, players)
```

---

## 11. Troubleshooting Extensions

### 11.1 Common Issues

**Issue**: Extension not loading

**Solution**: Check plugin path, import statements, and class inheritance

**Issue**: Configuration not recognized

**Solution**: Verify YAML syntax, restart league manager

**Issue**: Extension conflicts with existing code

**Solution**: Check for namespace collisions, review dependencies

### 11.2 Debugging Tips

1. Enable DEBUG logging
2. Check audit logs for protocol messages
3. Verify configuration is loaded correctly
4. Test extension in isolation first
5. Use integration tests to verify end-to-end

---

## 12. Summary

The Agent League System provides extensive extensibility through:

- **Game Engine Plugins**: Add new games by implementing the game interface
- **Protocol Extensions**: Add new message types and envelope fields
- **Scheduling Algorithms**: Implement custom tournament formats
- **Player Strategies**: Create intelligent or specialized strategies
- **Plugin Architecture**: Auto-discover and load extensions
- **Configuration**: Customize behavior without code changes

By following the patterns and guidelines in this document, developers can extend the system to support new games, features, and use cases while maintaining consistency, reliability, and backward compatibility.

---

**Document Version**: 1.0
**Last Updated**: 2025-12-21
**Status**: Production Ready
