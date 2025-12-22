# Section 7 - Timeouts, Errors, and Recovery

## 7.1 Purpose
Defines failure handling, including timeouts, retries, and authoritative outcomes.

## 7.2 Timeout Enforcement
Timeouts apply to:
- Registration requests
- Match join acknowledgements
- Move responses
- Result reporting

Enforcement:
- League Manager enforces league-level timeouts
- Referees enforce match-level timeouts

## 7.3 Error Classification
Errors are classified as:
- League-level errors (produced by League Manager)
- Match-level errors (produced by Referees)

## 7.4 Recovery Rules (High Level)
- Retries are bounded (policy defined by configuration)
- After retry exhaustion, the authoritative agent decides the outcome (technical loss or match termination)
- All failures and decisions are logged

## 7.5 Non-Goals
This section does not enumerate all error codes; it defines behavior and authority.
