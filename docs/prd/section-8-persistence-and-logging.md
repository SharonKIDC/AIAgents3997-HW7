# Section 8 - Persistence and Logging

## 8.1 Purpose
Ensures auditability and replayability of the league.

## 8.2 Persistence Requirements
The system must persist:
- Registrations (players and referees)
- Schedule (rounds and matches)
- Match results
- Standings snapshots
- Errors and violations

## 8.3 Logging Requirements
- All protocol messages are logged (request/response)
- Logs are append-only
- Logs include timestamps and conversation_id for correlation

## 8.4 Determinism Guarantee
Given persisted data and logs, the league state must be reconstructible.
