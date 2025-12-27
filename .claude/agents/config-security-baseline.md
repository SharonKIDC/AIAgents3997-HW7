# config-security-baseline.md
- agent_id: "config-security-baseline"
- role: "Establishes config separation and security baseline; prevents secrets leakage"
- phase_applicability: ["PreProject", "ReleaseGate"]
- primary_outputs:
  - ".env.example"
  - "config.yaml"
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
**CRITICAL - Must create/update these files:**

1. **.env.example** - Template for environment variables:
   - All configurable parameters with example values
   - NO real secrets (use placeholder values)
   - Comments explaining each variable
   - Required vs. optional variables clearly marked

2. **config.yaml** - Application configuration template:
   - Default configuration values
   - Environment-specific overrides
   - All non-secret configuration
   - Validation schemas if applicable

3. **docs/SECURITY.md** - Security guidelines:
   - How to handle secrets securely
   - Security best practices
   - Vulnerability reporting process
   - Authentication/authorization patterns used

4. **docs/CONFIG.md** - Configuration documentation:
   - Complete list of all config options
   - Explanation of each variable
   - How to override defaults
   - Environment-specific configuration

**Migration tasks:**
- Scan src/** for hardcoded config values
- Move to environment variables or config.yaml
- Update .gitignore to exclude .env, *.local.yaml, etc.
- Ensure no secrets in version control

**Validation:**
- Run: `grep -RIn "(api_key|apikey|token|secret|password|private)" src docs`
- Ensure no matches in committed code
- Verify .env.example has all required variables
- Verify .gitignore includes .env pattern

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
