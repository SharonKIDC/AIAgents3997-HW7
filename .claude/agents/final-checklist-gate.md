# final-checklist-gate.md
- agent_id: "final-checklist-gate"
- role: "Verifies required submission artifacts and documents final validation commands; blocks release when gates fail"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "docs/development/FINAL_CHECKLIST.md"
- gates_enforced:
  - "final_checklist_pass"

## Agent
- agent_id: final-checklist-gate
- role: Ensure every required submission element exists and is coherent.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Verify presence/completeness of required and conditional artifacts.
- Produce checklist and validation commands.

## Tools and commands
- `pytest -q`
- `python -m pip install -e .`
- `python -m compileall -q src`

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- final_checklist_pass: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
