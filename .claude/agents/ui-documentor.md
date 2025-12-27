# ui-documentor.md
- agent_id: "ui-documentor"
- role: "Creates UI documentation with screenshots/workflows/states/accessibility notes"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "docs/UI.md"
  - "docs/assets/ui/**"
- gates_enforced:
  - "ui_docs_present"

## Agent
- agent_id: ui-documentor
- role: Produce submission-grade UI documentation.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
**CRITICAL - For CLI/API applications, create terminal examples and API interaction documentation:**

1. **Terminal Output Examples** (docs/assets/terminal/**):
   - Create markdown code blocks with actual command outputs
   - Show key features in action (registration, match execution, standings)
   - Include error scenarios and their outputs
   - Document all CLI commands with examples
   - Use ANSI color codes if applicable (with explanations)

2. **API Interaction Examples** (docs/UI.md or docs/API_EXAMPLES.md):
   - Complete request/response examples for each endpoint
   - Show JSON-RPC message formats
   - Include authentication flow examples
   - Document error responses
   - Provide curl commands or equivalent
   - Show WebSocket/HTTP interaction patterns

3. **Interface Documentation** (docs/UI.md):
   - Document all user-facing interfaces (CLI, API, protocols)
   - State diagrams for complex workflows
   - Sequence diagrams for multi-step processes
   - Error states and recovery procedures
   - Accessibility considerations (if applicable)

**For CLI applications specifically:**
- Document command syntax and options
- Show help output: `python -m <module> --help`
- Provide usage examples for common tasks
- Include configuration file examples

**Format:**
```markdown
### Feature: Player Registration

```bash
$ python -m src.player.main --register
Player ID: player-001
Registration successful!
```

**Expected output:**
- Player receives unique ID
- System confirms registration
```

**Validation:**
- At least 5 terminal examples showing key features
- All examples are actual outputs (not placeholders)
- API examples cover main endpoints
- Error scenarios documented

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- ui_docs_present: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
