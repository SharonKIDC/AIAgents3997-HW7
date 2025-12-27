# cost-analyzer.md
- agent_id: "cost-analyzer"
- role: "Produces cost/token analysis, assumptions, scenarios, and monitoring controls"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "docs/COSTS.md"
- gates_enforced:
  - "final_checklist_pass"

## Agent
- agent_id: cost-analyzer
- role: Provide cost estimation and monitoring plan.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
**CRITICAL - Must create TWO files:**

1. **docs/COSTS.md** - Detailed cost analysis:
   - Token consumption analysis from development (read docs/development/PROMPT_LOG.md)
   - Cost breakdown by phase (PreProject, TaskLoop, ResearchLoop, ReleaseGate)
   - Cost per agent invocation
   - Total tokens consumed during development
   - Estimated API costs (tokens × rate)
   - Production cost estimates (ongoing usage)
   - Cost optimization recommendations

2. **docs/BUDGET.md** - Budget planning and controls:
   - Development budget (actual costs incurred)
   - Production budget projections
   - Cost scenarios (low/medium/high usage)
   - Monitoring and alerting thresholds
   - Budget controls and limits
   - Cost per user/transaction estimates

**Data sources:**
- Read docs/development/PROMPT_LOG.md for development activity
- Read src/** for API calls and LLM usage patterns
- Calculate token estimates from codebase size
- Include assumptions and calculation methods

**Validation:**
- Both files must exist
- Include numerical estimates (not just placeholders)
- Show calculation methodology
- Include at least 3 cost scenarios

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
