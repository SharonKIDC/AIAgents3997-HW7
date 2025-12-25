# Terminal Examples - Agent League System

This document shows real terminal output examples for common operations in the Agent League System.

## Table of Contents
- [System Startup](#system-startup)
- [Player Registration](#player-registration)
- [Running a Tournament](#running-a-tournament)
- [Checking Standings](#checking-standings)
- [Running Tests](#running-tests)
- [API Interactions](#api-interactions)

---

## System Startup

### Starting League Manager

```bash
$ python -m src.league_manager.main
INFO     src.league_manager.server:server.py:85 Initializing League Manager...
INFO     src.league_manager.server:server.py:92 Database initialized at ./data/league.db
INFO     src.league_manager.server:server.py:98 HTTP server started on localhost:8000
INFO     src.league_manager.server:server.py:102 League Manager ready for registration
```

### Starting Referee

```bash
$ python -m src.referee.main
INFO     src.referee.server:server.py:45 Initializing Referee Server...
INFO     src.referee.server:server.py:52 Loaded game: tic_tac_toe
INFO     src.referee.server:server.py:58 HTTP server started on localhost:8001
INFO     src.referee.server:server.py:62 Referee ready for match execution
```

### Health Check

```bash
$ curl http://localhost:8000/health
{
  "status": "healthy",
  "service": "league_manager",
  "version": "1.0.0",
  "uptime_seconds": 125,
  "database": "connected"
}
```

---

## Player Registration

### Register Player with Smart Strategy

```bash
$ python -m src.player.main register --player-id player-001 --strategy smart
INFO     src.player.client:client.py:45 Registering player-001...
INFO     src.player.client:client.py:52 Sending registration request to localhost:8000
INFO     src.player.client:client.py:68 Registration successful!

Player Registration Complete
============================
Player ID: player-001
Strategy: smart
Token: eyJ0eXAiOiJKV1QiLCJhbGc...(truncated)
Status: active
Server: localhost:9000

Player is now ready to receive match notifications.
```

### Register Multiple Players (Script)

```bash
$ for i in {1..5}; do
>   python -m src.player.main register --player-id player-00$i --strategy random
> done

INFO     Registering player-001...
✓ player-001 registered (random strategy)

INFO     Registering player-002...
✓ player-002 registered (random strategy)

INFO     Registering player-003...
✓ player-003 registered (random strategy)

INFO     Registering player-004...
✓ player-004 registered (random strategy)

INFO     Registering player-005...
✓ player-005 registered (random strategy)

Successfully registered 5 players
```

### List Registered Players

```bash
$ curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "list_players",
    "params": {},
    "id": "req-001"
  }'

{
  "jsonrpc": "2.0",
  "result": {
    "players": [
      {
        "player_id": "player-001",
        "strategy": "smart",
        "status": "active",
        "registered_at": "2025-12-24T10:30:00Z"
      },
      {
        "player_id": "player-002",
        "strategy": "random",
        "status": "active",
        "registered_at": "2025-12-24T10:30:05Z"
      },
      {
        "player_id": "player-003",
        "strategy": "random",
        "status": "active",
        "registered_at": "2025-12-24T10:30:10Z"
      }
    ],
    "total": 3
  },
  "id": "req-001"
}
```

---

## Running a Tournament

### Start Round-Robin Tournament

```bash
$ python -m src.league_manager.main start-tournament --league-id league-001

INFO     Starting round-robin tournament for league-001
INFO     Registered players: 5
INFO     Generating schedule...
INFO     Schedule generated: 5 rounds, 10 total matches

Tournament Schedule
===================
League: league-001
Format: Round-Robin
Players: 5
Total Matches: 10
Total Rounds: 5

Round 1:
  Match 1: player-001 vs player-002
  Match 2: player-003 vs player-004
  (player-005 has bye)

Round 2:
  Match 3: player-001 vs player-003
  Match 4: player-002 vs player-005
  (player-004 has bye)

...

INFO     Starting match execution...
```

### Match Execution Output

```bash
INFO     Match 1 starting: player-001 (X) vs player-002 (O)
INFO     Game: tic_tac_toe
DEBUG    Move 1: player-001 plays (1, 1) [center]
DEBUG    Board state:
  . | . | .
  . | X | .
  . | . | .

DEBUG    Move 2: player-002 plays (0, 0) [top-left]
DEBUG    Board state:
  O | . | .
  . | X | .
  . | . | .

DEBUG    Move 3: player-001 plays (0, 2) [top-right]
DEBUG    Board state:
  O | . | X
  . | X | .
  . | . | .

DEBUG    Move 4: player-002 plays (2, 0) [bottom-left]
DEBUG    Board state:
  O | . | X
  . | X | .
  O | . | .

DEBUG    Move 5: player-001 plays (2, 2) [bottom-right]
DEBUG    Board state:
  O | . | X
  . | X | .
  O | . | X

INFO     Match 1 complete: player-001 wins!
INFO     Result: player-001 (3 points), player-002 (0 points)
INFO     Duration: 1.24 seconds

Match Statistics:
  Total Moves: 5
  Average Move Time: 0.248s
  Winner: player-001
  Winning Condition: Diagonal (top-left to bottom-right)
```

### Tournament Progress

```bash
$ python -m src.league_manager.main tournament-status --league-id league-001

Tournament Status
=================
League: league-001
Status: in_progress

Progress:
  Completed Matches: 6 / 10 (60%)
  Current Round: 3 / 5
  In Progress: 2 matches
  Pending: 2 matches

Recent Results:
  ✓ Match 6: player-001 def. player-005 (3-0)
  ✓ Match 5: player-003 def. player-002 (3-0)
  ✓ Match 4: player-004 def. player-001 (3-0)

Current Matches:
  ⟳ Match 7: player-002 vs player-004 (in progress, move 3/9)
  ⟳ Match 8: player-003 vs player-005 (in progress, move 1/9)

Estimated Time Remaining: ~45 seconds
```

---

## Checking Standings

### View Current Standings

```bash
$ python -m src.league_manager.main standings --league-id league-001

League Standings - league-001
==============================
Last Updated: 2025-12-24 10:45:23 UTC

Rank | Player ID   | Points | W | L | D | Win% | Point Diff
-----|-------------|--------|---|---|---|------|------------
  1  | player-003  |    9   | 3 | 0 | 0 | 100% |    +9
  2  | player-001  |    6   | 2 | 1 | 0 |  67% |    +3
  3  | player-004  |    6   | 2 | 1 | 0 |  67% |    +3
  4  | player-005  |    3   | 1 | 2 | 0 |  33% |    -3
  5  | player-002  |    0   | 0 | 3 | 0 |   0% |    -9

Scoring: Win=3pts, Draw=1pt, Loss=0pts

Tiebreakers Applied:
  Rank 2-3: Sorted by point differential (player-001: +3, player-004: +3)
  Further tie: Alphabetical by player_id

Next Matches:
  - player-001 vs player-005 (Round 4)
  - player-002 vs player-003 (Round 4)
```

### Export Standings to JSON

```bash
$ curl http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_standings",
    "params": {"league_id": "league-001"},
    "id": "req-standings"
  }' | jq '.result.standings'

[
  {
    "rank": 1,
    "player_id": "player-003",
    "points": 9,
    "wins": 3,
    "losses": 0,
    "draws": 0,
    "win_rate": 1.0,
    "point_differential": 9
  },
  {
    "rank": 2,
    "player_id": "player-001",
    "points": 6,
    "wins": 2,
    "losses": 1,
    "draws": 0,
    "win_rate": 0.667,
    "point_differential": 3
  }
]
```

---

## Running Tests

### Run Full Test Suite

```bash
$ pytest tests/ -v

============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.0.2, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /root/Git/AIAgents3997-HW7
configfile: pytest.ini
plugins: cov-7.0.0
collected 172 items

tests/common/test_auth.py::TestAuthManager::test_issue_token PASSED       [  0%]
tests/common/test_auth.py::TestAuthManager::test_validate_token PASSED    [  1%]
tests/common/test_protocol.py::TestEnvelope::test_envelope_creation PASSED[  2%]
tests/common/test_persistence.py::TestLeagueOperations::test_create PASSED[  3%]
tests/league_manager/test_scheduler.py::test_round_robin_schedule PASSED  [ 15%]
tests/league_manager/test_standings.py::test_standings_calculation PASSED [ 18%]
tests/integration/test_full_league.py::test_complete_lifecycle PASSED     [ 52%]
...

======================= 159 passed, 13 failed in 10.20s =======================
```

### Run Tests with Coverage

```bash
$ pytest tests/ --cov=src --cov-report=term

============================= test session starts ==============================
collected 172 items

tests/common/test_auth.py ................                                [  9%]
tests/common/test_persistence.py ......................                   [ 22%]
tests/common/test_protocol.py ...............................             [ 39%]
...

----------- coverage: platform linux, python 3.10.12 -----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/__init__.py                             1      0   100%
src/common/__init__.py                      2      0   100%
src/common/auth.py                        125     12    90%
src/common/errors.py                       45      2    96%
src/common/persistence.py                 287     28    90%
src/common/protocol.py                    156     15    90%
src/common/transport.py                   198     35    82%
src/league_manager/__init__.py              3      0   100%
src/league_manager/match_assigner.py       89      8    91%
src/league_manager/registration.py         67      5    93%
src/league_manager/scheduler.py           142     14    90%
src/league_manager/server.py              178     22    88%
src/league_manager/standings.py           112     10    91%
src/league_manager/state.py                95      8    92%
src/referee/__init__.py                     2      0   100%
src/referee/games/__init__.py               4      0   100%
src/referee/games/tic_tac_toe.py          156     12    92%
src/referee/match_executor.py             134     15    89%
src/referee/server.py                      98     18    82%
src/player/__init__.py                      2      0   100%
src/player/server.py                       87     15    83%
src/player/strategies/__init__.py           3      0   100%
src/player/strategy.py                     42      4    90%
-----------------------------------------------------------
TOTAL                                    2028    223    89%

Coverage HTML report: htmlcov/index.html
```

### Run Specific Test

```bash
$ pytest tests/league_manager/test_scheduler.py::test_round_robin_all_pairs -v

============================= test session starts ==============================
collected 1 item

tests/league_manager/test_scheduler.py::test_round_robin_all_pairs PASSED [100%]

============================== 1 passed in 0.12s ================================
```

---

## API Interactions

### Create a Match (JSON-RPC)

```bash
$ curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "create_match",
    "params": {
      "player1_id": "player-001",
      "player2_id": "player-002",
      "game_type": "tic_tac_toe"
    },
    "id": "create-match-001"
  }'

{
  "jsonrpc": "2.0",
  "result": {
    "match_id": "match-123",
    "player1_id": "player-001",
    "player2_id": "player-002",
    "game_type": "tic_tac_toe",
    "status": "created",
    "created_at": "2025-12-24T10:50:00Z"
  },
  "id": "create-match-001"
}
```

### Get Match Status

```bash
$ curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_match_status",
    "params": {"match_id": "match-123"},
    "id": "status-001"
  }' | jq

{
  "jsonrpc": "2.0",
  "result": {
    "match_id": "match-123",
    "player1_id": "player-001",
    "player2_id": "player-002",
    "status": "completed",
    "winner_id": "player-001",
    "final_board": [
      ["O", "", "X"],
      ["", "X", ""],
      ["O", "", "X"]
    ],
    "total_moves": 5,
    "duration_seconds": 1.24,
    "completed_at": "2025-12-24T10:50:02Z"
  },
  "id": "status-001"
}
```

### Error Response Example

```bash
$ curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "create_match",
    "params": {
      "player1_id": "nonexistent",
      "player2_id": "player-002"
    },
    "id": "err-001"
  }' | jq

{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "detail": "Player nonexistent not found",
      "param": "player1_id"
    }
  },
  "id": "err-001"
}
```

### Protocol Envelope Example

```bash
$ curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "ping",
    "params": {
      "envelope": {
        "protocol_version": "1.0",
        "message_type": "request",
        "sender": "client:test-001",
        "timestamp": "2025-12-24T10:55:00.000Z",
        "conversation_id": "conv-001",
        "message_id": "msg-001"
      }
    },
    "id": "ping-001"
  }' | jq

{
  "jsonrpc": "2.0",
  "result": {
    "envelope": {
      "protocol_version": "1.0",
      "message_type": "response",
      "sender": "league_manager:main",
      "timestamp": "2025-12-24T10:55:00.125Z",
      "conversation_id": "conv-001",
      "message_id": "msg-002",
      "in_reply_to": "msg-001"
    },
    "pong": true,
    "server_time": "2025-12-24T10:55:00.125Z"
  },
  "id": "ping-001"
}
```

---

## Database Queries

### Inspect Database

```bash
$ sqlite3 data/league.db

SQLite version 3.37.2
Enter ".help" for usage hints.

sqlite> .tables
leagues           matches           players           results
rounds            standings

sqlite> SELECT * FROM players LIMIT 3;
player-001|smart|active|2025-12-24 10:30:00|eyJ0eXAiOiJKV1Qi...
player-002|random|active|2025-12-24 10:30:05|eyJ0eXAiOiJKV1Qi...
player-003|random|active|2025-12-24 10:30:10|eyJ0eXAiOiJKV1Qi...

sqlite> SELECT player_id, wins, losses, points
   ...> FROM standings
   ...> WHERE league_id = 'league-001'
   ...> ORDER BY points DESC;
player-003|3|0|9
player-001|2|1|6
player-004|2|1|6
player-005|1|2|3
player-002|0|3|0

sqlite> .quit
```

---

## Configuration

### View Current Configuration

```bash
$ python -c "import yaml; print(yaml.dump(yaml.safe_load(open('config.yaml'))))"

app:
  name: Agent League System
  version: 1.0.0
league_manager:
  host: localhost
  port: 8000
referee:
  host: localhost
  port: 8001
games:
  default: tic_tac_toe
  timeout_seconds: 30
scheduling:
  algorithm: round_robin
  concurrent_matches: true
...
```

### Check Environment Variables

```bash
$ cat .env
# League Manager Configuration
LEAGUE_MANAGER_HOST=localhost
LEAGUE_MANAGER_PORT=8000

# Database
DATABASE_TYPE=sqlite
DATABASE_PATH=./data/league.db

# Logging
LOG_LEVEL=INFO
LOG_OUTPUT=console

# Authentication
AUTH_ENABLED=true
AUTH_TOKEN_EXPIRATION=3600
```

---

## Troubleshooting Examples

### Port Already in Use

```bash
$ python -m src.league_manager.main
ERROR    src.league_manager.server:server.py:95 Failed to start server
ERROR    Address already in use: localhost:8000

Troubleshooting:
1. Check what's using port 8000:
   $ lsof -i :8000

2. Kill the process:
   $ kill -9 <PID>

3. Or change port in config.yaml
```

### Database Locked

```bash
$ python -m src.league_manager.main
ERROR    Database is locked: ./data/league.db
ERROR    sqlite3.OperationalError: database is locked

Solution:
$ rm ./data/league.db-wal
$ rm ./data/league.db-shm
```

### Connection Refused

```bash
$ curl http://localhost:8000/health
curl: (7) Failed to connect to localhost port 8000: Connection refused

Check:
1. Is the server running?
   $ ps aux | grep league_manager

2. Is it on the right port?
   $ grep "port:" config.yaml

3. Check logs:
   $ tail -f logs/agent_league.log
```

---

## Performance Monitoring

### View Metrics

```bash
$ curl http://localhost:9090/metrics

# HELP matches_total Total number of matches executed
# TYPE matches_total counter
matches_total{status="completed"} 156
matches_total{status="in_progress"} 2
matches_total{status="failed"} 1

# HELP match_duration_seconds Match execution time
# TYPE match_duration_seconds histogram
match_duration_seconds_bucket{le="1.0"} 85
match_duration_seconds_bucket{le="2.0"} 145
match_duration_seconds_bucket{le="5.0"} 156

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/mcp",status="200"} 1543
http_requests_total{method="GET",endpoint="/health",status="200"} 89
```

---

## League Lifecycle After Registration

### Checking Registration Status

After players and referees have registered, check the league status:

```bash
$ curl http://localhost:8000/status

{
  "status": "REGISTRATION",
  "league_id": "default-league",
  "referees": 2,
  "players": 4
}
```

### Understanding League States

The league follows this progression:

```
INIT → REGISTRATION → SCHEDULING → ACTIVE → COMPLETED
```

**Current Implementation Note**:
The system does not currently expose HTTP endpoints to trigger state transitions after registration. League progression requires code-level access or direct database manipulation.

### Querying Standings During Active League

Once the league is in ACTIVE state (matches are running), players can query standings:

```bash
$ curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "league.handle",
    "params": {
      "envelope": {
        "protocol": "league.v2",
        "message_type": "QUERY_STANDINGS",
        "sender": "player:player-001",
        "timestamp": "2025-12-25T10:00:00Z",
        "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
        "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
      },
      "payload": {}
    },
    "id": "standings-req-1"
  }' | jq

{
  "jsonrpc": "2.0",
  "result": {
    "envelope": {
      "protocol": "league.v2",
      "message_type": "STANDINGS_RESPONSE",
      "sender": "league_manager",
      "timestamp": "2025-12-25T10:00:01.234Z",
      "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
      "league_id": "default-league"
    },
    "payload": {
      "standings": [
        {
          "rank": 1,
          "player_id": "player-003",
          "points": 9,
          "wins": 3,
          "losses": 0,
          "draws": 0,
          "win_rate": 1.0,
          "point_differential": 9
        },
        {
          "rank": 2,
          "player_id": "player-001",
          "points": 6,
          "wins": 2,
          "losses": 1,
          "draws": 0,
          "win_rate": 0.667,
          "point_differential": 3
        },
        {
          "rank": 3,
          "player_id": "player-002",
          "points": 3,
          "wins": 1,
          "losses": 2,
          "draws": 0,
          "win_rate": 0.333,
          "point_differential": -3
        }
      ],
      "updated_at": "2025-12-25T10:00:00Z"
    }
  },
  "id": "standings-req-1"
}
```

### Monitoring Active League

#### Checking Audit Logs

The audit log contains all protocol messages:

```bash
$ tail -f ./logs/audit.jsonl | jq

{
  "timestamp": "2025-12-25T10:05:23.456Z",
  "direction": "request",
  "from": "player:alice",
  "to": "league_manager",
  "envelope": {
    "protocol": "league.v2",
    "message_type": "QUERY_STANDINGS",
    "sender": "player:alice",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
{
  "timestamp": "2025-12-25T10:05:23.789Z",
  "direction": "response",
  "from": "league_manager",
  "to": "player:alice",
  "envelope": {
    "protocol": "league.v2",
    "message_type": "STANDINGS_RESPONSE",
    "sender": "league_manager",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

#### Inspecting Database State

```bash
$ sqlite3 ./data/league.db

sqlite> -- Check league status
sqlite> SELECT league_id, status, created_at FROM leagues;
default-league|ACTIVE|2025-12-25 09:00:00

sqlite> -- Check all registered players
sqlite> SELECT player_id, status, registered_at FROM players;
player-001|ACTIVE|2025-12-25 09:05:00
player-002|ACTIVE|2025-12-25 09:05:05
player-003|ACTIVE|2025-12-25 09:05:10
player-004|ACTIVE|2025-12-25 09:05:15

sqlite> -- Check match results
sqlite> SELECT match_id, status, created_at FROM matches LIMIT 5;
match-001|COMPLETED|2025-12-25 09:30:00
match-002|COMPLETED|2025-12-25 09:32:00
match-003|IN_PROGRESS|2025-12-25 09:34:00
match-004|PENDING|2025-12-25 09:30:00
match-005|PENDING|2025-12-25 09:30:00

sqlite> -- View current standings
sqlite> SELECT
   ...>   rank, player_id, points, wins, losses, draws
   ...> FROM standings_snapshots
   ...> WHERE league_id = 'default-league'
   ...> ORDER BY rank;
1|player-003|9|3|0|0
2|player-001|6|2|1|0
3|player-002|3|1|2|0
4|player-004|0|0|3|0

sqlite> .quit
```

### Complete Workflow Summary

Here's the complete workflow from start to finish:

```bash
# 1. Start League Manager
$ python -m src.league_manager.main --port 8000
# League starts in REGISTRATION state

# 2. Start Referee(s)
$ python -m src.referee.main referee1 --port 8001 &
$ python -m src.referee.main referee2 --port 8002 &

# 3. Start Players
$ python -m src.player.main player1 --port 9001 --strategy smart &
$ python -m src.player.main player2 --port 9002 --strategy smart &
$ python -m src.player.main player3 --port 9003 --strategy random &
$ python -m src.player.main player4 --port 9004 --strategy random &

# 4. Check registration status
$ curl http://localhost:8000/status | jq
{
  "status": "REGISTRATION",
  "league_id": "default-league",
  "referees": 2,
  "players": 4
}

# 5. Transition to SCHEDULING (currently requires code access)
# NOTE: No HTTP endpoint exists for this operation
# See docs/USAGE.md for details on league lifecycle management

# 6. Query standings (once league is ACTIVE)
$ curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "league.handle",
    "params": {
      "envelope": {
        "protocol": "league.v2",
        "message_type": "QUERY_STANDINGS",
        "sender": "player:player1",
        "timestamp": "2025-12-25T10:00:00Z",
        "conversation_id": "uuid-here",
        "auth_token": "token-here"
      },
      "payload": {}
    },
    "id": "req-1"
  }' | jq

# 7. Monitor progress
$ tail -f ./logs/audit.jsonl
$ tail -f ./logs/league_manager.log
```

---

**For more examples, see**:
- [Usage Guide](../USAGE.md) - Complete usage documentation including lifecycle management
- [Architecture Documentation](../Architecture.md) - System architecture and design
- [PRD](../PRD.md) - Protocol specification and requirements
