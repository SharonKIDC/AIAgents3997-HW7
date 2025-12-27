# python-env-setup.md
- agent_id: "python-env-setup"
- role: "Defines, documents, and validates a Python venv-based development environment (no conda), dependency management, and reproducibility"
- phase_applicability: ["PreProject", "ReleaseGate"]
- primary_outputs:
  - ".python-version (optional)"
  - "requirements.txt"
  - "requirements-dev.txt"
  - "requirements-test.txt (optional)"
  - "requirements.lock (optional)"
  - "pyproject.toml"
  - ".gitignore"
  - "docs/ENVIRONMENT.md"
  - ".pre-commit-config.yaml"
  - ".github/workflows/ci.yml"
  - ".pylintrc"
- gates_enforced:
  - "environment_defined"
  - "environment_reproducible"
  - "quality_tools_configured"

## Agent
- agent_id: python-env-setup
- role: Ensure Python environment setup is explicit, reproducible, and documented without conda.

## Inputs
- task:
- phase:
- scope:
- constraints:
  - python_version (optional, default: 3.10+ or project standard)
  - os_targets: [linux, macos, windows] (optional)
  - packaging: pyproject.toml (required for editable install)
  - lockfile_required: true/false (optional)
  - index_url / extra_index_url (optional)

## Work performed
**CRITICAL - Must create development environment files:**

1. **Python Environment:**
   - Enforce "no conda" policy
   - Use `venv` for isolation
   - Split dependencies:
     - `requirements.txt` for runtime/production
     - `requirements-dev.txt` for dev/test/lint tools
     - `requirements-test.txt` for test-only dependencies (optional)
   - Optional: maintain `requirements.lock` for full pinning when requested
   - **CRITICAL**: Install package in editable mode with `pip install -e .`
   - Document exact setup commands and verification steps
   - Ensure shell startup does not auto-activate any env

2. **pyproject.toml** - Package configuration:
   - Define package metadata (name, version, description)
   - List runtime dependencies
   - List dev dependencies in `[project.optional-dependencies]`
   - Configure tools: black, ruff, pytest, mypy, isort, pylint
   - **CRITICAL**: Configure line-length consistently (100-120 chars)
   - Example tool configurations below

3. **.pylintrc** - Pylint configuration:
   - **CRITICAL**: Empty disable list - fix issues, don't hide them
   - Configure max-line-length to match black/ruff
   - Configure good-names, max-args, max-attributes as needed
   - Ignore directories: .venv, venv, build, dist, htmlcov, .pytest_cache, .ruff_cache, .mypy_cache, data, logs
   - Set jobs=4 for parallel linting
   - **Target: 10.00/10 score with zero warnings**

4. **.gitignore** - Version control exclusions:
   - Python: `__pycache__/`, `*.py[cod]`, `*$py.class`, `.venv/`, `venv/`, `ENV/`, `env/`
   - IDEs: `.vscode/`, `.idea/`, `*.swp`, `*.swo`
   - Testing: `.pytest_cache/`, `.coverage`, `htmlcov/`, `coverage.xml`
   - Build: `build/`, `dist/`, `*.egg-info/`
   - Linters: `.ruff_cache/`, `.mypy_cache/`
   - **Temp files**: `*.log`, `*.tmp`, `bandit-report.json`, `*.db`, `data/`, `logs/`
   - OS: `.DS_Store`, `Thumbs.db`

5. **.pre-commit-config.yaml** - Pre-commit hooks:
   - Code formatters (black, isort)
   - Linters (ruff, pylint)
   - Security checks (bandit)
   - File checks (trailing whitespace, end of file, YAML/JSON validation)
   - **Use latest versions** (check repo tags)
   - Installation command in docs/ENVIRONMENT.md

6. **.github/workflows/ci.yml** - GitHub Actions CI:
   - **CRITICAL**: Use latest action versions (actions/checkout@v4, actions/setup-python@v5, actions/upload-artifact@v4, codecov/codecov-action@v5)
   - Test matrix (Python 3.10, 3.11, 3.12)
   - OS matrix (ubuntu-latest, optionally macos, windows)
   - **CRITICAL Steps**:
     1. Checkout code
     2. Setup Python with pip caching
     3. Install dependencies INCLUDING `pip install -e .`
     4. Run linting (ruff check)
     5. Run tests with coverage
     6. Run formatting checks (black --check, isort --check-only)
     7. Run security scan (bandit)
   - Code coverage reporting
   - Badge in README.md

**Example pyproject.toml:**
```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-project-name"
version = "1.0.0"
description = "Your project description"
requires-python = ">=3.10"
dependencies = [
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.10.0",
    "black>=23.7.0",
    "ruff>=0.1.0",
    "isort>=5.12.0",
    "pylint>=3.0.0",
    "mypy>=1.5.0",
    "bandit>=1.7.0",
]

[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --cov=src --cov-report=html --cov-report=term"

[tool.isort]
profile = "black"
line_length = 100
```

**Example .pylintrc:**
```ini
[MASTER]
init-hook='import sys; sys.path.append(".")'
jobs=4
ignore=.venv,venv,build,dist,htmlcov,.pytest_cache,.ruff_cache,.mypy_cache,data,logs

[MESSAGES CONTROL]
# CRITICAL: No disables - all issues must be fixed, not hidden
disable=

[REPORTS]
output-format=colorized
reports=no

[FORMAT]
max-line-length=100
indent-string='    '

[DESIGN]
max-args=8
max-attributes=14
min-public-methods=1
```

**Example .gitignore:**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
.venv/
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
coverage.xml
.tox/

# Build
build/
dist/
*.egg-info/
*.egg

# Linters
.ruff_cache/
.mypy_cache/

