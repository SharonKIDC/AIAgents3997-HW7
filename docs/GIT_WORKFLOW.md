# Git Workflow

This document defines the Git workflow and best practices for the AIAgents3997-HW7 project.

## Table of Contents

1. [Branching Strategy](#branching-strategy)
2. [Commit Message Conventions](#commit-message-conventions)
3. [Pull Request Process](#pull-request-process)
4. [Release Strategy](#release-strategy)
5. [Git Best Practices](#git-best-practices)

---

## Branching Strategy

### Branch Types

#### Main Branch: `main`
- **Purpose**: Production-ready code
- **Protection**: Protected branch, requires PR reviews
- **Stability**: Always deployable
- **Merging**: Only via approved Pull Requests

#### Feature Branches: `feature/<feature-name>`
- **Purpose**: New features or enhancements
- **Naming**: `feature/pluggable-strategies`, `feature/referee-registry`
- **Lifespan**: Delete after merging to main
- **Base**: Created from `main`
- **Example**: `git checkout -b feature/strategy-pattern main`

#### Bugfix Branches: `bugfix/<issue-description>`
- **Purpose**: Bug fixes
- **Naming**: `bugfix/player-initialization`, `bugfix/game-state-error`
- **Lifespan**: Delete after merging to main
- **Base**: Created from `main`

#### Hotfix Branches: `hotfix/<critical-issue>`
- **Purpose**: Critical production fixes
- **Naming**: `hotfix/security-vulnerability`, `hotfix/game-crash`
- **Priority**: Highest priority, fast-tracked reviews
- **Base**: Created from `main`

#### Release Branches: `release/v<version>`
- **Purpose**: Prepare new production releases
- **Naming**: `release/v1.0.0`, `release/v2.1.0`
- **Activities**: Final testing, documentation, version bumping
- **Merging**: To both `main` (with tag) and back-merge to development branches

#### Experiment Branches: `experiment/<experiment-name>`
- **Purpose**: Research, prototyping, proof-of-concept
- **Naming**: `experiment/monte-carlo-optimization`
- **Lifespan**: May be long-lived or abandoned
- **Merging**: Optional, may not merge if experiment fails

### Workflow Diagram

```
main ──────●─────────●──────────●─────────────●──────>
           │         │          │             │
           │         │          │             │
feature/x  └──●──●───┘          │             │
                                │             │
bugfix/y                        └──●──●───────┘

release/v1.0.0                        └──●──●──┘
                                          (tag v1.0.0)
```

---

## Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
  - Example: `feat(player): add Monte Carlo strategy`
- **fix**: Bug fix
  - Example: `fix(referee): correct game state validation`
- **docs**: Documentation changes
  - Example: `docs(readme): update installation instructions`
- **style**: Code style changes (formatting, missing semicolons, etc.)
  - Example: `style(player): apply PEP 8 formatting`
- **refactor**: Code refactoring without feature changes
  - Example: `refactor(game): extract strategy pattern`
- **perf**: Performance improvements
  - Example: `perf(player): optimize move calculation`
- **test**: Adding or updating tests
  - Example: `test(player): add edge case tests for strategies`
- **build**: Build system or dependency changes
  - Example: `build(deps): upgrade pytest to 8.3.4`
- **ci**: CI/CD configuration changes
  - Example: `ci(github): add automated testing workflow`
- **chore**: Other changes (maintenance, tooling)
  - Example: `chore(lint): add pylint configuration`
- **revert**: Revert a previous commit
  - Example: `revert: revert "feat(player): add risky strategy"`

### Scope

Optional but recommended. Indicates the module or component:
- `player`, `referee`, `game`, `strategy`, `registry`, `config`, `docs`, `tests`

### Subject

- Use imperative mood: "add" not "added" or "adds"
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters

### Body

- Optional but recommended for complex changes
- Explain **what** and **why**, not **how**
- Wrap at 72 characters
- Separate from subject with blank line

### Footer

- **BREAKING CHANGE**: Indicates breaking changes
  - Example: `BREAKING CHANGE: Player strategy imports have changed`
- **Closes**: Reference issue numbers
  - Example: `Closes #42, #53`
- **Co-authored-by**: Credit contributors
  - Example: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

### Examples

#### Simple Feature
```
feat(strategy): add greedy strategy implementation

Implements a greedy strategy that always selects the highest-value move
available without considering long-term consequences.
```

#### Bug Fix
```
fix(referee): prevent duplicate player registration

Players can no longer register multiple times for the same game,
which was causing inconsistent game states.

Closes #127
```

#### Breaking Change
```
feat(player): implement pluggable strategy pattern

BREAKING CHANGE: Player strategy imports have changed.
Old: from player.basic_strategy import BasicStrategy
New: from player.strategies import get_strategy

Migration guide available in docs/MIGRATION.md
```

#### Refactoring
```
refactor(game): separate strategy pattern from game logic

Major refactoring to achieve complete decoupling of game logic from
communication layer using Strategy and Registry design patterns.

Changes:
- Add abstract base classes (StrategyInterface, GameInterface)
- Implement registry pattern for runtime component discovery
- Refactor player strategies into pluggable modules
- Refactor referee games for pluggability

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Pull Request Process

### Before Creating a PR

1. **Sync with main**
   ```bash
   git checkout main
   git pull origin main
   git checkout feature/your-feature
   git rebase main
   ```

2. **Run tests locally**
   ```bash
   ./run_tests.sh
   pytest tests/ -v
   ```

3. **Lint your code**
   ```bash
   pylint src/ tests/
   ```

4. **Update documentation** if needed

### Creating a Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature
   ```

2. **Create PR on GitHub** with:
   - Clear, descriptive title following commit conventions
   - Description explaining changes
   - Link to related issues
   - Screenshots/examples if UI/output changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests pass locally
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases tested

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No merge conflicts

## Related Issues
Closes #123
```

### Code Review Guidelines

**For Authors:**
- Keep PRs focused and small
- Respond to feedback promptly
- Don't take criticism personally
- Explain your reasoning when disagreeing

**For Reviewers:**
- Review within 24 hours if possible
- Be constructive and kind
- Ask questions, don't make demands
- Approve only when ready for production
- Check:
  - Code correctness
  - Test coverage
  - Documentation
  - Style consistency
  - Security implications
  - Performance impact

### Merging

- **Strategy**: Squash and merge (keeps main clean)
- **Alternative**: Rebase and merge (preserves individual commits)
- **Delete branch** after merging

---

## Release Strategy

We follow [Semantic Versioning](https://semver.org/) (SemVer): `MAJOR.MINOR.PATCH`

### Version Numbers

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
  - API changes incompatible with previous version
  - Major refactoring changing interfaces

- **MINOR** (1.0.0 → 1.1.0): New features (backward compatible)
  - New strategies added
  - New game types supported
  - Enhanced functionality

- **PATCH** (1.0.0 → 1.0.1): Bug fixes (backward compatible)
  - Bug fixes
  - Performance improvements
  - Documentation updates

### Release Process

1. **Create release branch**
   ```bash
   git checkout -b release/v1.2.0 main
   ```

2. **Update version numbers**
   - `pyproject.toml`
   - `setup.py`
   - `__init__.py` (if applicable)

3. **Update CHANGELOG.md**
   ```markdown
   ## [1.2.0] - 2025-12-22
   ### Added
   - New Monte Carlo strategy
   - Strategy registry system

   ### Changed
   - Improved player initialization

   ### Fixed
   - Game state synchronization bug
   ```

4. **Final testing**
   ```bash
   ./run_tests.sh
   pytest tests/ -v --cov=src
   ```

5. **Create release PR** to main

6. **Tag the release** after merging
   ```bash
   git checkout main
   git pull origin main
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   ```

7. **Create GitHub Release**
   - Use tag v1.2.0
   - Copy CHANGELOG entry to release notes
   - Attach distribution files if applicable

### Pre-release Versions

For alpha, beta, or release candidates:
- **Alpha**: `1.2.0-alpha.1`
- **Beta**: `1.2.0-beta.1`
- **Release Candidate**: `1.2.0-rc.1`

---

## Git Best Practices

### General Guidelines

1. **Commit often, push regularly**
   - Small, focused commits
   - Push at least daily to backup work

2. **Write meaningful commit messages**
   - Follow conventional commits
   - Explain the "why", not the "what"

3. **Keep commits atomic**
   - One logical change per commit
   - Should be revertable independently

4. **Never commit secrets**
   - No API keys, passwords, credentials
   - Use `.gitignore` for sensitive files
   - Use environment variables or config files

5. **Review before committing**
   ```bash
   git diff
   git diff --staged
   ```

### Commands Cheatsheet

#### Daily Workflow
```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/my-feature

# Make changes and commit
git add src/player/strategies/new_strategy.py
git commit -m "feat(strategy): add new strategy"

# Update from main
git fetch origin
git rebase origin/main

# Push to remote
git push origin feature/my-feature
```

#### Fixing Mistakes

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - DANGEROUS
git reset --hard HEAD~1

# Amend last commit message
git commit --amend -m "new message"

# Unstage file
git restore --staged <file>

# Discard local changes
git restore <file>

# Stash changes temporarily
git stash
git stash pop
```

#### Viewing History

```bash
# View commit history
git log --oneline --graph --all

# View changes in commit
git show <commit-hash>

# View file history
git log --follow <file>

# Search commits
git log --grep="strategy"
git log --author="Claude"
```

### File Management

#### .gitignore Best Practices

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
env/

# IDE
.vscode/
.idea/
*.swp

# Testing
.pytest_cache/
.coverage
htmlcov/

# Build
dist/
build/
*.egg-info/

# Secrets
.env
secrets/
credentials.json
```

### Security

1. **Never use `--force` on shared branches**
   - Especially not on `main`
   - Only use on your own feature branches if absolutely necessary

2. **Sign commits** (optional but recommended)
   ```bash
   git config --global commit.gpgsign true
   ```

3. **Review dependencies**
   - Regular security audits: `pip-audit`
   - Keep dependencies updated

4. **Protect sensitive data**
   - Use git-secrets or similar tools
   - Scan commits before pushing

### Collaboration

1. **Communicate changes**
   - Comment on PRs
   - Update issue status
   - Document breaking changes

2. **Sync frequently**
   - Pull/rebase daily
   - Avoid long-lived branches

3. **Respect code ownership**
   - Tag appropriate reviewers
   - Follow team conventions

---

## Agent-Based Workflow (Automated)

This project uses an **automated agent orchestration system** that manages git workflow through specialized agents. This ensures consistent process and quality for all development work.

### Overview

Two orchestrators manage different types of development:

1. **agent-orchestrator.md**: For greenfield projects and PRD-based features
2. **continuous-dev-orchestrator.md**: For bug fixes, improvements, and ongoing development

**CRITICAL**: Both use the SAME git-workflow agent to ensure consistency.

### Git-Workflow Agent

The `git-workflow` agent has **exclusive authority** over all git operations:
- Creates branches for each phase and agent
- Commits changes after each agent execution
- Merges agent branches using `--no-ff` (preserves history)
- Enforces minimum commit targets
- Tracks workflow state in `.git-workflow-state.json`

### Automated Branch Structure

#### Phase Branches
```
phase/{phase-name}-YYYYMMDD-HHMMSS
```
Examples:
- `phase/PreProject-20250624-140000`
- `phase/TaskLoop-20250624-150000`
- `phase/ContinuousDev-20250624-160000`

#### Agent Branches
```
agent/{phase}/{agent-id}-YYYYMMDD-HHMMSS
```
Examples:
- `agent/PreProject/prd-author-20250624-140530`
- `agent/TaskLoop/implementer-20250624-150215`
- `agent/ContinuousDev/unit-test-writer-20250624-160445`

### Automated Commit Format

Each agent execution produces a structured commit:

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

Example:
```
[TaskLoop] implementer: Add player strategy registry

Agent: implementer
Purpose: Implement core functionality for task
Phase: TaskLoop

Changes:
- Created: src/player/registry.py
- Modified: src/player/__init__.py
- Tests: tests/test_registry.py

Documentation: .claude/agents/implementer.md
```

### Workflow Execution Pattern

#### For Main Orchestrator (PRD-based projects)
```
git-workflow(pre_phase: PreProject)
  ├─ git-workflow(pre_agent) → repo-scaffolder → git-workflow(post_agent)
  ├─ git-workflow(pre_agent) → prd-author → git-workflow(post_agent)
  └─ git-workflow(pre_agent) → architecture-author → git-workflow(post_agent)
git-workflow(post_phase: PreProject) → merge to main, tag

git-workflow(pre_phase: TaskLoop)
  ├─ git-workflow(pre_agent) → implementer → git-workflow(post_agent)
  ├─ git-workflow(pre_agent) → quality-commenter → git-workflow(post_agent)
  └─ git-workflow(pre_agent) → unit-test-writer → git-workflow(post_agent)
git-workflow(post_phase: TaskLoop) → merge to main, tag

... (ResearchLoop, ReleaseGate follow same pattern)
```

#### For Continuous Dev Orchestrator (bug fixes, improvements)
```
User task: "Fix timeout bug in agent registration"

git-workflow(pre_phase: ContinuousDev)
  ├─ git-workflow(pre_agent) → implementer → git-workflow(post_agent)
  ├─ git-workflow(pre_agent) → unit-test-writer → git-workflow(post_agent)
  ├─ git-workflow(pre_agent) → quality-commenter → git-workflow(post_agent)
  └─ git-workflow(pre_agent) → prompt-log-updater → git-workflow(post_agent)
git-workflow(post_phase: ContinuousDev) → merge to main, tag

Result: 4 commits, proper branching, quality gates enforced
```

### Commit Targets

- **Main orchestrator**: Minimum 15 commits across full project lifecycle
- **Continuous dev**: 1-5 commits per task (depends on complexity)

### Quality Gates (Automated)

The git-workflow agent enforces:

1. **agent_branch_isolation**: Each agent works on dedicated branch
2. **clean_merge_history**: All merges use `--no-ff` flag
3. **commit_message_quality**: All commits follow structured format
4. **minimum_commits_target**: Project meets commit goals

### Viewing Agent Workflow Progress

#### Full branch/merge tree
```bash
git log --graph --oneline --all --decorate
```

#### Commits by phase
```bash
git log --grep="\[PreProject\]" --oneline
git log --grep="\[TaskLoop\]" --oneline
git log --grep="\[ContinuousDev\]" --oneline
```

#### Commits by specific agent
```bash
git log --grep="Agent: implementer" --oneline
git log --grep="Agent: quality-commenter" --oneline
```

#### Files changed by agent
```bash
git log --stat --grep="Agent: implementer"
```

#### Current workflow state
```bash
cat .git-workflow-state.json | jq
```

Sample output:
```json
{
  "project_start": "2025-12-24T14:00:00Z",
  "current_phase": "TaskLoop",
  "phases_completed": ["PreProject"],
  "current_branch": "phase/TaskLoop-20250624-150000",
  "agents_executed": [
    {
      "agent_id": "implementer",
      "phase": "TaskLoop",
      "branch": "agent/TaskLoop/implementer-20250624-150215",
      "commit_sha": "a1b2c3d",
      "timestamp": "2025-12-24T15:02:45Z",
      "files_changed": ["src/player/registry.py", "tests/test_registry.py"]
    }
  ],
  "total_commits": 8,
  "target_commits": 15,
  "gates_passed": {"agent_branch_isolation": true, "clean_merge_history": true},
  "gates_failed": {}
}
```

### Success Criteria

A well-managed agent workflow shows:
- ✅ Each agent has dedicated branch and merge commit
- ✅ Clear phase boundaries in commit history
- ✅ Structured commit messages throughout
- ✅ No direct commits to main (all via agent branches)
- ✅ Minimum commit targets met
- ✅ Full merge history preserved with `--no-ff`

### Example: Complete Bug Fix Workflow

```bash
# User request: "Fix race condition in match scheduler"
# continuous-dev-orchestrator analyzes and selects agents

# Git-workflow creates phase branch
phase/ContinuousDev-20250624-160000

# Each agent gets its own branch:
agent/ContinuousDev/implementer-20250624-160015
  → Fix implemented → commit → merge to phase branch

agent/ContinuousDev/unit-test-writer-20250624-160045
  → Test added → commit → merge to phase branch

agent/ContinuousDev/edge-case-defender-20250624-160115
  → Edge cases verified → commit → merge to phase branch

agent/ContinuousDev/quality-commenter-20250624-160145
  → Quality reviewed → commit → merge to phase branch

agent/ContinuousDev/prompt-log-updater-20250624-160215
  → Documentation updated → commit → merge to phase branch

# Git-workflow merges phase to main
git checkout main
git merge --no-ff phase/ContinuousDev-20250624-160000
git tag v-continuous-dev-fix-race-condition-20250624

# Result: 5 commits, complete audit trail, proper process
```

### Integration with Manual Workflow

The agent-based workflow complements manual development:

**Automated (via orchestrators)**:
- Greenfield projects
- PRD implementation
- Structured bug fixes
- Quality-gated improvements

**Manual (traditional git)**:
- Experimental work
- Quick prototypes
- Manual hotfixes (urgent)
- Documentation-only changes

Both workflows can coexist on the same repository.

---

## Project-Specific Guidelines

### For This Project (AIAgents3997-HW7)

1. **Strategy Changes**
   - All strategy changes require tests
   - Update strategy registry documentation
   - Run full test suite before committing

2. **Game Logic Changes**
   - Verify against game interface contracts
   - Test with all strategy combinations
   - Update architecture documentation

3. **Configuration Changes**
   - Document in README.md
   - Provide migration guide if breaking
   - Test with default and custom configs

4. **Documentation**
   - Keep docs/ up to date
   - Update API documentation
   - Maintain CHANGELOG.md

5. **Testing Requirements**
   - Minimum 80% code coverage
   - All tests must pass
   - Include edge case tests

---

## Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Pro Git Book](https://git-scm.com/book/en/v2)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-22
**Maintained By**: AI Agents Course Team
