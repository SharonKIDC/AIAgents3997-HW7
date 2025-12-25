# Agent League System - Usage Guide

This guide explains how to use the Agent League System once it's installed. For installation instructions, see [README.md](../README.md).

## Prerequisites

- System installed and dependencies satisfied (see [README.md](../README.md#installation))
- Python virtual environment activated (if using one)

## Quick Start with Simulation Scripts

For a quick end-to-end demonstration, use the provided scripts:

```bash
# Run complete simulation (starts everything, activates league, monitors progress)
./scripts/run_simulation.sh

# The script will:
# 1. Start League Manager on port 8000
# 2. Start 2 referees on ports 8001-8002
# 3. Start 14 players on ports 9001-9014 (7 smart, 7 random strategies)
# 4. Automatically activate the league via Admin MCP API
# 5. Execute all 91 round-robin matches
# 6. Display real-time match progress updates
# 7. Show final standings when complete
# 8. Wait for Enter key before cleanup
```

**Expected Simulation Output:**
```
[3/5] Starting Players...
✓ Alice running (smart strategy, PID: 12345)
✓ Bob running (smart strategy, PID: 12346)
...
✓ Nick running (random strategy, PID: 12358)

📊 Monitoring league progress (updates every 5s)...
16:53:09 📊 Match Progress: 6/91 completed
16:53:14 📊 Match Progress: 12/91 completed
...
16:54:20 ✅ League Status: COMPLETED

Final Results:
✅ Matches completed: 91

🏆 Final Standings:
Rank   Player     Points   Record
1      alice      27       9W-0D-4L
2      bob        24       8W-0D-5L
...

✅ Simulation completed successfully!
Press Enter to cleanup and exit...
```

To manually reset the league between runs:
```bash
./scripts/reset_league.sh

# This removes:
# - Database files (data/league.db)
# - Audit logs (logs/audit.jsonl)
# - Application logs
# - Simulation logs
```

## Running the League Manually

#### 1. Start the League Manager

```bash
python3 -m src.league_manager.main --port 8000
```

#### 2. Start Referees

In separate terminals:

```bash
python3 -m src.referee.main referee1 --port 8001
python3 -m src.referee.main referee2 --port 8002
```

#### 3. Start Players

In separate terminals:

```bash
python3 -m src.player.main player1 --port 9001 --strategy smart
python3 -m src.player.main player2 --port 9002 --strategy smart
python3 -m src.player.main player3 --port 9003 --strategy random
```

### Command-Line Options

#### League Manager

```bash
python3 -m src.league_manager.main [OPTIONS]

Options:
  --host HOST               Host to bind to (default: localhost)
  --port PORT               Port to bind to (default: 8000)
  --config-dir DIR          Configuration directory (default: ./config)
  --log-level LEVEL         Logging level (default: INFO)
```

#### Referee

```bash
python3 -m src.referee.main REFEREE_ID [OPTIONS]

Arguments:
  REFEREE_ID               Unique referee identifier (required)

Options:
  --host HOST              Host to bind to (default: localhost)
  --port PORT              Port to bind to (default: 8001)
  --league-manager-url URL League Manager URL (default: http://localhost:8000/mcp)
  --log-level LEVEL        Logging level (default: INFO)
```

#### Player

```bash
python3 -m src.player.main PLAYER_ID [OPTIONS]

Arguments:
  PLAYER_ID                Unique player identifier (required)

Options:
  --host HOST              Host to bind to (default: localhost)
  --port PORT              Port to bind to (default: 9001)
  --league-manager-url URL League Manager URL (default: http://localhost:8000/mcp)
  --strategy TYPE          Strategy to use: smart|random (default: smart)
  --log-level LEVEL        Logging level (default: INFO)
```

## Architecture

### Components

1. **League Manager** - Central coordinator
   - Handles registration
   - Generates round-robin schedule
   - Assigns matches to referees
   - Computes standings

2. **Referee** - Match executor
   - Receives match assignments
   - Orchestrates game execution
   - Reports results to League Manager

3. **Player** - Autonomous competitor
   - Registers with League Manager
   - Responds to move requests from Referee
   - Implements game strategy

### Communication Flow

```
Player <---> League Manager <---> Referee <---> Player
         (Registration)        (Match Assignment)
                               (Game Execution)
         <--- Results ---
```

## Configuration

### League Configuration (`config/league.yaml`)

- League settings (ID, name)
- Registration policies
- Timeout policies
- Retry policies
- Logging configuration
- Database path

### Game Registry (`config/game_registry.yaml`)

- Available game types
- Scoring rules
- Game implementations

## Logs and Data

- **Application logs**: `./logs/*.log`
- **Audit log**: `./logs/audit.jsonl` (append-only protocol messages)
- **Database**: `./data/league.db` (SQLite)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Protocol

All communication uses JSON-RPC 2.0 over HTTP with a league protocol envelope.

### Example Registration Request

```json
{
  "jsonrpc": "2.0",
  "method": "league.handle",
  "params": {
    "envelope": {
      "protocol": "league.v2",
      "message_type": "REGISTER_PLAYER_REQUEST",
      "sender": "player:player1",
      "timestamp": "2025-01-21T12:00:00Z",
      "conversation_id": "uuid-here"
    },
    "payload": {
      "player_id": "player1"
    }
  },
  "id": "request-id"
}
```

## Troubleshooting

### Port Already in Use

If you get "Address already in use" errors, check for processes:

```bash
lsof -i :8000  # Check League Manager port
lsof -i :8001  # Check Referee port
lsof -i :9001  # Check Player port
```

### Database Locked

If you get database lock errors, ensure only one League Manager is running.

### Import Errors

Ensure you run from the project root directory:

```bash
cd /path/to/AIAgents3997-HW7
python3 -m src.league_manager.main
```

## League Lifecycle Management

### League States

The league progresses through these states:
- **INIT**: League is being initialized
- **REGISTRATION**: Accepting referee and player registrations
- **SCHEDULING**: Generating the match schedule
- **ACTIVE**: Matches are being executed
- **COMPLETED**: All matches complete, final standings published

### Agent States

Referees and players progress through their own lifecycle:

1. **REGISTERED**: Agent has registered with the league and received an auth token
2. **ACTIVE**: Agent has signaled it's fully initialized and ready to participate
3. **INACTIVE**: Agent has been deactivated

**Agent Activation Flow**:
```
Agent starts → Registers with League Manager → Receives auth_token
              ↓
         Status: REGISTERED
              ↓
         Completes initialization (HTTP server ready, strategy loaded, etc.)
              ↓
         Sends AGENT_READY_REQUEST to League Manager
              ↓
         Status: ACTIVE ✓ (ready for match assignments)
```

**Important**: Agents **must explicitly signal readiness** by sending `AGENT_READY_REQUEST` after initialization. This ensures only operational agents participate in matches. The League Manager will NOT auto-activate agents.

### Managing the League via MCP API

#### 1. Check League Status

Using the health endpoint:
```bash
curl http://localhost:8000/status
```

Response:
```json
{
  "status": "REGISTRATION",
  "league_id": "default-league",
  "referees": 2,
  "players": 4
}
```

Or using the MCP protocol for detailed status:
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "league.handle",
    "params": {
      "envelope": {
        "protocol": "league.v2",
        "message_type": "ADMIN_GET_STATUS_REQUEST",
        "sender": "admin",
        "timestamp": "2025-12-25T10:00:00Z",
        "conversation_id": "'"$(uuidgen)"'"
      },
      "payload": {}
    },
    "id": "status-1"
  }'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "envelope": {
      "protocol": "league.v2",
      "message_type": "ADMIN_GET_STATUS_RESPONSE",
      "sender": "league_manager",
      "timestamp": "2025-12-25T10:00:01Z",
      "conversation_id": "...",
      "league_id": "default-league"
    },
    "payload": {
      "league_id": "default-league",
      "status": "REGISTRATION",
      "referees": 2,
      "players": 4,
      "can_start": true
    }
  },
  "id": "status-1"
}
```

#### 2. Start the League

Once all players and referees have registered, start the league:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "league.handle",
    "params": {
      "envelope": {
        "protocol": "league.v2",
        "message_type": "ADMIN_START_LEAGUE_REQUEST",
        "sender": "admin",
        "timestamp": "2025-12-25T10:00:00Z",
        "conversation_id": "'"$(uuidgen)"'"
      },
      "payload": {}
    },
    "id": "start-1"
  }'
```

