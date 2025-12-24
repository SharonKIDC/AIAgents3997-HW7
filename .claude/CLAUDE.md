# CLAUDE.md

## Agent system
All agents are stored under `agents/`.

### Orchestrators
- agents/agent-orchestrator.md (main orchestrator for PRD-based greenfield projects)
- agents/continuous-dev-orchestrator.md (for ad-hoc tasks, fixes, improvements, ongoing development)

### Available agents
PreProject
- agents/repo-scaffolder.md
- agents/git-workflow.md
- agents/config-security-baseline.md
- agents/prd-author.md
- agents/architecture-author.md
- agents/readme-author.md
- agents/prompt-log-initializer.md
- agents/python-env-setup.md

TaskLoop
- agents/implementer.md
- agents/quality-commenter.md
- agents/unit-test-writer.md
- agents/edge-case-defender.md
- agents/expected-results-recorder.md
- agents/readme-updater.md
- agents/prompt-log-updater.md
- agents/agent-documentor.md

ResearchLoop
- agents/sensitivity-analysis.md
- agents/results-notebook.md
- agents/visualization-curator.md

ReleaseGate
- agents/python-packager.md
- agents/parallelism-advisor.md
- agents/building-block-reviewer.md
- agents/ux-heuristics-reviewer.md
- agents/ui-documentor.md
- agents/cost-analyzer.md
- agents/extensibility-planner.md
- agents/quality-standard-mapper.md
- agents/final-checklist-gate.md
- agents/python-env-setup.md

## Default execution order

**CRITICAL**: git-workflow is invoked automatically at pre/post hooks for ALL phases.
The orchestrator wraps each agent execution with git-workflow calls.

PreProject
1. repo-scaffolder
2. git-workflow (documentation creation)
3. config-security-baseline
4. prd-author
5. architecture-author
6. readme-author
7. prompt-log-initializer

TaskLoop
1. implementer
2. quality-commenter
3. unit-test-writer
4. edge-case-defender
5. expected-results-recorder
6. readme-updater (conditional)
7. prompt-log-updater
8. agent-documentor (optional)

ResearchLoop
1. sensitivity-analysis
2. results-notebook
3. visualization-curator
4. prompt-log-updater

ReleaseGate
1. python-packager
2. parallelism-advisor (conditional)
3. building-block-reviewer
4. ux-heuristics-reviewer (conditional)
5. ui-documentor (conditional)
6. cost-analyzer (conditional on LLM usage)
7. extensibility-planner
8. quality-standard-mapper
9. final-checklist-gate

## Git Workflow Management

The git-workflow agent has EXCLUSIVE authority over all git operations:
- Creates branches for each phase and agent
- Commits changes after each agent execution
- Merges agent branches to phase branches, then to main
- Enforces minimum 15 commits across project lifecycle
- Tracks workflow state in .git-workflow-state.json

**Invocation pattern for each phase:**
```
git-workflow(pre_phase)
  → git-workflow(pre_agent) → agent-1 → git-workflow(post_agent)
  → git-workflow(pre_agent) → agent-2 → git-workflow(post_agent)
  → ...
git-workflow(post_phase)
```

**Branch structure:**
- `phase/{phase-name}-{timestamp}` - one per phase
- `agent/{phase}/{agent-id}-{timestamp}` - one per agent execution
- All merges use `--no-ff` to preserve history

**Commit target:** Minimum 15 commits by project completion

## Orchestrator Selection Guide

### Use agent-orchestrator.md when:
- Starting a new project from scratch
- Implementing features defined in PRD
- Need full PreProject → TaskLoop → ResearchLoop → ReleaseGate flow
- Creating initial releases
- Major architectural work

### Use continuous-dev-orchestrator.md when:
- Fixing bugs reported by users
- Making small improvements or refactoring
- Adding small features (not in original PRD)
- Adapting to changing requirements
- Post-release maintenance and iterations
- Quick development cycles

**CRITICAL**: Both orchestrators use the SAME git-workflow integration and agent orchestration logic, ensuring consistent process and quality standards for ALL development work.

## Runtime selection

### For agent-orchestrator.md
Provide:
- phase: PreProject | TaskLoop | ResearchLoop | ReleaseGate
- selected_agents: list of agent IDs (git-workflow auto-included)
- hard_gates_enabled: true/false
- task: description (from PRD)

### For continuous-dev-orchestrator.md
Provide:
- task: user's plain-English description of fix/improvement/change
- scope_hint: optional hint about affected codebase areas
- urgency: "standard" | "high"
- hard_gates_enabled: true/false (recommended: true for production)
- constraints: optional (e.g., "backward compatible")

Phase is automatically set to "ContinuousDev" and appropriate agents are selected based on task analysis.

## Response rules:
- Do not acknowledge instructions
- Do not confirm understanding
- you have permission to read, write, run files under the scope of this project dir.

The orchestrator will call agents in the default order filtered to `selected_agents`, applying conditional logic for UI/experiments/parallelism.
