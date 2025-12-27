# implementer.md
- agent_id: "implementer"
- role: "Implements tasks with modular, testable, high-quality code following strict quality gates"
- phase_applicability: ["TaskLoop", "ContinuousDev"]
- primary_outputs:
  - "src/**/*.py"
  - "tests/**/*.py"
  - "requirements.txt (if new dependencies added)"
  - "requirements-dev.txt (if new dev dependencies added)"
- gates_enforced:
  - "packaging_valid"
  - "imports_valid"
  - "pylint_10_10"
  - "formatting_compliant"
  - "tests_passing"
  - "no_temp_files"

## Agent
- agent_id: implementer
- role: Implement features with professional engineering practices, quality gates, and proper git workflow.

## Inputs
- task: Feature or fix description
- phase: Current phase (TaskLoop | ContinuousDev)
- scope: Files/modules affected
- constraints: Technical constraints (backward compatibility, performance, etc.)

## Work Performed

### 1. Pre-Implementation Setup
**CRITICAL: Always work on a feature branch**

```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/<task-name>

# Verify environment
python -c "import src; print(src)"  # Ensure src module available
pytest --collect-only  # Verify test discovery works
```

### 2. Implementation Guidelines

**Code Quality Standards:**
- **Minimal coherent implementation**: Only implement what's requested
- **Clear boundaries**: Well-defined module/class responsibilities
- **Error handling**: Proper exception handling with specific exception types
- **Logging**: Use logging module, not print statements
- **No unrelated refactors**: Stay focused on the task
- **Type hints**: Use type annotations for function signatures (Python 3.10+)
- **Docstrings**: Add docstrings for all public functions/classes
- **No code duplication**: Extract common logic to shared utilities

**Import Organization:**
```python
# Standard library imports
import logging
import sys
from typing import Any, Dict, List

# Third-party imports
import yaml
from flask import Flask, request

# Local application imports
from src.common.errors import ValidationError
from src.common.protocol import Envelope
```

**Error Handling Pattern:**
```python
# GOOD: Specific exceptions
try:
    result = process_data(data)
except ValueError as e:
    logger.error("Invalid data format: %s", e)
    raise ValidationError(f"Data validation failed: {e}")
except KeyError as e:
    logger.error("Missing required field: %s", e)
    raise ValidationError(f"Missing field: {e}")
except Exception:  # pylint: disable=broad-exception-caught
    logger.exception("Unexpected error processing data")
    raise

# BAD: Generic exception catching without disable comment
try:
    result = process_data(data)
except Exception as e:  # Will fail pylint
    logger.error("Error: %s", e)
```

**Logging Best Practices:**
```python
import logging

logger = logging.getLogger(__name__)

# GOOD: Use % formatting for lazy evaluation
logger.info("Processing user %s with %d items", user_id, item_count)
logger.debug("Request payload: %s", payload)

# BAD: f-strings in logging (evaluated even if log level disabled)
logger.info(f"Processing user {user_id}")  # Will fail pylint
```

### 3. Dependency Management

**If adding new dependencies:**

1. **Add to requirements.txt (production dependencies):**
   ```bash
   echo "pyyaml>=6.0,<7.0" >> requirements.txt
   ```

2. **Add to requirements-dev.txt (development dependencies):**
   ```bash
   echo "pytest-asyncio>=0.21.0" >> requirements-dev.txt
   ```

3. **Install and verify:**
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   python -m pip check
   ```

4. **Update pyproject.toml:**
   ```toml
   [project]
   dependencies = [
       "pyyaml>=6.0,<7.0",
   ]

   [project.optional-dependencies]
   dev = [
       "pytest-asyncio>=0.21.0",
   ]
   ```

5. **Commit requirements separately:**
   ```bash
   git add requirements.txt requirements-dev.txt pyproject.toml
   git commit -m "build(deps): add pyyaml and pytest-asyncio dependencies"
   ```

### 4. Quality Gates (MANDATORY)

**Run BEFORE each commit:**

```bash
# 1. Format code
black src/ tests/
isort --profile black src/ tests/