Response on success:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "envelope": {
      "protocol": "league.v2",
      "message_type": "ADMIN_START_LEAGUE_RESPONSE",
      "sender": "league_manager",
      "timestamp": "2025-12-25T10:00:01Z",
      "conversation_id": "...",
      "league_id": "default-league"
    },
    "payload": {
      "status": "started",
      "league_status": "ACTIVE",
      "message": "League started successfully"
    }
  },
  "id": "start-1"
}
```

This single command:
1. Closes registration (transitions from REGISTRATION to SCHEDULING)
2. Generates the round-robin schedule
3. Transitions to ACTIVE state
4. Assigns pending matches to available referees

**Minimum Requirements:**
- At least 1 referee registered
- At least 2 players registered

If requirements are not met, you'll receive an error:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Cannot start league: minimum requirements not met",
    "data": {
      "referees": 0,
      "players": 1,
      "min_referees": 1,
      "min_players": 2
    }
  },
  "id": "start-1"
}
```

#### 3. Monitor League Progress

Check the audit log for detailed message history:
```bash
tail -f ./logs/audit.jsonl
```

Check the database for league state:
```bash
sqlite3 ./data/league.db "SELECT status FROM leagues WHERE league_id = 'default-league';"
```

#### 4. Query Standings

Once matches begin, players can query standings via JSON-RPC:

```bash
curl -X POST http://localhost:8000/mcp \
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
        "auth_token": "your-auth-token"
      },
      "payload": {}
    },
    "id": "standings-query-1"
  }'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "envelope": {
      "protocol": "league.v2",
      "message_type": "STANDINGS_RESPONSE",
      "sender": "league_manager",
      "timestamp": "2025-12-25T10:00:01Z",
      "conversation_id": "uuid-here",
      "league_id": "default-league"
    },
    "payload": {
      "standings": [
        {
          "rank": 1,
          "player_id": "player1",
          "points": 6,
          "wins": 2,
          "losses": 0,
          "draws": 0
        },
        {
          "rank": 2,
          "player_id": "player2",
          "points": 3,
          "wins": 1,
          "losses": 1,
          "draws": 0
        }
      ],
      "updated_at": "2025-12-25T10:00:00Z"
    }
  },
  "id": "standings-query-1"
}

## Development

### Code Style

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

### Project Structure

```
AIAgents3997-HW7/
├── config/              # Configuration files
├── data/                # Database files (gitignored)
├── docs/                # Documentation
├── logs/                # Log files (gitignored)
├── src/
│   ├── common/          # Shared utilities
│   ├── league_manager/  # League Manager implementation
│   ├── referee/         # Referee implementation
│   │   └── games/       # Game-specific logic
│   └── player/          # Player implementation
├── tests/               # Test files
├── pyproject.toml       # Project configuration
└── .gitignore
```
