# Product Requirements Document (PRD) - Agent League System

## Overview
This PRD defines requirements for a league system that orchestrates matches between autonomous agents.
The league is game-agnostic: referees execute game logic, while the League Manager coordinates registration,
scheduling, and standings.

This PRD is split into section documents under `docs/prd/`. Each section is authoritative for its domain.

---

## Problem Statement

### Current Situation
There is no standardized, game-agnostic framework for organizing and executing tournaments between autonomous software agents. Existing tournament systems are typically:
- **Tightly coupled to specific games** - Changing games requires rewriting the tournament infrastructure
- **Lacking proper isolation** - Agents can interfere with each other or the tournament system
- **Missing standardized protocols** - Each implementation uses ad-hoc communication patterns
- **Difficult to extend** - Adding new games or tournament formats requires significant effort

### Who Is Affected
- **AI/ML Researchers**: Need consistent environments to test and compare agent strategies across multiple games
- **Software Developers**: Want to build autonomous agents that can compete in various game types
- **Educators**: Require tournament systems for teaching AI concepts and hosting student competitions
- **Game Developers**: Need infrastructure to host agent-based competitions for their games

### Why This Is A Problem
Without a standardized agent league system:
1. **Duplicated Effort**: Every new game requires building tournament infrastructure from scratch
2. **Limited Comparability**: Agents designed for different systems cannot compete against each other
3. **Reduced Innovation**: Developers spend time on infrastructure instead of strategy development
4. **Fragmented Ecosystem**: No shared platform for agent competitions and learning

### Consequences of Not Solving
- Continued fragmentation of agent competition platforms
- Higher barrier to entry for new agent developers
- Missed opportunities for cross-game agent learning and transfer
- Limited ability to host large-scale, multi-game tournaments

---

## Functional Requirements

### FR-1: Game-Agnostic Architecture
**Requirement**: The system MUST support multiple game types without modifying core league logic.

**Acceptance Criteria**:
- Adding a new game requires only implementing a referee interface
- League Manager operates independently of game-specific rules
- Same protocol works for any turn-based game
- Demonstrated with at least 2 different games (e.g., Tic-Tac-Toe, Connect Four)

### FR-2: Autonomous Agent Registration
**Requirement**: Players MUST be able to register autonomously via API without manual intervention.

**Acceptance Criteria**:
- RESTful registration endpoint available
- Authentication tokens issued automatically
- Registration confirmation within 1 second
- Support for minimum 100 concurrent registrations

### FR-3: Round-Robin Tournament Scheduling
**Requirement**: The system MUST generate fair round-robin schedules where each player faces every other player exactly once.

**Acceptance Criteria**:
- All player pairs scheduled exactly once
- Schedule generation is deterministic (same inputs = same schedule)
- Concurrent matches grouped to minimize total rounds
- Schedule generated within 5 seconds for 100 players

### FR-4: Automated Match Execution
**Requirement**: Matches MUST execute automatically without manual intervention once scheduled.

**Acceptance Criteria**:
- Referee enforces game rules autonomously
- Invalid moves rejected with error codes
- Game state tracked accurately
- Match results recorded automatically

### FR-5: Real-Time Standings Calculation
**Requirement**: The system MUST calculate and update standings after each match completion.

**Acceptance Criteria**:
- Standings update within 1 second of match completion
- Points calculated correctly (win/loss/draw)
- Tiebreakers applied consistently
- Historical standings preserved

### FR-6: JSON-RPC Protocol Communication
**Requirement**: All inter-component communication MUST use JSON-RPC 2.0 over HTTP.

**Acceptance Criteria**:
- Standard JSON-RPC 2.0 compliance
- Protocol envelope with sender, timestamp, conversation_id
- Support for both request/response and notification patterns
- Maximum 100ms protocol overhead

### FR-7: Persistent State Management
**Requirement**: All league data MUST be persisted to survive system restarts.

**Acceptance Criteria**:
- SQLite database for persistence
- Atomic transactions for state changes
- Data integrity maintained across restarts
- Backup and recovery supported

### FR-8: Configurable System Parameters
**Requirement**: Key system parameters MUST be configurable without code changes.

**Acceptance Criteria**:
- Configuration via YAML file and environment variables
- Sensitive values (secrets) isolated in .env
- Configuration validation on startup
- Hot-reload for non-critical settings (optional)

### FR-9: Comprehensive Error Handling
**Requirement**: The system MUST handle errors gracefully with clear error messages.

**Acceptance Criteria**:
- Structured error codes (-32700 to -32603 range)
- Human-readable error messages
- Automatic retry for transient errors
- Failed matches marked explicitly

### FR-10: Extensible Game Interface
**Requirement**: Adding new games MUST only require implementing a defined interface.

**Acceptance Criteria**:
- GameReferee abstract base class defined
- Interface includes: initialize, validate_move, execute_move, check_game_over
- New games loaded without modifying League Manager
- Reference implementation provided

### FR-11: Player Strategy Abstraction
**Requirement**: Players MUST support pluggable strategy implementations.

