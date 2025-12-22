# ADR-003: Game-Agnostic Referee Pattern

## Status
Accepted

## Context
The Agent League System must support multiple game types without modifying the core league logic. The PRD explicitly states that the league is "game-agnostic" (Section 1, Section 5):

Key requirements:
1. **Separation of concerns**: League Manager handles coordination; game logic is elsewhere
2. **Extensibility**: New games can be added without changing League Manager code
3. **Protocol stability**: Adding a game must not require protocol changes
4. **Referee authority**: Match execution and game rules are controlled by referees
5. **Opaque payloads**: League protocol treats game-specific data as black boxes

The system must answer a fundamental architectural question: **Who executes game logic, and where does it live?**

Options considered:
- Embed game logic in League Manager (monolithic)
- Embed game logic in players (distributed)
- Delegate game logic to specialized referee agents (delegated authority)

The choice affects extensibility, maintainability, testing, and the ability to add new games dynamically.

## Decision
We will delegate all game-specific logic to autonomous Referee agents, making the League Manager completely game-agnostic.

The architecture enforces strict separation:
- **League Manager**: Coordinates registration, scheduling, standings (zero game knowledge)
- **Referee Agents**: Execute matches, enforce game rules, validate moves (full game knowledge)
- **Player Agents**: Respond to move requests (game-specific strategies, but no rule enforcement)

Game-specific logic (move validation, state advancement, win conditions) is encapsulated entirely within referee implementations. The league protocol treats game data as opaque payloads.

## Rationale

### Separation of Concerns
This pattern cleanly separates:
- **League coordination** (scheduling, standings, authentication) → League Manager
- **Game execution** (rules, validation, state) → Referees
- **Strategy** (decision-making, learning) → Players

