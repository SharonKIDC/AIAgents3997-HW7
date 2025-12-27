# edge-case-defender.md
- agent_id: "edge-case-defender"
- role: "Hardens code with validation, clear errors, and graceful degradation"
- phase_applicability: ["TaskLoop", "ReleaseGate"]
- primary_outputs:
  - "src/**"
- gates_enforced:
  - "edge_cases_covered"

## Agent
- agent_id: edge-case-defender
- role: Systematically identify and handle edge cases.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Enumerate boundary conditions and failure modes.
- Add input validation, error handling, non-sensitive logs.
- Ensure tests exist or request them.

## Tools and commands
- `pytest -q`

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- edge_cases_covered: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
