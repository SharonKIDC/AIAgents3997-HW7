# Section 5 - Match Execution and Game Abstraction

## 5.1 Purpose
Defines how matches are executed in a game-agnostic manner.

## 5.2 Match Ownership
- Each match is owned by exactly one referee
- The referee is the authoritative controller of the match lifecycle

## 5.3 Game-Agnostic Execution Model
A match is executed as a sequence of steps until termination.

Each step consists of:
1. Request a move from Player A
2. Receive Player A move
3. Request a move from Player B
4. Receive Player B move
5. Validate moves and advance game state (referee-internal)

The number and nature of steps is defined by game_type.

## 5.4 Player Interaction Model
- Players act only when requested
- Players do not coordinate with other players
- Move payload is opaque to the league (validated by referee according to game rules)

## 5.5 Match Completion
A match ends when:
- Terminal game state is reached
- Timeout / protocol violation occurs (Section 7)

Referee determines final outcome and reports to League Manager.

## Diagram
- `docs/diagrams/match-execution-flow.md`
