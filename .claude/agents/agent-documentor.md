# agent-documentor.md
- agent_id: "agent-documentor"
- role: "Post-task doc coherence agent: aligns README/PRD/Architecture/Expected Results with code changes"
- phase_applicability: ["TaskLoop", "ReleaseGate"]
- primary_outputs:
  - "README.md"
  - "docs/EXPECTED_RESULTS.md"
  - "docs/Architecture.md (if needed)"
  - "docs/PRD.md (if needed)"
- gates_enforced:
  - "readme_updated_if_needed"
  - "expected_results_updated"
  - "docstrings_complete"

## Agent
- agent_id: agent-documentor
- role: Keep documentation aligned after each task.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Update docs impacted by API/config/workflow/criteria changes.
- Ensure docstrings remain aligned.

## Tools and commands
- `pytest -q`

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
- expected_results_updated: pass/fail
  - evidence:
  - remediation:
- docstrings_complete: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
