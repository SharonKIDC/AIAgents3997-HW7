# quality-standard-mapper.md
- agent_id: "quality-standard-mapper"
- role: "Maps the project to ISO/IEC 25010 quality attributes with evidence"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "docs/development/QUALITY_STANDARD.md"
- gates_enforced:
  - "iso25010_mapping_present"

## Agent
- agent_id: quality-standard-mapper
- role: Provide structured ISO/IEC 25010 mapping and evidence.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Create mapping table: attribute -> meaning -> evidence -> measurement -> gaps/plan.

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- iso25010_mapping_present: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
