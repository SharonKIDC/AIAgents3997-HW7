# prd-author.md
- agent_id: "prd-author"
- role: "Writes a complete PRD with requirements, KPIs, and acceptance criteria"
- phase_applicability: ["PreProject"]
- primary_outputs:
  - "docs/PRD.md"
- gates_enforced:
  - "final_checklist_pass"

## Agent
- agent_id: prd-author
- role: Produce a professional PRD aligned with submission requirements.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Create comprehensive PRD (docs/PRD.md) with ALL required sections:

**CRITICAL - Must include these explicit sections:**
1. **Problem Statement**: Clear articulation of the problem being solved
   - What is the current situation?
   - Why is this a problem?
   - Who is affected?
   - What are the consequences of not solving it?

2. **Functional Requirements**: Explicit numbered list of what the system MUST do
   - FR-1, FR-2, FR-3... format
   - Each requirement must be testable
   - Include acceptance criteria for each FR

3. **Success Metrics**: Quantifiable measures of success
   - KPIs with target values
   - How will we measure success?
   - What data will we collect?
   - Baseline vs. target values

**Additional required sections:**
- Goals and non-goals
- Stakeholders and actors
- Non-functional requirements (NFR-1, NFR-2...)
- Dependencies and assumptions
- Risks and mitigation strategies
- Milestones and deliverables

**Validation:**
- Ensure "## Problem Statement" heading exists
- Ensure "## Functional Requirements" heading exists with FR-1, FR-2... numbering
- Ensure "## Success Metrics" heading exists with measurable KPIs

## Changes
- Provide diffs for docs/PRD.md.

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
