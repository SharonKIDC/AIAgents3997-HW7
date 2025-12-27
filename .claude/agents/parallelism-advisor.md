# parallelism-advisor.md
- agent_id: "parallelism-advisor"
- role: "Defines and validates safe parallelism strategy (mp/mt/async), thread safety, and resource handling"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "docs/PARALLELISM.md"
- gates_enforced:
  - "parallelism_strategy_defined"
  - "thread_safety_checked"

## Agent
- agent_id: parallelism-advisor
- role: Ensure parallel processing strategy is correct and safe.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Workload classification, strategy choice, worker sizing, synchronization, cleanup rules, shared state mitigation.

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- parallelism_strategy_defined: pass/fail
  - evidence:
  - remediation:
- thread_safety_checked: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
