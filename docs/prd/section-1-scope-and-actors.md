# Section 1 - League Scope, Actors, and Responsibilities

## 1.1 Purpose
The League Management System coordinates a competitive league composed of autonomous agents that play games governed by a shared protocol.

The system is responsible for:
- Managing league-wide state and lifecycle
- Enforcing protocol compliance at the league level
- Scheduling matches and announcing rounds
- Delegating match execution to referees
- Aggregating results and publishing standings

Game execution is delegated to referees, allowing the league to support multiple game types without changing league-level logic.

## 1.2 Actors

### 1.2.1 League Manager
The League Manager is the single authoritative coordinator of the league.

Responsibilities:
- Accept and validate registrations from referees and players
- Issue authentication tokens
- Maintain league configuration and metadata
- Generate a Round-Robin match schedule
- Assign matches to referees
- Announce rounds
- Receive match results from referees
- Compute and publish league standings
- Enforce league-level protocol rules and timeouts

Authority:
- Final authority for league state and standings
- May suspend or reject agents that violate protocol or timing constraints

Out of scope:
- Running game logic
- Communicating game rules to players
- Making game-level decisions

### 1.2.2 Referee
A Referee is an autonomous agent responsible for executing a single match at a time. Multiple referees may exist concurrently.

Responsibilities:
- Register with the League Manager
- Accept match assignments
- Invite players to participate in a match
- Orchestrate game steps according to the assigned game type
- Request moves from players
- Validate moves
- Advance the game state
- Determine match outcome
- Report finalized results to the League Manager

Authority:
- Final authority for all decisions within a match
- Authoritative source of match results

Constraints:
- A referee must not execute more than one match concurrently
- A referee must follow the league protocol and timing rules

### 1.2.3 Player
A Player is an autonomous agent representing a competitor in the league.

Responsibilities:
- Register with the League Manager
- Accept or reject match invitations
- Respond to move requests issued by referees
- Follow game-specific rules as instructed by the referee

Constraints:
- Players do not communicate directly with other players
- Players do not compute schedules, results, or standings
- Players act only when prompted by the League Manager or a Referee

## 1.3 Communication Model
The system follows a hub-and-spoke communication model.

Rules:
- All communication is performed over HTTP using MCP-compatible JSON-RPC
- Players never communicate directly with other players
- League Manager and Referees act as communication hubs

Allowed communication paths:
- Player ↔ League Manager: registration, league notifications, standings queries
- Player ↔ Referee: game invitations, move requests, game results
- Referee ↔ League Manager: match assignment, match result reporting, error reporting

Any communication outside these paths is considered invalid.

## 1.4 Authentication Model (Conceptual)
- Every actor must register before participating in league operations
- Successful registration returns an auth_token
- All subsequent requests must include a valid auth_token
- Tokens are validated by the receiving authority:
  - League Manager validates league-level requests
  - Referees validate match-level requests

Requests missing a valid token are rejected.

## 1.5 Actor Lifecycle States
All actors transition through the following lifecycle states:
- INIT: Agent started, not registered
- REGISTERED: Registration accepted, token issued
- ACTIVE: Participating in league or match operations
- SUSPENDED: Temporarily blocked due to timeout or protocol violation
- SHUTDOWN: Agent no longer active

State transitions are enforced by the League Manager or Referee, depending on context.

## 1.6 League Execution Flow
High-level flow:
1. League Manager starts
2. Referees register
3. Players register
4. League Manager generates schedule
5. League Manager assigns matches to referees
6. Referees execute matches (game-agnostic step loop)
7. Referees report results
8. League Manager updates standings

Diagram:
- `docs/diagrams/league-flow.md`

## 1.7 Non-Functional Constraints
- Exactly one League Manager exists per league
- Multiple referees may operate concurrently
- Scheduling and scoring must be deterministic
- All timestamps must be expressed in UTC
- All decisions must be reproducible from persisted logs
- The system must support multiple game types without modifying league logic

## 1.8 Explicit Non-Goals
This section does not define:
- Message schemas
- JSON-RPC field structures
- Error codes
- Game rules
- Scheduling algorithms

These are defined in subsequent PRD sections.
