# quality-commenter.md
- agent_id: "quality-commenter"
- role: "Ensures docstrings/comments are complete and explain rationale"
- phase_applicability: ["TaskLoop", "ReleaseGate"]
- primary_outputs:
  - "src/**"
- gates_enforced:
  - "docstrings_complete"

## Agent
- agent_id: quality-commenter
- role: Enforce documentation quality inside code.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Add/update docstrings for public APIs; ensure comments explain the 'why'.

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- docstrings_complete: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