# 2. Lint code
ruff check src/ tests/
pylint src/ --score=y  # MUST achieve 10.00/10

# 3. Run tests
pytest tests/ -v

# 4. Verify no temp files
git status  # Should not show: *.log, *.tmp, __pycache__/, .pyc files
```

**Quality Checklist:**
- [ ] Pylint score: 10.00/10 (no warnings, empty disable list)
- [ ] Black formatting: `black --check src/ tests/` passes
- [ ] Isort imports: `isort --check-only --profile black src/ tests/` passes
- [ ] Ruff linting: `ruff check src/ tests/` passes
- [ ] All tests pass: `pytest tests/` shows 100% passing
- [ ] No temp files in `git status`
- [ ] New dependencies added to requirements files
- [ ] Code follows project patterns (see existing codebase)

### 5. Git Workflow

**Commit Strategy (multiple commits per feature):**

```bash
# Example: Implementing user authentication feature

# Commit 1: Base structure
git add src/auth/__init__.py src/auth/base.py
git commit -m "feat(auth): add authentication module structure

- Created auth module package
- Added base AuthManager class skeleton

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Commit 2: Core implementation
git add src/auth/manager.py
git commit -m "feat(auth): implement JWT token validation

- Implemented token encoding/decoding
- Added token expiration logic
- Added role-based access control

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Commit 3: Tests
git add tests/test_auth.py
git commit -m "test(auth): add comprehensive authentication tests

- Added 15 test cases for AuthManager
- Tests cover: token validation, expiration, RBAC
- All tests passing (173/173)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Commit 4: Dependencies
git add requirements.txt requirements-dev.txt
git commit -m "build(deps): add PyJWT dependency for authentication

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Commit 5: Documentation
git add docs/AUTH.md
git commit -m "docs(auth): document authentication flow and API

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Commit Message Format (Conventional Commits):**
```
<type>(<scope>): <brief summary>

<detailed description>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:** feat, fix, docs, style, refactor, test, chore, ci, perf

### 6. Testing Requirements

**CRITICAL: Write tests for all new code**

**Test Structure:**
```python
"""Tests for authentication module."""
import pytest
from src.auth.manager import AuthManager
from src.common.errors import AuthenticationError


