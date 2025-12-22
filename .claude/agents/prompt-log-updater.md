# prompt-log-updater.md
- agent_id: "prompt-log-updater"
- role: "Appends prompt usage and lessons learned to the prompt log"
- phase_applicability: ["TaskLoop", "ResearchLoop", "ReleaseGate"]
- primary_outputs:
  - "docs/PROMPT_LOG.md"
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
- Append an entry summarizing purpose, prompts (no secrets), outputs, iterations, lessons learned.

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
