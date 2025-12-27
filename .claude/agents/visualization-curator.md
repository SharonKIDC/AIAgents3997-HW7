# visualization-curator.md
- agent_id: "visualization-curator"
- role: "Produces high-quality labeled plots and exports"
- phase_applicability: ["ResearchLoop", "ReleaseGate"]
- primary_outputs:
  - "results/**"
- gates_enforced:
  - "figures_present"

## Agent
- agent_id: visualization-curator
- role: Make visuals submission-ready.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
**CRITICAL - Must create visualizations:**

1. **Token Consumption Visualization** (results/token_consumption.png):
   - Parse docs/development/PROMPT_LOG.md for development activity
   - Create bar chart or timeline showing token usage by phase
   - Include: PreProject, TaskLoop, ResearchLoop, ReleaseGate phases
   - Add trend lines if applicable
   - Export as high-resolution PNG (300 DPI minimum)

2. **Cost Analysis Charts** (if LLM usage in production):
   - Production cost projections
   - Cost per user/transaction estimates
   - Budget scenarios visualization

**Required elements for ALL plots:**
- Clear, descriptive titles
- Axis labels with units
- Legends (if multiple series)
- Grid lines for readability
- Professional color scheme
- High resolution export (300+ DPI)
- Source data annotation

**Output requirements:**
- Save to results/ directory
- Reference from docs/development/PROMPT_LOG.md or relevant notebook
- Include generation code/script for reproducibility
- Add README.md in results/ explaining each visualization

**Validation:**
- All plots have titles and labels
- Images are high resolution (check file size > 100KB for complex plots)
- At least one token consumption visualization exists

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- figures_present: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
