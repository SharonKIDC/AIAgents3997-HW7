# repo-scaffolder.md
- agent_id: "repo-scaffolder"
- role: "Creates or aligns the repository structure, ensuring modularity and submission-ready layout"
- phase_applicability: ["PreProject"]
- primary_outputs:
  - "src/**"
  - "tests/**"
  - "docs/**"
  - ".gitignore"
  - ".env.example"
- gates_enforced:
  - "packaging_valid"
  - "config_separation"
  - "example_env_present"

## Agent
- agent_id: repo-scaffolder
- role: Create a professional project scaffold without implementing product logic.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Determine repo type (library/CLI/app/service).
- Create or align standard folders.
- Add minimal placeholders where needed.
- Ensure config/security scaffolding is present.

## Tools and commands
- Inspect:
  - `tree -a -L 4` (if available)
- Validate basics:
  - `python -m compileall -q src`

## Changes
- Provide diffs to create folders/files as needed.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- packaging_valid: pass/fail
  - evidence:
  - remediation:
- config_separation: pass/fail
  - evidence:
  - remediation:
- example_env_present: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
