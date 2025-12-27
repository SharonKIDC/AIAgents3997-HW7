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

### ⚠️ CRITICAL ENFORCEMENT RULES ⚠️

**NEVER bypass this workflow with single massive commits!**

❌ **FORBIDDEN**: Creating one commit with all changes from multiple agents
❌ **FORBIDDEN**: Direct commits to main without branching
❌ **FORBIDDEN**: Skipping agent branch creation
❌ **FORBIDDEN**: Merging without --no-ff
❌ **FORBIDDEN**: Batching multiple agent outputs into one commit

✅ **REQUIRED**: One commit per agent execution minimum
✅ **REQUIRED**: Agent branch for each agent
✅ **REQUIRED**: --no-ff merges to preserve history
✅ **REQUIRED**: Structured commit messages
✅ **REQUIRED**: Minimum 15 commits across project (target: 1 per agent × agents)

**Violation Consequences**:
- Loss of traceability (cannot see which agent did what)
- Cannot rollback individual agent changes
- Defeats the purpose of multi-agent orchestration
- Makes git history useless for learning and debugging
- Fails minimum_commits_target gate

**Enforcement**:
- If orchestrator is not being used, ANY commits must STILL follow ONE COMMIT PER LOGICAL UNIT
- If creating multiple files (>3), they MUST be in separate commits by category:
  - Config files (1 commit)
  - Documentation files (1-3 commits by type)
  - Code files (1 commit per module)
  - Test files (1 commit)
  - CI/CD files (1 commit)
- NEVER bundle 15 files in one commit
- NEVER add 3,779 lines in one commit

### Exclusive Responsibilities
This agent is the ONLY component authorized to:
- Create branches for agent work
- Commit changes after agent execution
- Merge agent branches to main
- Manage git workflow state
- Tag releases

**IF git-workflow agent is not being invoked by orchestrator:**
- Human or AI must STILL follow the spirit of the workflow
- Break work into logical commits (one per major task/file category)
- Use clear, structured commit messages
- Target minimum 5-10 commits for any significant work
- Create branches for non-trivial changes

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
2. **CRITICAL: Run quality checks before committing**:
   - `pylint src/ --score=y` (must achieve 10/10)
   - `black --check src/ tests/` (must pass)
   - `isort --check-only --profile black src/ tests/` (must pass)
   - `ruff check src/ tests/` (must pass)
   - `pytest tests/` (all tests must pass)
   - If any checks fail, fix issues before committing
3. **Verify .gitignore compliance**:
   - Check `git status` for temp files (*.log, *.tmp, bandit-report.json, etc.)
   - If temp files appear, update .gitignore FIRST, then commit .gitignore separately
   - Never commit: __pycache__/, .venv/, *.pyc, build artifacts, test reports
4. Stage changes from agent work: `git add .` (or selective staging)
5. Create descriptive commit with:
   - Conventional commit format (see below)
   - Agent ID and purpose
   - Summary of changes (files created/modified)
   - Link to agent documentation
   - Structured format for tracking
6. **Post-commit validation**:
   - Verify commit created: `git log -1 --oneline`
   - Verify no unstaged changes remain: `git status`
   - Verify temp files not committed: `git show --name-only`
7. Checkout phase branch
8. Merge agent branch: `git merge --no-ff agent/{phase}/{agent-id}`
9. Delete agent branch: `git branch -d agent/{phase}/{agent-id}`
10. Log agent completion in workflow state

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
- **Per Agent**: At least 1 commit per agent execution (MANDATORY)
- **Quality Markers**: Additional commits for:
  - Test fixes and refinements
  - Documentation updates
  - Integration adjustments
  - Gate remediation

### ⚠️ COMMIT BREAKDOWN RULES (MANDATORY)

When working on multiple tasks/agents without orchestrator:

**NEVER create 1 commit for 15 files!**

Instead, create SEPARATE commits for:

1. **Configuration Changes** (1 commit):
   - .env.example, config.yaml, etc.
   - Message: "feat(config): add environment and application configuration"

2. **Cost/Budget Analysis** (1 commit):
   - docs/COSTS.md, docs/BUDGET.md
   - Message: "docs(costs): add cost analysis and budget planning"

3. **Contributing Guidelines** (1 commit):
   - docs/CONTRIBUTING.md
   - Message: "docs(contributing): add contribution guidelines"

4. **CI/CD Setup** (1 commit):
   - .pre-commit-config.yaml, .github/workflows/ci.yml
   - Message: "ci: add pre-commit hooks and CI pipeline"

5. **Terminal Examples** (1 commit):
   - docs/examples/TERMINAL_EXAMPLES.md
   - Message: "docs(examples): add terminal output examples"

