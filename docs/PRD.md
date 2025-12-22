# Product Requirements Document (PRD) - Agent League System

## Overview
This PRD defines requirements for a league system that orchestrates matches between autonomous agents.
The league is game-agnostic: referees execute game logic, while the League Manager coordinates registration,
scheduling, and standings.

This PRD is split into section documents under `docs/prd/`. Each section is authoritative for its domain.

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
