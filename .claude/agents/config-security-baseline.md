# config-security-baseline.md
- agent_id: "config-security-baseline"
- role: "Establishes config separation and security baseline; prevents secrets leakage"
- phase_applicability: ["PreProject", "ReleaseGate"]
- primary_outputs:
  - ".env.example"
  - "docs/SECURITY.md"
  - "docs/CONFIG.md"
- gates_enforced:
  - "no_secrets_in_code"
  - "config_separation"
  - "example_env_present"

## Agent
- agent_id: config-security-baseline
- role: Ensure config is externalized and security basics are documented.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
- Create/validate .env.example and .gitignore rules.
- Add SECURITY.md and CONFIG.md.
- Define config conventions and validation expectations.

## Tools and commands
- Secret scan:
  - `grep -RIn "(api_key|apikey|token|secret|password)" src docs`

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- no_secrets_in_code: pass/fail
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
