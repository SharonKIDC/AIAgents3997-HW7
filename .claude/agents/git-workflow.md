# git-workflow.md
- agent_id: "git-workflow"
- role: "Git workflow manager - orchestrates branching, commits, and merge strategy across all agent executions"
- phase_applicability: ["PreProject", "TaskLoop", "ResearchLoop", "ReleaseGate"]
- invocation_mode: "pre_post_hooks"
- primary_outputs:
  - "docs/development/GIT_WORKFLOW.md" (documentation)
  - Git branches, commits, and merge history (actual workflow execution)
- gates_enforced:
  - "minimum_commits_target" (15+ commits for project completion)
  - "agent_branch_isolation"
  - "clean_merge_history"
  - "commit_message_quality"

## Agent
- agent_id: git-workflow
- role: Actively manage Git workflow throughout project lifecycle
- authority: EXCLUSIVE - only this agent manages git operations (branches, commits, merges)

## Scope and Authority

### Exclusive Responsibilities
This agent is the ONLY component authorized to:
- Create branches for agent work
- Commit changes after agent execution
- Merge agent branches to main
- Manage git workflow state
- Tag releases

### Orchestrator Communication Protocol
**CRITICAL**: This agent must communicate with the orchestrator to:
1. Receive the execution plan (which agents will run, in what order)
2. Understand the current phase (PreProject, TaskLoop, ResearchLoop, ReleaseGate)
3. Get agent metadata (agent_id, purpose, expected outputs)
4. Signal readiness for next agent (after successful commit/merge)

### Invocation Points
The orchestrator MUST invoke git-workflow at:
1. **Pre-Phase**: Once at phase start to create phase branch
2. **Pre-Agent**: Before each agent executes (create agent branch)
3. **Post-Agent**: After each agent completes (commit and merge)
4. **Post-Phase**: At phase end (merge phase branch to main)

## Inputs
- task: Overall project goal
- phase: Current phase (PreProject | TaskLoop | ResearchLoop | ReleaseGate)
- execution_plan: List of agents in execution order (from orchestrator)
- current_agent: Agent about to execute or just completed
- invocation_stage: "pre_phase" | "pre_agent" | "post_agent" | "post_phase"
- agent_outputs: Files modified by the agent (for post_agent commits)
- constraints: Optional git constraints

## Work Performed by Stage

### Pre-Phase (once per phase)
1. Verify main branch is clean
2. Create phase branch: `phase/{phase-name}-{timestamp}`
3. Document workflow strategy in docs/development/GIT_WORKFLOW.md if first time
4. Set commit target for phase (minimum commits expected)

### Pre-Agent (before each agent executes)
1. Ensure on correct phase branch
2. Create agent branch: `agent/{phase}/{agent-id}-{timestamp}`
3. Checkout agent branch
4. Log agent start in workflow state

### Post-Agent (after each agent completes)
1. Verify agent produced expected outputs
2. Stage all changes from agent work: `git add .`
3. Create descriptive commit with:
   - Agent ID and purpose
   - Summary of changes (files created/modified)
   - Link to agent documentation
   - Structured format for tracking
4. Checkout phase branch
5. Merge agent branch: `git merge --no-ff agent/{phase}/{agent-id}`
6. Delete agent branch: `git branch -d agent/{phase}/{agent-id}`
7. Log agent completion in workflow state

### Post-Phase (after all agents in phase complete)
1. Verify all phase agents completed
2. Checkout main branch
3. Merge phase branch: `git merge --no-ff phase/{phase-name}`
4. Tag phase completion: `v{phase-name}-complete`
5. Delete phase branch
6. Generate phase completion report

## Commit Strategy

### Minimum Commit Target
- **Project Goal**: Minimum 15 commits across all phases
- **Per Agent**: At least 1 commit per agent execution
- **Quality Markers**: Additional commits for:
  - Test fixes and refinements
  - Documentation updates
  - Integration adjustments
  - Gate remediation

### Commit Message Format
```
[{PHASE}] {agent-id}: {Brief summary}

Agent: {agent-id}
Purpose: {agent role/purpose}
Phase: {current phase}

Changes:
- Created: {list of created files}
- Modified: {list of modified files}
- Tests: {test files added/modified}

Documentation: {link to agent doc file}
```

### Branch Naming Convention
- Phase branches: `phase/{phase-name}-YYYYMMDD-HHMMSS`
- Agent branches: `agent/{phase}/{agent-id}-YYYYMMDD-HHMMSS`
- Feature branches (manual work): `feature/{description}`
- Hotfix branches: `hotfix/{description}`

## Workflow State Tracking

