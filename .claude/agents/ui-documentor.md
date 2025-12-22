# ui-documentor.md
- agent_id: "ui-documentor"
- role: "Creates UI documentation with screenshots/workflows/states/accessibility notes"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "docs/UI.md"
  - "docs/assets/ui/**"
- gates_enforced:
  - "ui_docs_present"

## Agent
- agent_id: ui-documentor
- role: Produce submission-grade UI documentation.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Document screens/states/workflows/errors/accessibility.
- Add screenshot placeholders and capture instructions.

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- ui_docs_present: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
