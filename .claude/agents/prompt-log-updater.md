# prompt-log-updater.md
- agent_id: "prompt-log-updater"
- role: "Appends prompt usage and lessons learned to the prompt log"
- phase_applicability: ["TaskLoop", "ResearchLoop", "ReleaseGate"]
- primary_outputs:
  - "docs/development/PROMPT_LOG.md"
  - "PROMPT_BOOK.md"
- gates_enforced:
  - "prompt_log_updated"

## Agent
- agent_id: prompt-log-updater
- role: Maintain prompt engineering traceability.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
**CRITICAL - Must maintain TWO files:**

1. **docs/development/PROMPT_LOG.md** - Development prompt history:
   - Append entry for current agent/task
   - Include: timestamp, phase, agent_id, task description
   - Document prompts used (sanitized, no secrets)
   - Record outputs and changes made
   - Note iterations and refinements
   - Capture lessons learned
   - Track token consumption (if available)

2. **PROMPT_BOOK.md** - User-facing prompt guide (created/updated at ReleaseGate):
   - Distilled best prompts for USING the system (not building it)
   - Organized by use case or feature
   - Example prompts for common tasks
   - Expected responses/behavior
   - Tips and best practices
   - Troubleshooting prompts
   - Advanced usage examples

**For PROMPT_LOG.md entry format:**
```markdown
## [YYYY-MM-DD HH:MM] Phase: TaskLoop | Agent: implementer
**Task:** Implement player registration

**Prompts used:**
- "Create a PlayerRegistration class that..."
- "Add validation for player_id format"

**Outputs:**
- Created: src/player/registration.py
- Modified: src/player/__init__.py

**Iterations:** 2 (initial + validation fix)

**Lessons learned:**
- Validation should happen before state changes
- Clear error messages improve debugging

**Token estimate:** ~2000 tokens
```

**For PROMPT_BOOK.md structure:**
```markdown
# Prompt Book

## Player Registration
**Prompt:** "Register a new player with ID 'player-001'"
**Expected:** Player registered successfully with confirmation

## Match Execution
...

## Troubleshooting
**Issue:** Registration fails
**Prompt:** "Check registration logs for player-001"
...
```

**Validation:**
- PROMPT_LOG.md has entry for current agent execution
- If in ReleaseGate phase, PROMPT_BOOK.md exists and has at least 5 example prompts
- No secrets in either file

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- prompt_log_updated: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
