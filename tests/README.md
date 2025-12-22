# Agent League System - Test Suite

This directory contains comprehensive unit and integration tests for the Agent League System.

## Test Structure

```
tests/
├── conftest.py                           # Shared fixtures and test utilities
├── pytest.ini                            # Pytest configuration (in parent dir)
│
├── common/                               # Tests for common infrastructure
│   ├── test_protocol.py                  # Protocol validation, envelopes, JSON-RPC
│   ├── test_transport.py                 # HTTP server/client, communication
│   ├── test_auth.py                      # Authentication and authorization
│   └── test_persistence.py               # Database operations
│
├── league_manager/                       # Tests for league management
│   ├── test_registration.py             # Referee and player registration
│   ├── test_scheduler.py                # Round-robin scheduling algorithm
│   └── test_standings.py                # Standings computation and tie-breaking
│
├── referee/                              # Tests for referee components
│   ├── test_tic_tac_toe.py              # Tic Tac Toe game logic
│   └── test_match_executor.py           # Match execution orchestration
│
├── player/                               # Tests for player components
│   └── test_strategy.py                 # Player move strategies
│
└── integration/                          # End-to-end integration tests
    └── test_full_league.py              # Complete league workflow
```

## Test Coverage

### Common Infrastructure Tests (tests/common/)

**test_protocol.py** - Protocol Layer Tests
- Envelope creation and validation
- Message type enumeration
- Sender format validation
- Timestamp validation (ISO-8601 UTC)
- UUID validation
- JSON-RPC request/response structures
- Error response generation
- Helper function testing

**test_transport.py** - HTTP Transport Tests
- HTTP server lifecycle (start/stop)
- Health and status endpoints
- JSON-RPC message handling
- Client request/response cycle
- Error handling and propagation
- Concurrent request handling
- Fire-and-forget messaging

**test_auth.py** - Authentication Tests
- Token issuance and validation
- Token idempotency
- Sender verification
- Token invalidation
- Agent type verification
- Thread safety
- Multi-agent scenarios

**test_persistence.py** - Database Tests
- Schema initialization
- League CRUD operations
- Referee registration and management
- Player registration and management
- Round and match operations
- Match result storage and retrieval
- Standings snapshot management
- Transaction commit and rollback

### League Manager Tests (tests/league_manager/)

**test_registration.py** - Registration Flow Tests
- Successful referee registration
- Successful player registration
- Duplicate registration prevention
- Registration closed enforcement
- Precondition validation (referee required before players)
- Token issuance verification
- Multiple agent registration

**test_scheduler.py** - Scheduling Tests
- Round-robin schedule generation
- Deterministic scheduling
- All-pairs-once guarantee
- No-player-twice-per-round constraint
- Schedule persistence to database
- Edge cases (0, 1, 2, many players)
- Large group scheduling (10+ players)
- Player order independence

**test_standings.py** - Standings Tests
- Basic standings computation
- Sorting by points (descending)
- Tie-breaking by wins
- Tie-breaking by draws
- Tie-breaking by player ID (deterministic)
- Statistics tracking (wins, draws, losses, matches played)
- Standings publication and persistence
- Players with no matches inclusion
- Multi-round accumulation

### Referee Tests (tests/referee/)

**test_tic_tac_toe.py** - Game Logic Tests
- Game initialization
- Valid and invalid move detection
- Horizontal win detection
- Vertical win detection
- Diagonal win detection (both directions)
- Draw detection
- Board state management
- Step context generation
- Available moves calculation
- Result computation (win/loss/draw with points)
- Board state isolation

**test_match_executor.py** - Match Execution Tests
- Match executor initialization
- Complete match execution (tic tac toe)
- Draw game handling
- Invalid move forfeit
- Player timeout forfeit
- Unsupported game type rejection
- Game invitation sending
- Game over notification sending
- Result metadata inclusion

### Player Tests (tests/player/)

