# ADR-XXX: [Title of Decision]

## Status
[Proposed | Accepted | Deprecated | Superseded]

If superseded, link to the superseding ADR.

## Context
Describe the context and background that led to this decision. Include:
- What problem are we trying to solve?
- What constraints exist?
- What forces are at play?
- What alternatives were considered?

## Decision
State the decision clearly and concisely. This should be a single sentence if possible, followed by detailed explanation if needed.

Example: "We will use JSON-RPC 2.0 over HTTP as the transport protocol for all agent communication."

## Rationale
Explain why this decision was made. Include:
- Benefits of the chosen approach
- Trade-offs considered
- Why alternatives were rejected
- How this aligns with system goals and principles

## Consequences

### Positive
- List positive consequences
- What becomes easier or better?
- What capabilities are enabled?

### Negative
- List negative consequences or trade-offs
- What becomes harder?
- What limitations are introduced?

### Neutral
- List consequences that are neither clearly positive nor negative
- Changes that are noteworthy but neutral in impact

## Implementation Notes
- Key implementation considerations
- Dependencies on other components or decisions
- Migration path (if applicable)
- Testing strategy (if applicable)

## Alternatives Considered

### Alternative 1: [Name]
- **Description**: Brief description of the alternative
- **Pros**: Benefits of this approach
- **Cons**: Drawbacks of this approach
- **Reason for rejection**: Why this was not chosen

### Alternative 2: [Name]
- **Description**: Brief description of the alternative
- **Pros**: Benefits of this approach
- **Cons**: Drawbacks of this approach
- **Reason for rejection**: Why this was not chosen

## References
- Link to related PRD sections
- Link to related documentation
- External references (specifications, articles, etc.)
- Related ADRs

## Metadata
- **Author**: [Name or role]
- **Date**: YYYY-MM-DD
- **Reviewers**: [Names or roles]
- **Related ADRs**: [Links to related ADRs]
- **Related PRD Sections**: [Links to PRD sections]

---

## Usage Instructions

When creating a new ADR:

1. Copy this template to a new file: `docs/ADRs/NNN-short-title.md`
   - Use a sequential three-digit number (e.g., 001, 002, 003)
   - Use kebab-case for the short title

2. Fill in all sections:
   - Set status to "Proposed" initially
   - Provide thorough context and rationale
   - List at least 2-3 alternatives considered
   - Be specific about consequences

3. Update status as the ADR progresses:
   - "Proposed" → "Accepted" when approved
   - "Accepted" → "Deprecated" when no longer applicable
   - "Accepted" → "Superseded" when replaced by another ADR

4. Link ADRs from:
   - Architecture documentation
   - Related ADRs
   - Implementation code (in comments where relevant)

5. Keep ADRs immutable after acceptance:
   - Do not edit accepted ADRs
   - Create new ADRs to supersede old ones
   - Update status and add superseding links

## Best Practices

- **Be concise but complete**: Each section should be thorough but focused
- **Use concrete examples**: Abstract decisions are hard to understand
- **Explain trade-offs**: Every decision has pros and cons
- **Document context**: Future readers won't have today's context
- **Link to evidence**: Reference PRD sections, benchmarks, research
- **Keep it technical**: ADRs are for technical decisions, not policy
- **Review and iterate**: Get feedback before accepting
- **Date all decisions**: Context changes over time
