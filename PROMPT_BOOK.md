# Prompt Book - Agent League System

## Document Overview

This guide provides example prompts and usage patterns for interacting with the Agent League System. Use these prompts as templates for common tasks and scenarios.

**Target Audience**: Users, developers, AI assistants
**Last Updated**: December 24, 2025

---

## Table of Contents

- [System Setup](#system-setup)
- [Player Operations](#player-operations)
- [Match Execution](#match-execution)
- [League Management](#league-management)
- [Tournament Operations](#tournament-operations)
- [Troubleshooting](#troubleshooting)
- [Development Prompts](#development-prompts)

---

## System Setup

### Starting the System

**Prompt**: "Start the Agent League System with default configuration"

**Expected Response**:
```
League Manager started on localhost:8000
Referee started on localhost:8001
System ready for player registration
```

**CLI Command**:
```bash
python -m src.league_manager.main &
python -m src.referee.main &
```

---

### Configuration Check

**Prompt**: "Show me the current system configuration"

**Expected Response**:
```
League Manager: localhost:8000
Referee: localhost:8001
Database: ./data/league.db
Default Game: tic_tac_toe
Max Concurrent Matches: 10
```

**CLI Command**:
```bash
# Check configuration
cat config.yaml | grep -A 5 "league_manager:"
```

---

## Player Operations

### Register a New Player

**Prompt**: "Register a new player with ID 'player-001' using the smart strategy"

**Expected Response**:
```
Player registered successfully
  Player ID: player-001
  Strategy: smart
  Status: active
  Registration time: 2025-12-24 10:30:00 UTC
```

**CLI Command**:
```bash
python -m src.player.main --register --player-id player-001 --strategy smart
```

**API Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "register_player",
  "params": {
    "player_id": "player-001",
    "strategy": "smart"
  },
  "id": "msg-001"
}
```

---

### Check Player Status

**Prompt**: "What is the status of player-001?"

**Expected Response**:
```
Player ID: player-001
Status: active
Games Played: 5
Wins: 3
Losses: 2
Win Rate: 60%
Current Ranking: 2nd place
```

**API Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "get_player_status",
  "params": {
    "player_id": "player-001"
  },
  "id": "msg-002"
}
```

---

### List All Players

**Prompt**: "Show me all registered players"

**Expected Response**:
```
Registered Players (5):
1. player-001 (smart) - active
2. player-002 (random) - active
3. player-003 (smart) - active
4. player-004 (random) - inactive
5. player-005 (smart) - active
```

**API Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "list_players",
  "params": {},
  "id": "msg-003"
}
```

---

## Match Execution

### Start a Single Match

**Prompt**: "Start a match between player-001 and player-002 playing tic-tac-toe"

**Expected Response**:
```
Match created
  Match ID: match-001
  Player 1: player-001 (X)
  Player 2: player-002 (O)
  Game: tic_tac_toe
  Status: in_progress
```

**API Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "create_match",
  "params": {
    "player1_id": "player-001",
    "player2_id": "player-002",
    "game_type": "tic_tac_toe"
  },
  "id": "msg-004"
}
```

---

### Check Match Status

**Prompt**: "What is the status of match-001?"

**Expected Response**:
```
Match ID: match-001
Status: completed
Winner: player-001
Final Board:
  X | O | X
  O | X | O
  O | X | X
Moves: 9
Duration: 2.3 seconds
```

**API Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "get_match_status",
  "params": {
    "match_id": "match-001"
  },
  "id": "msg-005"
}
```

---

### Get Match History

**Prompt**: "Show me the last 10 matches"

**Expected Response**:
```
Recent Matches:
1. match-010: player-003 vs player-005 → player-003 won
2. match-009: player-001 vs player-004 → player-001 won
3. match-008: player-002 vs player-005 → draw
...
```

---

## League Management

### Create a New League

**Prompt**: "Create a new league called 'Winter Championship' with tic-tac-toe"

**Expected Response**:
```
League created successfully
  League ID: league-001
  Name: Winter Championship
  Game: tic_tac_toe
  Status: registration_open
  Players: 0
```

**API Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "create_league",
  "params": {
    "league_name": "Winter Championship",
    "game_type": "tic_tac_toe"
  },
  "id": "msg-006"
}
```

---

### View League Standings

**Prompt**: "Show me the current standings for league-001"

**Expected Response**:
```
League: Winter Championship
Standings (as of 2025-12-24):

Rank | Player     | Points | Wins | Losses | Draws
-----|------------|--------|------|--------|------
  1  | player-003 |    9   |  3   |   0    |   0
  2  | player-001 |    6   |  2   |   1    |   0
  3  | player-005 |    3   |  1   |   2    |   0
  4  | player-002 |    1   |  0   |   2    |   1
  5  | player-004 |    0   |  0   |   3    |   0
```

**API Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "get_standings",
  "params": {
    "league_id": "league-001"
  },
  "id": "msg-007"
}
```

---

## Tournament Operations

### Start a Round-Robin Tournament

**Prompt**: "Start a round-robin tournament with all registered players"

**Expected Response**:
```
Tournament started
  League ID: league-001
  Format: round-robin
  Players: 5
  Total Rounds: 5
  Matches per Round: 2
  Total Matches: 10
  Estimated Duration: ~2 minutes
```

**API Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "start_tournament",
  "params": {
    "league_id": "league-001",
    "format": "round_robin"
  },
  "id": "msg-008"
}
```

---

### Check Tournament Progress

**Prompt**: "How far along is the tournament in league-001?"

**Expected Response**:
```
Tournament Progress:
  League: league-001
  Current Round: 3 of 5
  Completed Matches: 6 of 10 (60%)
  In Progress: 2
  Pending: 2
  Estimated Time Remaining: 45 seconds
```

---

### Get Round Schedule

**Prompt**: "Show me the match schedule for round 2"

**Expected Response**:
```
Round 2 Matches:
1. player-001 vs player-003 (pending)
2. player-002 vs player-004 (pending)
(player-005 has bye this round)
```

---

## Troubleshooting

### Connection Issues

**Prompt**: "I can't connect to the league manager. Help me troubleshoot."

**Expected Response**:
```
Troubleshooting Steps:
1. Check if league manager is running:
   $ ps aux | grep league_manager

2. Verify port 8000 is available:
   $ lsof -i :8000

3. Check logs:
   $ tail -f logs/agent_league.log

4. Test connection:
   $ curl http://localhost:8000/health

Common fixes:
- Restart league manager
- Check firewall settings
- Verify configuration in config.yaml
```

---

### Player Registration Fails

**Prompt**: "Player registration is failing with error 'invalid_params'. What should I check?"

**Expected Response**:
```
Error: invalid_params - Common Causes:

1. Player ID format:
   - Must be alphanumeric + hyphens
   - Example: player-001, team-alpha-1

2. Duplicate registration:
   - Check if player already registered
   - Use list_players to verify

3. Invalid strategy:
   - Allowed: random, smart, ai_powered
   - Check spelling

4. Missing authentication:
   - Ensure auth token is valid
   - Check AUTH_ENABLED in .env

Debug Command:
$ python -m src.player.main --register --player-id test-001 --strategy smart --debug
```

---

### Match Timeout

**Prompt**: "My match timed out. How can I increase the timeout?"

**Expected Response**:
```
Adjust Match Timeout:

1. In config.yaml:
   games:
     timeout_seconds: 60  # Increase from 30

2. Or via environment:
   export GAME_TIMEOUT_SECONDS=60

3. Per-match override (API):
   {
     "method": "create_match",
     "params": {
       "player1_id": "player-001",
       "player2_id": "player-002",
       "timeout": 60
     }
   }

Note: Timeouts prevent infinite loops. Consider optimizing strategy instead.
```

---

### Database Locked

**Prompt**: "I'm getting 'database is locked' errors. How do I fix this?"

**Expected Response**:
```
Database Lock Resolution:

1. Check for multiple processes:
   $ ps aux | grep "league_manager\|referee"
   Kill duplicates

2. Close stale connections:
   $ rm ./data/league.db-wal
   $ rm ./data/league.db-shm

3. Increase timeout in config.yaml:
   database:
     sqlite:
       timeout: 60  # Increase from 30

4. Switch to PostgreSQL for concurrent access (see docs/CONFIG.md)

Prevention:
- Only run one instance of each component
- Use connection pooling
- Close connections properly
```

---

## Development Prompts

### Adding a New Game

**Prompt**: "I want to add Connect Four as a new game. Walk me through the process."

**Expected Steps**:
```
1. Create game module:
   $ touch src/referee/games/connect_four.py

2. Implement GameReferee interface:
   - initialize_game()
   - validate_move()
   - execute_move()
   - check_game_over()
   - get_winner()

3. Add game configuration:
   In config.yaml:
   games:
     connect_four:
       board_width: 7
       board_height: 6
       win_condition: 4

4. Write tests:
   $ touch tests/referee/test_connect_four.py

5. Register game:
   Update src/referee/games/__init__.py

6. Test:
   $ pytest tests/referee/test_connect_four.py

See docs/EXTENSIBILITY.md for detailed guide.
```

---

### Running Tests

**Prompt**: "How do I run the test suite?"

**Expected Response**:
```
Run Tests:

# All tests
$ pytest tests/

# Specific module
$ pytest tests/common/

# With coverage
$ pytest tests/ --cov=src --cov-report=html

# Verbose output
$ pytest tests/ -v

# Stop on first failure
$ pytest tests/ -x

# Run specific test
$ pytest tests/common/test_protocol.py::TestEnvelope::test_envelope_creation

View coverage report:
$ open htmlcov/index.html
```

---

### Debugging a Failed Test

**Prompt**: "Test test_standings_tie_breaking_by_player_id is failing. How do I debug it?"

**Expected Steps**:
```
1. Run test with verbose output:
   $ pytest tests/league_manager/test_standings.py::TestStandingsEngine::test_standings_tie_breaking_by_player_id -vv

2. Add print statements:
   In src/league_manager/standings.py, add:
   print(f"Sorting players: {player_ids}")

3. Run with output capture disabled:
   $ pytest tests/... -s

4. Use debugger:
   Add: import pdb; pdb.set_trace()
   $ pytest tests/... -s

5. Check actual vs expected:
   Expected: ['alpha', 'beta', 'zebra']
   Actual: ['zebra', 'alpha', 'beta']
   → Issue: sorting order reversed

Fix: Check sort key in standings.py
```

---

## Advanced Usage

### Batch Operations

**Prompt**: "Register 10 players at once with different strategies"

**Example Script**:
```python
import requests

base_url = "http://localhost:8000/mcp"
for i in range(10):
    strategy = "smart" if i % 2 == 0 else "random"
    payload = {
        "jsonrpc": "2.0",
        "method": "register_player",
        "params": {
            "player_id": f"player-{i:03d}",
            "strategy": strategy
        },
        "id": f"batch-{i}"
    }
    response = requests.post(base_url, json=payload)
    print(f"Registered player-{i:03d}: {response.json()}")
```

---

### Custom Strategy

**Prompt**: "Create a custom player strategy that always plays center first in tic-tac-toe"

**Expected Implementation**:
```python
# src/player/strategies/center_first.py
from src.player.strategy import PlayerStrategy

class CenterFirstStrategy(PlayerStrategy):
    def get_move(self, game_state):
        board = game_state['board']

        # First move: always play center
        if sum(1 for row in board for cell in row if cell) == 0:
            return (1, 1)  # Center position

        # Subsequent moves: use smart strategy
        return self.find_best_move(board)

# Register in src/player/strategies/__init__.py
```

---

## Tips and Best Practices

1. **Always check system status before starting tournament**
2. **Use meaningful player IDs** (e.g., "team-alpha-player1" not "p1")
3. **Monitor logs** during tournaments for errors
4. **Test custom strategies** with small matches first
5. **Back up database** before major operations
6. **Use configuration files** instead of hardcoding values
7. **Implement timeouts** to prevent infinite loops
8. **Handle errors gracefully** in custom code

---

## Common Patterns

### Pattern: Retry on Failure

```python
import time

def register_with_retry(player_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = register_player(player_id)
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Pattern: Batch Processing

```python
def process_tournament_results(league_id):
    standings = get_standings(league_id)
    for rank, player in enumerate(standings, 1):
        notify_player(player, rank)
        update_statistics(player, league_id)
        if rank == 1:
            award_trophy(player)
```

---

## Glossary

- **League**: A competition with multiple players
- **Match**: Single game between two players
- **Round**: Set of concurrent matches
- **Tournament**: Complete series of matches following a format
- **Strategy**: Algorithm that decides player moves
- **Referee**: Component that enforces game rules

---

**Need more help?** See:
- Full documentation: `docs/`
- API reference: `docs/API.md`
- Contributing guide: `docs/CONTRIBUTING.md`
- Examples: `examples/`

**Last Updated**: December 24, 2025
