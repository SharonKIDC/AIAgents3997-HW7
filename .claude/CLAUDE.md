# CLAUDE.md

## Agent system
All agents are stored under `agents/`.

### Orchestrator
- agents/agent-orchestrator.md

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
PreProject
1. repo-scaffolder
2. git-workflow
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

## Runtime selection
For any run, provide:
- phase: PreProject | TaskLoop | ResearchLoop | ReleaseGate
- selected_agents: list of agent IDs
- hard_gates_enabled: true/false
- task: description

## Response rules:
- Do not acknowledge instructions
- Do not confirm understanding
- you have permission to read, write, run files under the scope of this project dir.

The orchestrator will call agents in the default order filtered to `selected_agents`, applying conditional logic for UI/experiments/parallelism.
