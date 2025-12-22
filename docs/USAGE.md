# Agent League System - Usage Guide

## Quick Start

### Installation

```bash
# Install dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Running the League

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
