# extensibility-planner.md
- agent_id: "extensibility-planner"
- role: "Defines extension points and plugin conventions with interfaces and examples"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "docs/EXTENSIBILITY.md"
  - "IMPROVEMENT_PLAN.md"
- gates_enforced:
  - "extension_points_documented"

## Agent
- agent_id: extensibility-planner
- role: Make the project easy to extend safely.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
**CRITICAL - Must create TWO files:**

1. **docs/EXTENSIBILITY.md** - Extension point documentation:
   - Identify extension axes (plugins, games, strategies, etc.)
   - Define interfaces and abstract base classes
   - Document extension points and hooks
   - Provide extension examples
   - Safety guidelines and validation
   - Version compatibility considerations

2. **IMPROVEMENT_PLAN.md** - Future improvements and roadmap:
   - Short-term improvements (next 1-3 months)
   - Long-term enhancements (3-12 months)
   - Known limitations and how to address them
   - Performance optimization opportunities
   - Feature requests and priorities
   - Technical debt items
   - Scalability improvements
   - Security enhancements
   - UX/usability improvements

**For IMPROVEMENT_PLAN.md structure:**
```markdown
# Improvement Plan

## Immediate Priorities (Next Month)
- [ ] Item 1 with justification
- [ ] Item 2 with justification

## Short-term (1-3 Months)
...

## Long-term (3-12 Months)
...

## Technical Debt
...

## Performance Optimizations
...
```

**Validation:**
- Both files must exist
- IMPROVEMENT_PLAN.md has at least 10 concrete items
- Items are prioritized and categorized
- Each item has justification or impact description

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- extension_points_documented: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
