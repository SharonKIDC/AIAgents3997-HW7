# Section 9 - Configuration and Extensibility

## 9.1 Purpose
Defines how the system supports multiple game types and evolves without breaking the league core.

## 9.2 Game Registry
Games are declared via configuration. Each game entry defines:
- game_type identifier
- referee responsibility for validating move payloads
- scoring semantics (points per outcome)

## 9.3 Extensibility Constraints
- Adding a new game must not require changes to:
  - League Manager
  - Transport protocol or envelope format
- Only referees contain game-specific logic
- League Manager treats game metadata as opaque

## 9.4 Non-Goals
This section does not define plugin loading mechanisms or dynamic code execution.