6. **Visualizations** (1 commit):
   - results/*.png, scripts/generate_token_visualization.py
   - Message: "feat(viz): add token consumption visualizations"

7. **User Documentation** (1 commit):
   - PROMPT_BOOK.md
   - Message: "docs(prompts): add user-facing prompt guide"

8. **Planning Documentation** (1 commit):
   - IMPROVEMENT_PLAN.md
   - Message: "docs(planning): add improvement roadmap"

9. **PRD Updates** (1 commit):
   - docs/PRD.md additions
   - Message: "docs(prd): add problem statement, FRs, and success metrics"

**Minimum**: 9 commits for 9 different categories of work
**Target**: 10-15 commits when including iterations and fixes

**Rationale**:
- Each commit represents ONE agent's output or ONE logical unit of work
- Enables rollback of specific changes without affecting others
- Creates meaningful git history for learning and debugging
- Satisfies minimum_commits_target gate

### Commit Message Format

**Use Conventional Commits Format:**
```
<type>(<scope>): <brief summary>

<detailed description>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (black, isort)
- `refactor`: Code restructuring without behavior change
- `test`: Test additions or modifications
- `chore`: Build process, dependencies, tooling
- `ci`: CI/CD pipeline changes
- `perf`: Performance improvements

**Examples:**
```
feat(auth): add JWT token validation

Implement token validation middleware for API endpoints.
- Added AuthManager class
- Created token validation tests
- Updated API documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

```
fix(ci): install package in editable mode to fix import errors

Add 'pip install -e .' to the test job dependencies to ensure
the src module is available when running pytest.

Fixes:
  ModuleNotFoundError: No module named 'src'
  ImportError while loading conftest

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

```
refactor: achieve pylint 10/10 by clearing disable list and fixing all issues

- Cleared all items from .pylintrc disable list
- Created AgentServerBase to eliminate player/referee duplication
- Created PlayerRanking dataclass to reduce method arguments
- Added cli_helpers.py for shared CLI argument parsing
- All 173 tests passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Agent Execution Format (when using orchestrator):**
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
- Bugfix branches: `bugfix/{issue-number}-{description}`

## Feature Branch Workflow (Continuous Development)

**For non-orchestrated work (bug fixes, improvements, features):**

### Process:
1. **Create feature branch from main**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/add-user-auth
   ```

2. **Make changes with quality gates**:
   ```bash
   # Make your changes
   # Run quality checks BEFORE each commit
   pylint src/ --score=y  # Must be 10/10
   black src/ tests/
   isort --profile black src/ tests/
   ruff check src/ tests/
   pytest tests/  # All must pass

   # Commit with conventional format
   git add <specific-files>  # Stage selectively
   git commit -m "feat(auth): add user authentication module

   - Created AuthManager class
   - Added JWT token validation
   - Tests: 15 new tests, all passing

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

3. **Multiple commits for complex features**:
   - **DO**: Break into logical commits
     - Commit 1: `feat(auth): add AuthManager base class`
     - Commit 2: `feat(auth): add JWT token validation`
     - Commit 3: `test(auth): add comprehensive auth tests`
     - Commit 4: `docs(auth): document authentication flow`
   - **DON'T**: One massive commit with all changes

4. **Push and create PR**:
   ```bash
   git push origin feature/add-user-auth
   gh pr create --title "feat(auth): add user authentication" \
                --body "$(cat <<'EOF'
   ## Summary
   - Implements JWT-based authentication
   - Adds AuthManager for token validation
   - Includes comprehensive test coverage

   ## Test Plan
   - [x] All 173 existing tests pass
   - [x] Added 15 new authentication tests
   - [x] Pylint score: 10/10
   - [x] All formatting checks pass
   - [x] CI pipeline passes

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

5. **Merge to main**:
   ```bash
   # After PR approval and CI passing
   git checkout main
   git pull origin main
   git merge --no-ff feature/add-user-auth
   git push origin main
   git branch -d feature/add-user-auth
   ```

### Quality Checklist (MANDATORY before push):
- [ ] `pylint src/ --score=y` shows 10.00/10
- [ ] `black --check src/ tests/` passes
- [ ] `isort --check-only --profile black src/ tests/` passes
- [ ] `ruff check src/ tests/` passes
- [ ] `pytest tests/` shows 100% passing
- [ ] `git status` shows no temp files (.log, .tmp, bandit-report.json, etc.)
- [ ] All commits use conventional commit format
- [ ] Minimum 2-5 commits for non-trivial features
- [ ] Commit messages are descriptive and include context

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
