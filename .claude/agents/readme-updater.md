# readme-updater.md
- agent_id: "readme-updater"
- role: "Updates README when usage/config/workflows change"
- phase_applicability: ["TaskLoop", "ReleaseGate"]
- primary_outputs:
  - "README.md"
- gates_enforced:
  - "readme_updated_if_needed"

## Agent
- agent_id: readme-updater
- role: Keep README correct and user-ready.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Detect impact on user-facing docs and update minimal relevant README sections.
- Verify examples.

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- readme_updated_if_needed: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
