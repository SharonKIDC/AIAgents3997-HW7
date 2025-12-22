# python-env-setup.md
- agent_id: "python-env-setup"
- role: "Defines, documents, and validates a Python venv-based development environment (no conda), dependency management, and reproducibility"
- phase_applicability: ["PreProject", "ReleaseGate"]
- primary_outputs:
  - ".python-version (optional)"
  - "requirements.txt"
  - "requirements-dev.txt"
  - "requirements.lock (optional)"
  - "docs/ENVIRONMENT.md"
- gates_enforced:
  - "environment_defined"
  - "environment_reproducible"

## Agent
- agent_id: python-env-setup
- role: Ensure Python environment setup is explicit, reproducible, and documented without conda.

## Inputs
- task:
- phase:
- scope:
- constraints:
  - python_version (optional, default: 3.12 or project standard)
  - os_targets: [linux, macos, windows] (optional)
  - packaging: pyproject.toml | requirements (optional)
  - lockfile_required: true/false (optional)
  - index_url / extra_index_url (optional)

## Work performed
- Enforce "no conda" policy.
- Use `venv` for isolation.
- Split dependencies:
  - `requirements.txt` for runtime
  - `requirements-dev.txt` for dev/test/lint tools
- Optional: maintain `requirements.lock` for full pinning when requested.
- Document exact setup commands and verification steps.
- Ensure shell startup does not auto-activate any env.

## Tools and commands
- Create venv:
  - `python -m venv .venv`
- Activate:
  - `source .venv/bin/activate`
- Upgrade tooling:
  - `python -m pip install --upgrade pip setuptools wheel`
- Install deps:
  - `pip install -r requirements.txt -r requirements-dev.txt`
- Optional lock:
  - `pip freeze > requirements.lock`
- Verify:
  - `python --version`
  - `python -c "import sys; print(sys.executable)"`
  - `python -m pip check`

## Changes
```diff
*** /dev/null
--- b/docs/ENVIRONMENT.md
@@
+# Python Environment (no conda)
+
+## Python version
+- Recommended: 3.12+ (align with project packaging / CI)
+
+## Create virtual environment
+```bash
+python -m venv .venv
+source .venv/bin/activate
+python -m pip install --upgrade pip setuptools wheel
+```
+
+## Install dependencies
+```bash
+pip install -r requirements.txt -r requirements-dev.txt
+python -m pip check
+```
+
+## Run tests
+```bash
+pytest -q
+```
+
+## Optional: lock dependencies
+If a fully pinned snapshot is required:
+```bash
+pip freeze > requirements.lock
+```
+
+## Notes
+- Do not commit `.venv/`.
+- Do not auto-activate the environment on shell startup.
+- If your shell auto-activates something, remove any `source .venv/bin/activate` lines from:
+  - `~/.bashrc`, `~/.zshrc`, `~/.profile`