**test_strategy.py** - Strategy Tests
- Strategy initialization
- Valid move format
- Empty board move selection
- Winning move detection
- Opponent blocking
- Win prioritization over blocking
- Nearly full board handling
- No available moves error handling
- Win detection (all directions)
- Random strategy testing
- Strategy variety verification

### Integration Tests (tests/integration/)

**test_full_league.py** - End-to-End Tests
- Complete league lifecycle
  - Initialization
  - Registration (referees and players)
  - Scheduling
  - Match execution (simulated)
  - Standings computation
  - League completion
- Minimum players scenario (2)
- State persistence across instances
- Standings reflecting all results
- Authentication throughout lifecycle
- Schedule determinism across runs

## Running Tests

### Install Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Module

```bash
pytest tests/common/test_protocol.py -v
```

### Run Tests by Category

```bash
# Unit tests only
pytest tests/common tests/league_manager tests/referee tests/player -v

# Integration tests only
pytest tests/integration -v -m integration
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Run Specific Test

```bash
pytest tests/common/test_protocol.py::TestEnvelope::test_envelope_creation_with_required_fields -v
```

## Test Markers

Tests are marked with the following categories:

- `unit` - Unit tests for individual components
- `integration` - Integration tests for full system
- `protocol` - Protocol validation tests
- `database` - Database operation tests
- `auth` - Authentication tests
- `game` - Game logic tests
- `network` - Network communication tests

Use markers to run specific test categories:

```bash
pytest tests/ -m "unit and not network"
pytest tests/ -m integration
```

## Fixtures

### Available Fixtures (from conftest.py)

- `temp_db` - Temporary SQLite database with initialized schema
- `auth_manager` - Fresh AuthManager instance
- `config_manager` - ConfigManager with test configuration
- `sample_league_id` - Consistent league ID for tests
- `sample_referee_ids` - List of sample referee IDs
- `sample_player_ids` - List of sample player IDs
- `registered_league` - League with pre-registered referees and players
- `sample_envelope_data` - Valid envelope dictionary
- `sample_jsonrpc_request` - Valid JSON-RPC request

## Test Quality Standards

All tests follow these principles:

1. **Independence** - Tests can run in any order
2. **Determinism** - Same results every time
3. **Speed** - Use mocks where appropriate
4. **Clarity** - Clear test names and assertions
5. **Comprehensiveness** - Cover happy paths, edge cases, and error cases

## Coverage Goals

The test suite targets >80% code coverage across all modules:

- Common infrastructure: 90%+
- League manager: 85%+
- Referee: 80%+
- Player: 80%+
- Integration: Full workflow coverage

## Writing New Tests

When adding new tests:

1. Place test in appropriate directory
2. Name test file `test_<module>.py`
3. Name test functions `test_<description>`
4. Use fixtures from conftest.py
5. Add markers for categorization
6. Follow existing test patterns
7. Ensure test is independent and fast

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example CI configuration
test:
  script:
    - pip install -r requirements-test.txt
    - pytest tests/ --cov=src --cov-report=xml
    - coverage report --fail-under=80
```

## Troubleshooting

### Import Errors

Ensure you're running pytest from the project root:
```bash
cd /root/Git/AIAgents3997-HW7
pytest tests/
```

### Database Locked

Temporary databases use threading locks. If tests hang, check for:
- Unclosed database connections
- Deadlocks in transaction tests

### Network Tests Failing

Network tests (HTTP server/client) may fail if ports are in use:
- Tests use high port numbers (9990-9999)
- Each test uses unique ports
- Servers are stopped in cleanup

## Test Statistics

- **Total Test Modules**: 11
- **Total Test Lines**: ~3,300
- **Test Categories**: 8
- **Shared Fixtures**: 10
- **Integration Scenarios**: 6

## Future Enhancements

Potential test improvements:

1. Performance benchmarks
2. Load testing for concurrent matches
3. Security testing (injection, auth bypass)
4. Chaos testing (network failures, timeouts)
5. Property-based testing (hypothesis)
6. Contract testing for protocol compliance
