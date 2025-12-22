# Section 2 - Transport, MCP, and Protocol Envelope

## 2.1 Purpose
This section defines the transport mechanism, message invocation format, and mandatory protocol envelope used by all agents in the league.

Goals:
- Interoperability between independently implemented agents
- Strict validation of messages
- Deterministic, auditable communication
- Game-agnostic message routing

## 2.2 Transport Layer
- All communication uses HTTP.
- All messages are sent to a single endpoint per agent:
  - `POST /mcp`
- Payload format is JSON-RPC 2.0.

## 2.3 JSON-RPC Requirements
Every request must include:
- `jsonrpc`: must be `"2.0"`
- `method`: MCP method name
- `params`: object containing league protocol envelope and payload
- `id`: client-generated request identifier

Requests missing required fields are rejected.

## 2.4 MCP Method Convention
All league-related communication uses a single MCP method:
- `method: "league.handle"`

Receivers dispatch internally based on `params.envelope.message_type`.

## 2.5 Protocol Envelope (Mandatory)
All league messages must be wrapped inside:
- `params.envelope`

### 2.5.1 Required Envelope Fields
- `protocol`: fixed `"league.v2"`
- `message_type`: logical message type
- `sender`: sender identity
- `timestamp`: UTC timestamp
- `conversation_id`: conversation/session identifier

### 2.5.2 Sender format
Allowed formats:
- `league_manager`
- `referee:<referee_id>`
- `player:<player_id>`

Receivers validate that sender identity matches the authenticated token (where applicable).

### 2.5.3 Timestamp constraints
- ISO-8601 format
- Must be expressed in UTC
- Must include timezone designator (`Z` or `+00:00`)

## 2.6 Contextual Envelope Fields
These fields are required only when contextually relevant:
- `auth_token`: after registration
- `league_id`: league-scoped operations
- `round_id`: round announcements
- `match_id`: match execution
- `game_type`: match assignment and execution

Messages missing required contextual fields are rejected.

## 2.7 Validation Rules (Hard Requirements)
Receivers must reject messages when:
- `protocol` is unknown
- `jsonrpc` is not `"2.0"`
- `method` is not `"league.handle"`
- required envelope fields are missing
- timestamp is not UTC
- sender identity does not match authentication token (post-registration)
- contextual identifiers are missing or inconsistent

Rejected messages return a protocol-level error response (defined in Section 7).

## 2.8 Normative examples
- `docs/protocol/examples/register_player_request.json`
- `docs/protocol/examples/register_referee_request.json`
- `docs/protocol/examples/match_result_report.json`

These files are normative for field placement and nesting.
