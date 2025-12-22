# unit-test-writer.md
- agent_id: "unit-test-writer"
- role: "Writes unit tests, targets coverage threshold, documents expected results"
- phase_applicability: ["TaskLoop", "ReleaseGate"]
- primary_outputs:
  - "tests/**"
  - "docs/EXPECTED_RESULTS.md"
- gates_enforced:
  - "tests_present"
  - "coverage_target"
  - "edge_cases_covered"
  - "expected_results_updated"

## Agent
- agent_id: unit-test-writer
- role: Add robust tests and document expected outcomes.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Add deterministic tests for normal/edge/error paths.
- Update EXPECTED_RESULTS.md accordingly.

## Tools and commands
- `pytest -q`
- `pytest --cov=src --cov-report=term-missing` (if configured)

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- tests_present: pass/fail
  - evidence:
  - remediation:
- coverage_target: pass/fail
  - evidence:
  - remediation:
- edge_cases_covered: pass/fail
  - evidence:
  - remediation:
- expected_results_updated: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