**Acceptance Criteria**:
- PlayerStrategy interface defined
- Multiple strategies supported (random, smart, AI-powered)
- Strategy switchable per player
- Strategy isolation (one player's strategy doesn't affect others)

### FR-12: Timeout Enforcement
**Requirement**: Matches and operations MUST enforce configurable timeouts.

**Acceptance Criteria**:
- Move timeout configurable per game
- Match timeout enforced
- Timeout violations result in forfeit
- Timeout values configurable via config.yaml

---

## Success Metrics

### Primary KPIs

#### 1. System Scalability
**Metric**: Number of concurrent players supported
- **Baseline**: 0 (no existing system)
- **Target**: 100 players minimum
- **Measurement**: Load test with 100 registered players
- **Success Criteria**: System handles 100 players with <5% error rate

#### 2. Match Execution Performance
**Metric**: Matches executed per minute
- **Baseline**: 0
- **Target**: 60 matches/minute (1 match/second)
- **Measurement**: Throughput test with concurrent matches
- **Success Criteria**: Sustained 60 matches/minute for 10 minutes

#### 3. Scheduling Efficiency
**Metric**: Rounds required vs theoretical minimum (N/2 for N even players)
- **Baseline**: N/A (manual scheduling)
- **Target**: <110% of theoretical minimum
- **Measurement**: Compare generated schedule to optimal
- **Success Criteria**: Within 10% of minimum rounds

#### 4. Test Coverage
**Metric**: Code coverage percentage
- **Baseline**: 0%
- **Target**: 80% minimum
- **Measurement**: pytest --cov coverage report
- **Success Criteria**: 80%+ coverage on src/

#### 5. API Reliability
**Metric**: API success rate
- **Baseline**: N/A
- **Target**: 99.9% success rate
- **Measurement**: Monitor API responses over 1000 requests
- **Success Criteria**: <0.1% error rate (excluding client errors)

### Secondary KPIs

#### 6. Documentation Completeness
**Metric**: Percentage of public APIs documented
- **Target**: 100%
- **Measurement**: Docstring coverage check
- **Success Criteria**: All public functions have docstrings

#### 7. Error Recovery Rate
**Metric**: Percentage of transient errors successfully retried
- **Target**: 95%
- **Measurement**: Monitor retry success in logs
- **Success Criteria**: 95%+ of retryable errors succeed on retry

#### 8. Configuration Flexibility
**Metric**: Percentage of magic numbers moved to configuration
- **Target**: 100%
- **Measurement**: Code audit for hardcoded values
- **Success Criteria**: Zero hardcoded timeouts, ports, or limits in src/

### Quality Metrics

#### 9. Game Extensibility
**Metric**: Time to add a new game
- **Target**: <8 hours for a moderately complex game
- **Measurement**: Time trial implementing Connect Four
- **Success Criteria**: Complete implementation in one day

#### 10. Developer Experience
**Metric**: Time to first successful match for new developers
- **Target**: <30 minutes from clone to first match
- **Measurement**: New developer onboarding trial
- **Success Criteria**: README instructions sufficient for 30-minute setup

### Data Collection Methods

1. **Performance Metrics**: Collected via application logging and monitoring
2. **Coverage Metrics**: Automated via pytest-cov during CI/CD
3. **Error Metrics**: Tracked in application logs and metrics export
4. **User Metrics**: Time trials and developer surveys
5. **Quality Metrics**: Code audits and automated checks

### Reporting Frequency

- **Real-time**: API error rates, match throughput
- **Daily**: Test coverage, code quality checks
- **Weekly**: Developer experience metrics
- **Monthly**: Overall system health review

### Success Threshold

**Minimum Viable Product (MVP)**:
- All Primary KPIs meet targets
- At least 2 Secondary KPIs meet targets
- Zero critical bugs

**Production Ready**:
- All Primary and Secondary KPIs meet targets
- All Quality Metrics meet targets
- Comprehensive documentation complete

---

## Sections
1. [Section 1 - League Scope, Actors, and Responsibilities](prd/section-1-scope-and-actors.md)
2. [Section 2 - Transport, MCP, and Protocol Envelope](prd/section-2-transport-and-protocol.md)
3. [Section 3 - Registration and Authentication Flow](prd/section-3-registration-and-auth.md)
4. [Section 4 - Scheduling and Round Management](prd/section-4-scheduling-and-rounds.md)
5. [Section 5 - Match Execution and Game Abstraction](prd/section-5-match-execution.md)
6. [Section 6 - Result Reporting and Standings](prd/section-6-results-and-standings.md)
7. [Section 7 - Timeouts, Errors, and Recovery](prd/section-7-timeouts-and-errors.md)
8. [Section 8 - Persistence and Logging](prd/section-8-persistence-and-logging.md)
9. [Section 9 - Configuration and Extensibility](prd/section-9-configuration-and-extensibility.md)
10. [Section 10 - Out-of-Scope and Assumptions](prd/section-10-out-of-scope.md)

## Normative references
- Flow diagrams: `docs/diagrams/`
- Protocol examples: `docs/protocol/examples/`

Protocol examples are normative for field placement, nesting, and formatting.
