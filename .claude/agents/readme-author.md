# readme-author.md
- agent_id: "readme-author"
- role: "Creates a comprehensive README baseline"
- phase_applicability: ["PreProject"]
- primary_outputs:
  - "README.md"
  - "docs/CONTRIBUTING.md"
- gates_enforced:
  - "readme_updated_if_needed"

## Agent
- agent_id: readme-author
- role: Build a submission-grade README baseline.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
**CRITICAL - Must create TWO files:**

1. **README.md** - Main project documentation:
   - Project overview and purpose
   - Key features
   - Installation instructions
   - Requirements and dependencies
   - Configuration guide
   - Usage examples (link to docs/USAGE.md for details)
   - Quick start guide
   - Troubleshooting section
   - Link to CONTRIBUTING.md
   - License and credits
   - Links to additional documentation

2. **docs/CONTRIBUTING.md** - Contribution guidelines:
   - How to set up development environment
   - Code style and standards
   - Testing requirements
   - Pull request process
   - Issue reporting guidelines
   - Code of conduct
   - Development workflow
   - How to run tests
   - How to submit changes

**Validation:**
- Both files must exist
- README.md includes installation and quick start
- CONTRIBUTING.md has clear development setup instructions

## Changes
- Provide diffs for README.md.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- readme_updated_if_needed: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
