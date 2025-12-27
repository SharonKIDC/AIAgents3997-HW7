# python-packager.md
- agent_id: "python-packager"
- role: "Ensures packaging correctness: pyproject/setup, __init__.py exports, versioning, import hygiene"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "pyproject.toml (or setup.py)"
  - "src/**/__init__.py"
- gates_enforced:
  - "packaging_valid"
  - "imports_valid"
  - "init_exports_valid"
  - "versioning_present"

## Agent
- agent_id: python-packager
- role: Make packaging and imports submission-ready.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Ensure pyproject/setup exists, src layout is consistent, imports are correct, __version__ defined, editable install works.

## Tools and commands
- `python -m pip install -e .`
- `python -m compileall -q src`

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- packaging_valid: pass/fail
  - evidence:
  - remediation:
- imports_valid: pass/fail
  - evidence:
  - remediation:
- init_exports_valid: pass/fail
  - evidence:
  - remediation:
- versioning_present: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