# Temp files and reports
*.log
*.tmp
bandit-report.json
*.db
*.sqlite
*.sqlite3
data/
logs/

# OS
.DS_Store
Thumbs.db
```

**Example .pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        language_version: python3.10
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**Example .github/workflows/ci.yml:**
```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Test Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt -r requirements-dev.txt
        pip install -e .

    - name: Run linting
      run: |
        ruff check src/ tests/

    - name: Run tests with coverage
      run: |
        pytest tests/ --cov=src --cov-report=xml --cov-report=term

    - name: Upload coverage
      uses: codecov/codecov-action@v5
      with:
        files: ./coverage.xml
        fail_ci_if_error: false

  lint:
    name: Lint and Format Check
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install black isort ruff pylint

    - name: Check formatting with black
      run: black --check src/ tests/

    - name: Check import sorting with isort
      run: isort --check-only --profile black src/ tests/

    - name: Lint with ruff
      run: ruff check src/ tests/

    - name: Lint with pylint
      run: pylint src/ --score=y

  security:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"

    - name: Install bandit
      run: pip install bandit[toml]

    - name: Run security scan
      run: bandit -r src/ -f json -o bandit-report.json || true

    - name: Upload bandit report
      uses: actions/upload-artifact@v4
      with:
        name: bandit-security-report
        path: bandit-report.json
```

**Validation:**
- All files exist: requirements.txt, requirements-dev.txt, pyproject.toml, .gitignore, .pylintrc
- CI workflow is valid YAML with latest action versions
- Pre-commit config has at least 5 hooks
- Package installs in editable mode: `pip install -e .` succeeds
- All quality tools configured: black, isort, ruff, pylint, bandit
- Pylint achieves 10/10 score

## Tools and commands
- **Create venv:**
  - `python -m venv .venv`
- **Activate:**
  - Linux/Mac: `source .venv/bin/activate`
  - Windows: `.venv\Scripts\activate`
- **Upgrade tooling:**
  - `python -m pip install --upgrade pip setuptools wheel`
- **Install deps:**
  - `pip install -r requirements.txt -r requirements-dev.txt`
  - **CRITICAL**: `pip install -e .`
- **Verify install:**
  - `python --version`
  - `python -c "import sys; print(sys.executable)"`
  - `python -m pip check`
  - `python -c "import src; print(src)"`  # Verify src module available
- **Run quality checks:**
  - `ruff check src/ tests/`
  - `black --check src/ tests/`
  - `isort --check-only --profile black src/ tests/`
  - `pylint src/ --score=y`  # Must achieve 10/10
  - `pytest tests/`
  - `bandit -r src/`
- **Apply formatting:**
  - `black src/ tests/`
  - `isort --profile black src/ tests/`
  - `ruff format src/ tests/`
- **Optional lock:**
  - `pip freeze > requirements.lock`

## Changes
```diff
*** /dev/null
--- b/docs/ENVIRONMENT.md
@@
+# Python Environment (no conda)
+
+## Python version
+- Recommended: 3.10+ (align with project packaging / CI)
+
+## Create virtual environment
+```bash
+python -m venv .venv
+source .venv/bin/activate  # Linux/Mac
+# OR: .venv\Scripts\activate  # Windows
+python -m pip install --upgrade pip setuptools wheel
+```
+
+## Install dependencies
+```bash
+pip install -r requirements.txt -r requirements-dev.txt
+pip install -e .  # CRITICAL: Install package in editable mode
+python -m pip check
+```
+
+## Verify installation
+```bash
+python --version
+python -c "import src; print(src)"  # Should not raise ImportError
+```
+
+## Run quality checks
+```bash
+# Linting
+ruff check src/ tests/
+pylint src/ --score=y  # Target: 10.00/10
+
+# Formatting
+black --check src/ tests/
+isort --check-only --profile black src/ tests/
+
+# Tests
+pytest tests/ --cov=src
+
+# Security
+bandit -r src/
+```
+
+## Apply formatting
+```bash
+black src/ tests/
+isort --profile black src/ tests/
+```
+
+## Run tests
+```bash
+pytest -v
+```
+
+## Optional: lock dependencies
+If a fully pinned snapshot is required:
+```bash
+pip freeze > requirements.lock
+```
+
+## Notes
+- **Do not commit** `.venv/`, `__pycache__/`, or temp files
+- Do not auto-activate the environment on shell startup
+- If your shell auto-activates something, remove any `source .venv/bin/activate` lines from:
+  - `~/.bashrc`, `~/.zshrc`, `~/.profile`
+- Always run `pip install -e .` after pulling changes
+- Maintain pylint 10/10 score - fix issues, don't hide them
+```
+
+## Quality Gates
+**Before considering this agent's work complete:**
+
+1. ✅ `pip install -e .` succeeds without errors
+2. ✅ `python -c "import src"` succeeds (no ImportError)
+3. ✅ `pylint src/ --score=y` shows 10.00/10
+4. ✅ `black --check src/ tests/` passes
+5. ✅ `isort --check-only --profile black src/ tests/` passes
+6. ✅ `ruff check src/ tests/` passes
+7. ✅ `pytest tests/` shows 100% passing
+8. ✅ `.gitignore` includes all temp files and artifacts
+9. ✅ CI workflow uses latest GitHub Actions versions
+10. ✅ All config files use consistent line-length settings

## Dependencies to include in requirements-dev.txt
```
# Testing framework
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.10.0
pytest-timeout>=2.1.0

# Code quality tools
black>=23.7.0
ruff>=0.1.0
isort>=5.12.0
pylint>=3.0.0
mypy>=1.5.0

# Security scanning
bandit>=1.7.0

# Build tools
build>=0.10.0
setuptools>=68.0
wheel>=0.40.0
```
