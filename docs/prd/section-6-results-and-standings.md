# Section 6 - Result Reporting and Standings

## 6.1 Purpose
Defines how match results are reported and how league standings are computed and published.

## 6.2 Match Result Reporting
- Referees report results to the League Manager
- Exactly one result report is accepted per match_id
- Referee reports are authoritative for outcome

A result report includes:
- match_id, round_id, league_id
- player_ids
- per-player outcome (win/loss/draw)
- points awarded
- optional game-specific metadata (opaque to league)

Normative example:
- `docs/protocol/examples/match_result_report.json`

## 6.3 Standings Computation
Standings are computed deterministically from accepted match results.

Tie-breaking order is deterministic and documented by the league (initially: points, wins, draws).

## 6.4 Publication
- Standings are queryable by players
- Standings are immutable per round once published
