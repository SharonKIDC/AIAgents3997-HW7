# Section 4 - Scheduling and Round Management

## 4.1 Purpose
Defines how the league creates matches, groups them into rounds, and assigns them to referees.

The scheduling mechanism must:
- Be deterministic
- Support multiple referees
- Be game-agnostic
- Guarantee that all required matches are played exactly once

## 4.2 Scheduling Model
The league uses a Round-Robin model.

For N registered players:
- Each player plays every other player exactly once
- Total matches: N * (N - 1) / 2

## 4.3 Rounds
- Matches are grouped into rounds for orchestration and reporting
- All matches in a round may execute concurrently if referees are available
- No player appears in more than one match per round

## 4.4 Match Assignment
- The League Manager assigns each match to exactly one referee
- Referees must be ACTIVE and idle
- Assignment includes: match_id, round_id, player_ids, game_type

If no referee is available, the match remains pending until assignment is possible.

## 4.5 Round Announcement
The League Manager announces round start to:
- Assigned referees
- Participating players

Announcement includes:
- round_id
- list of matches (match_id, players, referee, game_type)

## 4.6 Determinism Requirement
Given the same player set, referee set, and configuration, the schedule must be identical.

## Diagram
- `docs/diagrams/scheduling-flow.md`