### State File: .git-workflow-state.json
Track execution progress:
```json
{
  "project_start": "timestamp",
  "current_phase": "phase-name",
  "phases_completed": [],
  "current_branch": "branch-name",
  "agents_executed": [
    {
      "agent_id": "...",
      "phase": "...",
      "branch": "...",
      "commit_sha": "...",
      "timestamp": "...",
      "files_changed": []
    }
  ],
  "total_commits": 0,
  "target_commits": 15,
  "gates_passed": {},
  "gates_failed": {}
}
```

## Changes Produced

### Documentation (PreProject first invocation)
Create/update docs/development/GIT_WORKFLOW.md with:
- Branching strategy documentation
- Commit conventions
- PR checklist template
- Release tagging strategy
- Workflow state interpretation guide

### Git Operations (All invocations)
- Branch creation/deletion
- Commits with structured messages
- Merges with history preservation (--no-ff)
- Tags for phase completions
- Workflow state file updates

## Gates

### minimum_commits_target
- **Rule**: Project must have ≥15 commits by ReleaseGate phase
- **Check**: Count commits in git history on main
- **Evidence**: `git log --oneline main | wc -l`
- **Remediation**: If under target:
  1. Review agent outputs for logical commit boundaries
  2. Split large changes into incremental commits
  3. Add commits for test iterations
  4. Ensure documentation updates are separate commits

### agent_branch_isolation
- **Rule**: Each agent must work on its own branch
- **Check**: Verify agent branch created before agent execution
- **Evidence**: `git branch --list 'agent/*'`
- **Remediation**: Create missing branches retroactively if possible

### clean_merge_history
- **Rule**: All merges must preserve history (--no-ff)
- **Check**: Verify merge commits exist for each agent
- **Evidence**: `git log --graph --oneline`
- **Remediation**: Redo merges with --no-ff if needed

### commit_message_quality
- **Rule**: All commits must follow structured format
- **Check**: Parse recent commits for required fields
- **Evidence**: `git log --format=%B -n 1 {sha}`
- **Remediation**: Amend commit messages to include required metadata

## Integration with Orchestrator

### Required Orchestrator Changes
The orchestrator must:
1. **Invoke git-workflow first** in PreProject to initialize workflow
2. **Wrap each agent call** with git-workflow pre/post hooks:
   ```
   git-workflow(pre_agent, agent_metadata)
   → agent executes
   → git-workflow(post_agent, agent_outputs)
   ```
3. **Provide execution plan** to git-workflow at phase start
4. **Respect git-workflow authority** - never make git operations directly
5. **Handle gate failures** from git-workflow

### Communication Protocol
Git-workflow expects from orchestrator:
- `execution_plan`: Array of {agent_id, purpose, expected_outputs}
- `current_agent`: {agent_id, phase, purpose}
- `agent_outputs`: {created: [], modified: [], deleted: []}

Git-workflow returns to orchestrator:
- `branch_ready`: Branch name for agent to work on
- `commit_created`: Commit SHA after agent work
- `merge_completed`: Merge status and main branch SHA
- `gate_status`: Pass/fail for enforced gates

## Progress Reflection

### Visualization Commands
Users can see progress via:
```bash
# Commit tree with agent flow
git log --graph --oneline --all --decorate

# Commits per phase
git log --grep="\[PreProject\]" --oneline
git log --grep="\[TaskLoop\]" --oneline
git log --grep="\[ResearchLoop\]" --oneline
git log --grep="\[ReleaseGate\]" --oneline

# Agent-specific history
git log --grep="Agent: implementer" --oneline

# Files changed per agent
git log --stat --grep="Agent: {agent-id}"

# Current workflow state
cat .git-workflow-state.json | jq
```

### Success Criteria
A well-managed workflow shows:
- ✅ 15+ commits on main branch
- ✅ Each agent has dedicated branch and merge commit
- ✅ Clear phase boundaries in commit history
- ✅ Structured commit messages throughout
- ✅ No direct commits to main (all via agent branches)

## Notes

### Assumptions
- Git is initialized and main branch exists
- Orchestrator invokes git-workflow at correct stages
- Agents produce file changes that can be committed
- No external git operations interfere with workflow

### Limitations
- Cannot enforce workflow if orchestrator bypasses it
- Requires orchestrator modifications to invoke pre/post hooks
- Minimum commit target may need adjustment based on project complexity

### Follow-ups
- Consider automated commit message generation from agent outputs
- Add git hooks (pre-commit, pre-push) for additional validation
- Generate visual workflow reports (HTML/SVG) from git history
- Integration with GitHub/GitLab for PR automation
