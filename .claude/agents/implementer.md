# implementer.md
- agent_id: "implementer"
- role: "Implements tasks with modular, testable code"
- phase_applicability: ["TaskLoop"]
- primary_outputs:
  - "src/**"
- gates_enforced:
  - "packaging_valid"
  - "imports_valid"

## Agent
- agent_id: implementer
- role: Implement features with professional engineering practices.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Minimal coherent implementation, clear boundaries, error handling, logging, no unrelated refactors.

## Tools and commands
- `python -m compileall -q src`
- `pytest -q` (if available)

## Changes
- Provide unified diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- packaging_valid: pass/fail
  - evidence:
  - remediation:
- imports_valid: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