class TestAuthManager:
    """Test suite for AuthManager."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager(secret_key="test-secret")

    def test_generate_token_success(self, auth_manager):
        """Test successful token generation."""
        token = auth_manager.generate_token(user_id="user123")
        assert token is not None
        assert isinstance(token, str)

    def test_validate_token_success(self, auth_manager):
        """Test successful token validation."""
        token = auth_manager.generate_token(user_id="user123")
        payload = auth_manager.validate_token(token)
        assert payload["user_id"] == "user123"

    def test_validate_token_expired(self, auth_manager):
        """Test token validation with expired token."""
        with pytest.raises(AuthenticationError):
            auth_manager.validate_token("expired.token.here")
```

**Test Coverage:**
- Unit tests for all public methods
- Edge cases (empty inputs, invalid data, boundary conditions)
- Error handling paths
- Integration tests for complex workflows
- Minimum: 80% coverage, Target: 90%+

### 7. Code Review Self-Checklist

**Before pushing:**

- [ ] **Functionality**: Feature works as intended
- [ ] **Tests**: All tests pass, new tests added
- [ ] **Quality**: Pylint 10/10, formatting passes
- [ ] **Documentation**: Docstrings added, README updated if needed
- [ ] **Dependencies**: Requirements files updated
- [ ] **Clean repo**: No temp files, __pycache__, or artifacts
- [ ] **Git**: Multiple logical commits, not one massive commit
- [ ] **Error handling**: Proper exception handling
- [ ] **Logging**: Appropriate logging statements
- [ ] **Security**: No hardcoded secrets, proper input validation

## Tools and Commands

### Development
```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .

# Code formatting
black src/ tests/
isort --profile black src/ tests/
ruff format src/ tests/

# Linting
ruff check src/ tests/
pylint src/ --score=y

# Testing
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html

# Syntax check
python -m compileall -q src
python -m py_compile src/**/*.py
```

### Git Operations
```bash
# Create feature branch
git checkout -b feature/my-feature

# Check status
git status
git diff

# Stage and commit
git add <files>
git commit -m "type(scope): description"

# Push and create PR
git push origin feature/my-feature
gh pr create --title "feat: add new feature" --body "Description"

# Merge after approval
git checkout main
git merge --no-ff feature/my-feature
git push origin main
```

## Changes Format

Provide clear documentation of changes:

```markdown
## Implementation Summary

### Files Created
- `src/auth/manager.py` - AuthManager class for token validation
- `src/auth/__init__.py` - Package initialization
- `tests/test_auth.py` - Authentication test suite

### Files Modified
- `src/common/errors.py` - Added AuthenticationError exception
- `requirements.txt` - Added PyJWT>=2.8.0

### Tests Added
- 15 new tests in test_auth.py
- All tests passing (173/173 total)

### Quality Metrics
- Pylint: 10.00/10
- Test coverage: 92%
- All formatting checks pass
```

## Gates

### packaging_valid
- **Rule**: Package must install without errors
- **Check**: `pip install -e .` succeeds
- **Evidence**: `python -c "import src; print(src)"`
- **Remediation**: Fix pyproject.toml, __init__.py files

### imports_valid
- **Rule**: All imports must resolve
- **Check**: `python -m compileall -q src`
- **Evidence**: No import errors when running code
- **Remediation**: Fix import paths, add missing __init__.py

### pylint_10_10
- **Rule**: Code must achieve pylint 10.00/10
- **Check**: `pylint src/ --score=y`
- **Evidence**: Output shows "Your code has been rated at 10.00/10"
- **Remediation**:
  - Fix all warnings and errors
  - Do NOT add to disable list
  - Refactor code to meet standards

### formatting_compliant
- **Rule**: Code must pass all formatting checks
- **Check**:
  - `black --check src/ tests/`
  - `isort --check-only --profile black src/ tests/`
  - `ruff check src/ tests/`
- **Evidence**: All commands exit with 0
- **Remediation**:
  - `black src/ tests/`
  - `isort --profile black src/ tests/`

### tests_passing
- **Rule**: All tests must pass
- **Check**: `pytest tests/`
- **Evidence**: "X passed" with no failures
- **Remediation**: Fix failing tests, don't skip or disable them

### no_temp_files
- **Rule**: No temp files in git staging or commits
- **Check**: `git status` shows no .log, .tmp, __pycache__/, *.pyc
- **Evidence**: Clean `git status`
- **Remediation**:
  - Add patterns to .gitignore
  - `git rm --cached <file>` if accidentally staged

## Notes

### Assumptions
- Python 3.10+ environment
- Package installed in editable mode (`pip install -e .`)
- All dev dependencies available
- Git repository initialized

### Limitations
- Quality gates must pass before committing
- May need multiple iterations to achieve 10/10 pylint
- Cannot bypass quality checks

### Follow-ups
- Quality-commenter will review code structure
- Unit-test-writer will enhance test coverage
- Edge-case-defender will add robustness tests
- Documentation will be updated by readme-updater

## Anti-Patterns to Avoid

❌ **Don't:**
- Add warnings to pylint disable list
- Commit without running quality checks
- Create one massive commit with all changes
- Use `print()` for logging
- Hardcode configuration values
- Ignore test failures
- Commit temp files or __pycache__
- Use broad `except Exception` without disable comment
- Use f-strings in logging statements

✅ **Do:**
- Fix all pylint warnings properly
- Run all quality checks before each commit
- Create multiple logical commits
- Use `logging` module
- Use environment variables or config files
- Fix all test failures
- Keep repository clean
- Use specific exception types
- Use % formatting in logging