Benefits:
- League Manager code is stable (changes only for league-level features)
- Game-specific code is isolated (bugs in one game don't affect others)
- Testing is modular (unit test games independently of league)
- Maintenance is focused (game developers don't touch league logic)

### Extensibility Without Code Changes
Adding a new game requires:
1. Implement a new Referee class (game-specific logic)
2. Add entry to `game_registry.yaml` (configuration)
3. Deploy referee instances

No changes needed to:
- League Manager code
- Protocol specification
- Database schema (game_metadata is opaque JSON)
- Player interface (players receive opaque step_context and submit opaque move_payload)

This enables:
- Third-party game development (game designers can contribute referees)
- Rapid experimentation (try new games without league downtime)
- Versioning (multiple versions of same game can coexist)

### Referee as Authoritative Source of Truth
Referees have final authority over match outcomes because:
- They enforce game rules (League Manager cannot validate game moves)
- They observe complete game state (League Manager sees only results)
- They detect rule violations and cheating (players cannot dispute referee decisions)

This authority model mirrors real-world sports:
- League organizers schedule games and track standings
- Referees/umpires control in-game decisions
- Players compete but do not judge themselves

### Protocol-Level Opacity
The league protocol treats game data as opaque:

**Opaque to League Manager**:
- `step_context` (game state summary sent to players)
- `move_payload` (player move submission)
- `game_metadata` (referee's outcome explanation)

**Visible to League Manager**:
- `game_type` (identifier for routing and registry lookup)
- `outcome` (win/loss/draw per player)
- `points` (numerical score per player)

This enables:
- **Protocol stability**: Adding games with new move formats doesn't change protocol
- **Privacy**: Game-specific details aren't exposed to league logs (if desired)
- **Flexibility**: Games can have radically different move structures (turn-based, simultaneous, multi-phase)

### Referee Implementation Flexibility
Referees can be implemented in different ways:
- **Built-in game engines**: Referee embeds complete game logic (e.g., chess engine)
- **Rule-based validators**: Referee validates moves against declarative rules (e.g., JSON schema)
- **External integrations**: Referee delegates to external game servers (e.g., OpenAI Gym)

The league doesn't care how referees implement games, only that they:
- Accept match assignments
- Invite players
- Request and validate moves
- Report final results

### Concurrent Match Execution
Multiple referees can operate concurrently, each executing different matches:
- Referees are independent processes (no shared state)
- Each referee handles one match at a time (enforced by protocol)
- League Manager assigns matches to available referees

This enables:
- **Parallelism**: Matches execute simultaneously (limited by referee count)
- **Fault isolation**: Referee crash affects only one match
- **Load balancing**: Distribute matches across referee pool

### Testability
Game logic can be tested independently:
- **Unit tests**: Test referee game logic without League Manager
- **Integration tests**: Test referee-player interaction without full league
- **End-to-end tests**: Test complete league with mock referees and players

Mocking is straightforward:
- Mock referees for testing League Manager (return fixed results)
- Mock players for testing referees (submit predetermined moves)
- Mock League Manager for testing registration flow

## Consequences

### Positive
1. **League Manager simplicity**: Zero game-specific code, easier to maintain and verify
2. **Rapid game addition**: New games deployed without touching core system
3. **Independent development**: Game developers work in isolation from league developers
4. **Fault isolation**: Game bugs don't crash league; referee crash affects one match
5. **Scalability**: Add more referee instances to increase concurrent match capacity
6. **Flexibility**: Games can use different move formats, state representations, rule systems
7. **Clear authority**: Referee decisions are final, simplifying dispute resolution
8. **Protocol stability**: Opaque payloads prevent protocol churn
9. **Testability**: Modular testing of league, game, and strategy components
10. **Security**: Referees validate moves (players cannot cheat by submitting invalid moves)

### Negative
1. **Referee deployment complexity**: Each game type requires referee instances to be running
2. **Referee availability**: If no referee is available for a game type, matches cannot start
3. **Debugging difficulty**: Multi-process architecture complicates debugging (distributed traces needed)
4. **Performance overhead**: HTTP calls between processes add latency vs. in-process game logic
5. **Referee trust**: Players must trust referee implementations (no independent verification)
6. **Resource usage**: Multiple referee processes consume more memory/CPU than in-process game logic
7. **Configuration burden**: Game registry must be maintained and kept in sync across deployments

### Neutral
1. **Protocol verbosity**: Opaque payloads may contain redundant data (referee and player both track state)
2. **State synchronization**: Players must maintain their own game state (referee doesn't re-send full history)
3. **Error reporting**: Game-specific errors must be translated to league protocol errors
4. **Referee heterogeneity**: Different games may have different quality referees (some well-tested, others experimental)

## Implementation Notes

### Referee Interface Contract
All referees must implement:
```python
class RefereeInterface:
    def accept_match_assignment(self, match_id, round_id, players, game_type):
        """Accept assignment from League Manager"""
        pass

    def invite_players(self, match_id, players):
        """Send GAME_INVITATION to players"""
        pass

    def execute_match(self, match_id):
        """
        Run game loop:
        1. Wait for player join acknowledgements
        2. Loop: request moves, validate, advance state
        3. Detect terminal condition
        4. Compute outcome and points
        """
        pass

    def report_result(self, match_id, outcome, points, metadata):
        """Send MATCH_RESULT_REPORT to League Manager"""
        pass
```

### Game Engine Abstraction
Referees should separate protocol handling from game logic:
```python
class GenericReferee:
    def __init__(self, game_engine):
        self.game_engine = game_engine  # Game-specific engine

    def execute_match(self, match_id):
        # Protocol handling (game-agnostic)
        self.invite_players(match_id)
        self.wait_for_join_acks()

        while not self.game_engine.is_terminal():
            # Request move (game-agnostic)
            step_context = self.game_engine.get_step_context()
            move = self.request_move(current_player, step_context)

            # Validate move (game-specific)
            if not self.game_engine.validate_move(move):
                raise InvalidMoveError()

            # Advance state (game-specific)
            self.game_engine.apply_move(move)

        # Compute outcome (game-specific)
        outcome, points = self.game_engine.get_outcome()
        self.report_result(match_id, outcome, points)
```

### Game Engine Interface
Each game implements a game engine interface:
```python
class GameEngineInterface:
    def initialize(self, players):
        """Set up initial game state"""
        pass

    def get_step_context(self, player):
        """Return opaque step context for player (current state summary)"""
        pass

    def validate_move(self, move_payload):
        """Return True if move is legal, False otherwise"""
        pass

    def apply_move(self, move_payload):
        """Update game state with player's move"""
        pass

    def is_terminal(self):
        """Return True if game has ended, False otherwise"""
        pass

    def get_outcome(self):
        """Return (outcome_dict, points_dict)"""
        pass
```

### Example: Even/Odd Game Engine
```python
class EvenOddGameEngine(GameEngineInterface):
    def initialize(self, players):
        self.players = players
        self.moves = {}
        self.step = 0

    def get_step_context(self, player):
        return {"step": self.step, "action": "predict_even_or_odd"}

    def validate_move(self, move_payload):
        return move_payload.get("prediction") in ["even", "odd"]

    def apply_move(self, move_payload):
        player = move_payload["player"]
        self.moves[player] = move_payload["prediction"]

    def is_terminal(self):
        return len(self.moves) == 2

    def get_outcome(self):
        # Game-specific logic: random number determines winner
        import random
        number = random.randint(1, 100)
        parity = "even" if number % 2 == 0 else "odd"

        winner = [p for p in self.players if self.moves[p] == parity][0]
        loser = [p for p in self.players if p != winner][0]

        outcome = {winner: "win", loser: "loss"}
        points = {winner: 3, loser: 0}
        return outcome, points
```

### Game Registry Configuration
```yaml
games:
  - game_type: "even_odd"
    name: "Even/Odd Prediction"
    referee_implementation: "src.referee.games.even_odd.EvenOddReferee"
    scoring:
      win: 3
      draw: 1
      loss: 0
    config:
      # Game-specific config (opaque to league)
      random_seed: null  # null = random, int = deterministic
```

### Referee Deployment
Referees are deployed as separate processes:
```bash
# Start referee for even/odd game
python -m src.referee.main \
  --game-type even_odd \
  --port 8001 \
  --league-manager-url http://localhost:8000/mcp

# Start another referee instance for same game (concurrency)
python -m src.referee.main \
  --game-type even_odd \
  --port 8002 \
  --league-manager-url http://localhost:8000/mcp

# Start referee for different game
python -m src.referee.main \
  --game-type rock_paper_scissors \
  --port 8003 \
  --league-manager-url http://localhost:8000/mcp
```

### League Manager Game Registry Lookup
```python
class LeagueManager:
    def assign_match(self, match):
        game_type = match.game_type
        available_referees = self.get_available_referees(game_type)

        if not available_referees:
            raise NoRefereeAvailableError(f"No referee for {game_type}")

        referee = available_referees[0]
        self.send_match_assignment(referee, match)
```

### Opaque Payload Examples

**Step Context** (referee → player):
```json
{
  "step_context": {
    "board": [[" ", " ", " "], ["X", "O", " "], [" ", " ", " "]],
    "your_symbol": "X",
    "legal_moves": [[0, 0], [0, 1], [0, 2], [1, 2], [2, 0], [2, 1], [2, 2]]
  }
}
```

**Move Payload** (player → referee):
```json
{
  "move_payload": {
    "row": 0,
    "col": 1
  }
}
```

**Game Metadata** (referee → League Manager):
```json
{
  "game_metadata": {
    "total_turns": 5,
    "winning_move": {"row": 0, "col": 1},
    "final_board": [[" ", "X", " "], ["X", "O", " "], [" ", " ", " "]],
    "note": "Player A won with horizontal line"
  }
}
```

League Manager stores these as opaque JSON blobs.

### Referee Crash Recovery
If a referee crashes mid-match:
1. League Manager detects timeout on result report
2. Match is marked as FAILED
3. League Manager assigns match to different referee (if configured for retries)
4. Players are notified of match cancellation
5. Incident is logged for review

### Validation Responsibilities
- **Referee validates**: Move legality, game rule compliance, win conditions
- **League Manager validates**: Protocol structure, authentication, authorization, duplicate results
- **Player validates**: Nothing (players trust referee, but can log disputes)

## Alternatives Considered

### Alternative 1: Game Logic in League Manager (Monolithic)
- **Description**: Embed all game engines in League Manager process
- **Pros**:
  - Simpler deployment (single process)
  - Lower latency (in-process function calls)
  - Easier debugging (single process to debug)
  - Shared state (no serialization overhead)
- **Cons**:
  - League Manager code changes for every new game (violates open/closed principle)
  - Game bugs can crash entire league (fault coupling)
  - No concurrency (single process bottleneck)
  - Testing complexity (cannot test games independently)
  - Monolithic binary grows with each game
  - Violates PRD separation of concerns (Section 1.2)
- **Reason for rejection**: Violates game-agnostic requirement. Makes League Manager complex and fragile.

### Alternative 2: Game Logic in Players (Distributed Validation)
- **Description**: Players validate each other's moves via consensus
- **Pros**:
  - No referee needed (pure peer-to-peer)
  - Decentralized (no single point of failure)
  - Players cannot cheat if majority validates
- **Cons**:
  - Requires complex consensus protocol (Byzantine fault tolerance)
  - Players must implement game rules (duplicates code across all players)
  - Cheating players can collude (majority attack)
  - Slow (network round-trips for every move validation)
  - Difficult to add new games (all players must update)
  - Violates PRD hub-and-spoke model (Section 1.3)
- **Reason for rejection**: Too complex. Players should focus on strategy, not rule enforcement.

### Alternative 3: Shared Game Engine Library (Linked)
- **Description**: League Manager, referees, and players all link to shared game engine libraries
- **Pros**:
  - Code reuse (single implementation of game rules)
  - Players can simulate moves locally (no network calls)
  - Faster validation (in-process)
- **Cons**:
  - Tight coupling (all agents must use same library version)
  - Players can cheat by modifying library (no authoritative validation)
  - Difficult to support heterogeneous agents (different languages)
  - Version skew problems (mismatched libraries produce different results)
  - Violates referee authority principle
- **Reason for rejection**: Coupling prevents independent agent development. Enables cheating.

### Alternative 4: External Game Server (Microservice)
- **Description**: League Manager calls external game server API for move validation
- **Pros**:
  - Game logic is external to league (separation of concerns)
  - Can use existing game servers (e.g., OpenAI Gym, Lichess API)
  - Language-agnostic (game server can be in any language)
- **Cons**:
  - Requires external service deployment (operational complexity)
  - Network latency for every move validation
  - Single point of failure (if game server crashes, all matches fail)
  - External dependency (versioning, availability SLAs)
  - Doesn't support multiple game types (unless multiple services)
- **Reason for rejection**: Similar benefits to referee pattern but with external dependency and single point of failure. Referee pattern is more self-contained.

### Alternative 5: Declarative Game Rules (DSL/JSON Schema)
- **Description**: Define games declaratively (JSON schema for moves, state transitions)
- **Pros**:
  - No code for simple games (configuration-driven)
  - Easy to add trivial games (rock-paper-scissors, coin flip)
  - Validation is automated (schema validation)
- **Cons**:
  - Limited expressiveness (complex games require Turing-complete logic)
  - DSL complexity (learning curve, tooling needed)
  - Debugging difficulty (declarative errors are cryptic)
  - Performance (interpreted rules slower than compiled code)
  - Doesn't eliminate need for game-specific code (just changes language)
- **Reason for rejection**: Solves only simple games. Complex games (chess, Go) require full programming language.

## References
- [PRD Section 1: League Scope, Actors, and Responsibilities](../prd/section-1-scope-and-actors.md)
- [PRD Section 5: Match Execution and Game Abstraction](../prd/section-5-match-execution.md)
- [PRD Section 9: Configuration and Extensibility](../prd/section-9-configuration-and-extensibility.md)
- [Architecture Documentation - Component Diagrams](../Architecture.md#24-level-3-component-diagram---referee-agent)
- [Architecture Documentation - Match Execution Flow](../Architecture.md#33-match-execution-flow-game-agnostic)
- [Diagram: match-execution-flow.md](../diagrams/match-execution-flow.md)

## Metadata
- **Author**: architecture-author agent
- **Date**: 2025-01-21
- **Status**: Accepted
- **Related ADRs**:
  - [ADR-001: JSON-RPC Transport](001-json-rpc-transport.md) (referees use JSON-RPC for communication)
  - [ADR-002: Round-Robin Scheduling](002-round-robin-scheduling.md) (scheduling is game-agnostic)
- **Related PRD Sections**:
  - Section 1.2: Actors (defines referee responsibilities)
  - Section 5: Match Execution and Game Abstraction
  - Section 9: Configuration and Extensibility
