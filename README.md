# Agent League System

A game-agnostic league coordinator for autonomous agents that orchestrates competitive matches using a hub-and-spoke communication model.

## Overview

The Agent League System coordinates competitive matches between autonomous player agents. It features:

- **Game Agnostic**: League logic is completely independent of specific game rules
- **Deterministic Scheduling**: Round-robin scheduling ensures all players compete fairly
- **Protocol-First Design**: JSON-RPC over HTTP with strict envelope validation
- **Authority Separation**: Clear delegation between League Manager (coordination) and Referees (game execution)
- **Full Auditability**: All communication and state transitions are logged for replay and verification

## Features

- **Registration & Authentication**: Secure token-based authentication for referees and players
- **Round-Robin Scheduling**: Deterministic scheduling algorithm ensuring each player faces every other player exactly once
- **Game-Agnostic Match Execution**: Referees execute game-specific logic while the league remains game-independent
- **Real-Time Standings**: Automatic standings computation with tie-breaking rules
- **Comprehensive Logging**: Full audit trail of all protocol messages and state transitions
- **Persistence**: SQLite-based persistence for league state, matches, and results

## Architecture

The system consists of three main components:

1. **League Manager**: Central coordinator that handles:
   - Player and referee registration
   - Match scheduling
   - Standings computation
   - State management

2. **Referee**: Game-specific match executors that:
   - Execute individual matches
   - Request moves from players
   - Report results to the League Manager

3. **Player**: Autonomous agents that:
   - Register with the league
   - Respond to move requests
   - Query standings

For detailed architecture documentation, see [docs/Architecture.md](docs/Architecture.md).

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd AIAgents3997-HW7
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Quick Start

### One-Command Demo

The fastest way to see the system in action:

```bash
./run_simulation.sh
```

This automated script will:
- Start the League Manager (port 8000)
- Start 2 Referees (ports 8001-8002)
- Start 14 Players (ports 9001-9014) with mixed strategies
- Register all agents and start the league
- Execute 91 round-robin matches
- Display live match progress
- Show final standings with rankings
- Wait for you to press Enter before cleanup

**What you'll see:**
```
[3/5] Starting Players...
✓ Alice running (smart strategy, PID: 12345)
✓ Bob running (smart strategy, PID: 12346)
...

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

### Manual Setup

For detailed usage instructions and manual component startup, see [USAGE.md](docs/USAGE.md).

#### Basic Workflow

1. **Start the League Manager**
   ```bash
   python -m src.league_manager.main --port 8000
   ```

2. **Start Referees and Players**
   ```bash
   # Start referees
   python -m src.referee.main referee1 --port 8001
   python -m src.referee.main referee2 --port 8002

   # Start players
   python -m src.player.main alice --port 9001 --strategy smart
   python -m src.player.main bob --port 9002 --strategy smart
   python -m src.player.main charlie --port 9003 --strategy random
   python -m src.player.main dave --port 9004 --strategy random
   ```

3. **Start the League via Admin API**

   Once all agents have registered and signaled ready:
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
           "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
           "conversation_id": "'$(uuidgen || cat /proc/sys/kernel/random/uuid)'"
         },
         "payload": {}
       },
       "id": "start-1"
     }'
   ```

   This transitions the league through: REGISTRATION → SCHEDULING → ACTIVE

4. **Monitor Progress**
   ```bash
   # Check league status
   curl http://localhost:8000/status

   # View audit log
   tail -f ./logs/audit.jsonl
   ```

For complete API documentation and advanced usage, see [USAGE.md](docs/USAGE.md).

## Configuration

### League Settings

- **league_id**: Unique identifier for the league
- **game_type**: Type of game to play (currently supports "tic_tac_toe")

### Timeout Settings

- **move_timeout_ms**: Maximum time (in ms) for a player to respond to a move request (default: 30000)
- **match_timeout_ms**: Maximum time (in ms) for a complete match (default: 300000)

### Persistence Settings

- **database_path**: Path to SQLite database file
- **audit_log_path**: Path to JSON Lines audit log file

For complete configuration options, see [USAGE.md](docs/USAGE.md).

## Running the League

### Complete Workflow

1. **Initialize**: Start the League Manager server
2. **Registration**: Referees and players register and receive authentication tokens
3. **Scheduling**: Close registration to generate the round-robin schedule
4. **Execution**: Matches are automatically assigned and executed
5. **Results**: Standings are computed after each round
6. **Completion**: League transitions to COMPLETED state after all matches

