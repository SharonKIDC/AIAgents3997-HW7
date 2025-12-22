# expected-results-recorder.md
- agent_id: "expected-results-recorder"
- role: "Maintains expected test results documentation and run instructions"
- phase_applicability: ["TaskLoop", "ReleaseGate"]
- primary_outputs:
  - "docs/EXPECTED_RESULTS.md"
- gates_enforced:
  - "expected_results_updated"

## Agent
- agent_id: expected-results-recorder
- role: Keep expected results doc accurate.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Ensure EXPECTED_RESULTS.md includes how-to-run, expected outcomes, key test cases, limitations.

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- expected_results_updated: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