### League States

- **INIT**: League is being initialized
- **REGISTRATION**: Accepting referee and player registrations
- **SCHEDULING**: Generating the match schedule
- **ACTIVE**: Matches are being executed
- **COMPLETED**: All matches complete, final standings published

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/common tests/league_manager tests/referee tests/player

# Integration tests only
pytest tests/integration

# With coverage report
pytest --cov=src --cov-report=html
```

### Test Organization

- **tests/common/**: Protocol, transport, auth, and persistence tests
- **tests/league_manager/**: Registration, scheduling, and standings tests
- **tests/referee/**: Game engine and match execution tests
- **tests/player/**: Player strategy tests
- **tests/integration/**: End-to-end league workflow tests

See [TEST_SUMMARY.md](TEST_SUMMARY.md) for detailed test coverage information.

## Protocol

The system uses JSON-RPC 2.0 over HTTP with a custom protocol envelope:

```json
{
  "jsonrpc": "2.0",
  "method": "league.handle",
  "params": {
    "envelope": {
      "protocol": "league.v2",
      "message_type": "REGISTER_PLAYER_REQUEST",
      "sender": "player:alice",
      "timestamp": "2025-01-21T10:00:00Z",
      "conversation_id": "uuid-here",
      "auth_token": "token-here"
    },
    "payload": {
      "player_id": "alice"
    }
  },
  "id": "request-uuid"
}
```

For complete protocol specification, see [docs/PRD.md](docs/PRD.md).

## Troubleshooting

### Common Issues

#### Players Cannot Register

**Problem**: Player registration fails with "At least one referee must be registered"

**Solution**: Ensure at least one referee is registered before registering players.

#### Match Execution Timeouts

**Problem**: Matches timeout during execution

**Solutions**:
- Increase `move_timeout_ms` in configuration
- Check that player processes are running and reachable
- Verify network connectivity between referee and players

#### Database Locked Errors

**Problem**: SQLite database locked errors

**Solution**: Ensure only one League Manager instance is running per database file.

#### Registration Closed

**Problem**: Cannot register after closing registration

**Solution**: Registration must complete before calling the close-registration endpoint. Restart the League Manager to reset.

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python -m src.league_manager.main --config config.yaml
```

### Audit Logs

All protocol messages are logged to the audit log file (default: `./data/audit.jsonl`). Review this file for detailed message flow analysis.

## Project Structure

```
AIAgents3997-HW7/
├── src/
│   ├── common/           # Shared protocol, transport, auth, persistence
│   ├── league_manager/   # League coordination logic
│   ├── referee/          # Match execution and game engines
│   └── player/           # Player agents and strategies
├── tests/                # Comprehensive test suite
├── docs/                 # Architecture and PRD documentation
│   ├── Architecture.md   # System architecture
│   ├── PRD.md           # Product requirements
│   └── ADRs/            # Architecture decision records
├── config.yaml          # Configuration file
└── README.md            # This file
```

## Contributing

### Development Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests before committing:
```bash
pytest
```

3. Follow the existing code style and patterns

### Adding New Games

To add support for a new game:

1. Implement a game engine in `src/referee/games/` following the interface:
   - `is_terminal()`: Check if game is finished
   - `make_move()`: Execute a move
   - `get_result()`: Get final outcome
   - `get_step_context()`: Provide game state to players

2. Register the game type in the referee's game type mapping

3. Add comprehensive tests

See [ADR-003: Game-Agnostic Referee Pattern](docs/ADRs/003-game-agnostic-referee.md) for details.

## License

This project is part of an academic assignment for AIAgents3997-HW7.

## Documentation

- [Architecture Documentation](docs/Architecture.md) - Detailed system architecture
- [Product Requirements](docs/PRD.md) - Complete product requirements
- [Usage Guide](USAGE.md) - Detailed usage instructions
- [Test Summary](TEST_SUMMARY.md) - Test coverage and organization
- [Development Log](docs/development/PROMPT_LOG.md) - Development process and decisions

## Support

For issues, questions, or contributions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Architecture Documentation](docs/Architecture.md)
3. Check existing test cases for examples
4. Review the audit logs for protocol-level debugging
