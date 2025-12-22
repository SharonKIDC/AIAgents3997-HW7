# ADR-001: JSON-RPC over HTTP for Transport

## Status
Accepted

## Context
The Agent League System requires a transport protocol for communication between autonomous agents (League Manager, Referees, and Players). The chosen protocol must support:

1. **Interoperability**: Agents may be implemented in different languages or frameworks
2. **Structured messaging**: Clear request/response semantics with type-safe payloads
3. **Protocol versioning**: Support for envelope-based versioning to evolve over time
4. **Auditability**: Messages must be easily logged and replayed for compliance
5. **Simplicity**: Minimize implementation complexity for agent developers
6. **Localhost deployment**: System operates on localhost only (no network security required)
7. **Debugging**: Human-readable messages for development and troubleshooting

The PRD explicitly requires:
- All communication over HTTP
- Single endpoint per agent: `POST /mcp`
- JSON-RPC 2.0 format
- League protocol envelope for routing and validation (Section 2)

Several transport alternatives were considered before selecting JSON-RPC over HTTP.

## Decision
We will use JSON-RPC 2.0 over HTTP as the exclusive transport protocol for all agent communication in the Agent League System.

All messages will:
- Use HTTP POST to a single endpoint: `/mcp`
- Follow JSON-RPC 2.0 specification strictly
- Include a league-specific protocol envelope within `params`
- Use a single MCP method: `"league.handle"`
- Route internally based on `params.envelope.message_type`

## Rationale

### Alignment with MCP (Model Context Protocol)
The PRD explicitly references MCP-compatible JSON-RPC, indicating intent to align with emerging standards for AI agent communication. Using JSON-RPC over HTTP at `/mcp` provides:
- Compatibility with MCP tooling and libraries
- Potential for future integration with MCP ecosystems
- Familiar patterns for developers working with AI agents

### Simplicity and Universality
JSON-RPC 2.0 is:
- Simple to implement (minimal specification)
- Supported by libraries in all major languages (Python, JavaScript, Go, Java, etc.)
- Human-readable (JSON text format)
- Widely understood by developers

### Single-Endpoint Architecture
Using a single endpoint (`/mcp`) per agent simplifies:
- Service discovery: Each agent has one well-known endpoint
- Routing: Message type determines handler, not URL path
- Authentication: Token validation occurs at envelope level, not endpoint level
- Logging: All messages flow through one point for complete audit trails

### Protocol Envelope Pattern
Embedding a league-specific envelope within JSON-RPC `params` allows:
- **Versioning**: `protocol: "league.v2"` enables protocol evolution
- **Routing**: `message_type` determines internal dispatch
- **Context**: Contextual fields (league_id, match_id, etc.) travel with every message
- **Authentication**: `auth_token` is validated consistently across all message types
- **Traceability**: `conversation_id` enables request/response correlation

### Request/Response Semantics
JSON-RPC provides clear semantics:
- Every request has an `id` for correlation
- Responses include the same `id`
- Error responses have standardized structure (`code`, `message`, `data`)
- No ambiguity about request vs. notification vs. response

### Auditability
JSON text format enables:
- Append-only audit logs in JSON Lines format
- Easy parsing for compliance and debugging
- Replay capability for testing and verification
- Human inspection without specialized tools

## Consequences

### Positive
1. **Rapid development**: Developers can use existing JSON-RPC libraries instead of implementing custom protocols
2. **Interoperability**: Agents can be implemented in any language with HTTP and JSON support
3. **Debugging**: Human-readable messages make troubleshooting straightforward
4. **Compliance**: Audit logs are easily inspected and validated
5. **Extensibility**: Envelope pattern allows protocol evolution without breaking existing agents
6. **Testability**: Mock servers and clients are trivial to implement
7. **MCP alignment**: Positions system for future MCP ecosystem integration

### Negative
1. **Verbosity**: JSON is more verbose than binary protocols (higher bandwidth for large payloads)
2. **Parsing overhead**: JSON serialization/deserialization is slower than binary formats
3. **No streaming**: JSON-RPC is request/response only; no native support for streaming or server push
4. **Single endpoint complexity**: All routing logic is internal, not REST-style URL-based
5. **HTTP overhead**: Each message requires full HTTP request/response cycle (no persistent connections by default)

### Neutral
1. **Single method pattern**: Using `"league.handle"` for all messages is unconventional but consistent
2. **Envelope nesting**: League envelope is nested within JSON-RPC params, adding one layer of nesting
3. **No HTTP semantics**: HTTP status codes are always 200 OK; errors are in JSON-RPC error object
4. **Localhost only**: Performance characteristics differ from network deployment

## Implementation Notes

### HTTP Server Requirements
- Must support HTTP POST
- Must accept `Content-Type: application/json`
- Must return `Content-Type: application/json`
- Should return HTTP 200 OK for all valid JSON-RPC messages (errors in JSON-RPC error object)
- Should return HTTP 400 Bad Request for invalid JSON or malformed requests

### JSON-RPC Validation
All messages must be validated for:
- `jsonrpc: "2.0"` (exact match)
- `method: "league.handle"` (exact match)
- `params` is an object containing `envelope` and optionally `payload`
- `id` is present and unique per request

### Envelope Validation
All envelopes must be validated for:
- `protocol: "league.v2"` (version enforcement)
- `message_type` is a known type
- `sender` matches authenticated identity (post-registration)
- `timestamp` is ISO-8601 UTC
- `conversation_id` is UUID v4
- Contextual fields are present when required

### Error Handling
Protocol errors return JSON-RPC error responses:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": {
      "envelope": { /* original envelope */ },
      "details": "Missing required field: auth_token"
    }
  },
  "id": "<request_id>"
}
```

### Recommended Libraries
- **Python**: jsonrpcserver, jsonrpcclient, or built-in `http.server` + `json`
- **JavaScript**: `jayson`, `json-rpc-2.0`
- **Go**: `net/rpc/jsonrpc` or third-party libraries
- **Java**: `jsonrpc4j`, `json-rpc-2.0`

### Timeout Handling
- HTTP client timeouts should be set per league policy (see timeout_policy.yaml)
- Servers should not hold connections open beyond reasonable processing time
- Retries should use exponential backoff

### Logging
- Log all requests and responses to audit log (JSON Lines format)
- Include full message body for auditability
- Do not log sensitive data (tokens should be redacted in logs accessible outside the system)

## Alternatives Considered

### Alternative 1: gRPC
- **Description**: Use gRPC with Protocol Buffers for efficient binary communication
- **Pros**:
  - High performance (binary protocol, HTTP/2 multiplexing)
  - Strong typing with .proto schemas
  - Built-in streaming support
  - Code generation for multiple languages
- **Cons**:
  - Binary format is not human-readable (harder to debug)
  - Requires .proto schema management and code generation
  - More complex setup than JSON-RPC
  - Overkill for localhost-only deployment
  - Less aligned with MCP standards
- **Reason for rejection**: Complexity outweighs performance benefits for localhost deployment. Human readability is prioritized for auditability and debugging.

### Alternative 2: WebSocket with Custom Protocol
- **Description**: Use WebSocket connections with custom JSON message format
- **Pros**:
  - Persistent connections reduce overhead
  - Supports server-initiated messages (push notifications)
  - Lower latency for high-frequency messaging
- **Cons**:
  - Requires custom protocol design and implementation
  - More complex connection management (reconnection, heartbeats)
  - No standard specification (less interoperable)
  - Persistent connections not needed for infrequent league operations
  - Does not align with MCP patterns
- **Reason for rejection**: Request/response pattern is sufficient for league operations. Connection management complexity is unnecessary.

### Alternative 3: REST over HTTP with JSON
- **Description**: Use RESTful HTTP endpoints with JSON payloads (e.g., POST /matches, GET /standings)
- **Pros**:
  - Widely understood REST semantics
  - URL-based routing (semantic endpoints)
  - HTTP verbs convey intent (GET, POST, PUT, DELETE)
  - Standard HTTP status codes
- **Cons**:
  - Multiple endpoints complicate service discovery
  - No standardized envelope or versioning pattern
  - Less aligned with MCP single-endpoint pattern
  - Requires custom error response format
  - No built-in request/response correlation (must implement manually)
- **Reason for rejection**: PRD explicitly requires single `/mcp` endpoint. REST's multi-endpoint model conflicts with MCP alignment.

### Alternative 4: GraphQL
- **Description**: Use GraphQL for flexible querying and mutations
- **Pros**:
  - Flexible query language
  - Single endpoint (`/graphql`)
  - Strong schema with introspection
  - Efficient data fetching (no over-fetching)
- **Cons**:
  - Schema complexity for simple request/response patterns
  - Overkill for non-query operations (match execution is procedural, not data-centric)
  - Less aligned with MCP standards
  - Steeper learning curve for agent implementers
- **Reason for rejection**: GraphQL is optimized for flexible data querying, not procedural agent communication. JSON-RPC is simpler and more appropriate.

### Alternative 5: Message Queue (e.g., RabbitMQ, Redis Pub/Sub)
- **Description**: Use message queue for asynchronous agent communication
- **Pros**:
  - Decouples senders and receivers
  - Built-in message persistence and replay
  - Supports pub/sub patterns
  - High throughput for message-heavy systems
- **Cons**:
  - Requires external message broker deployment
  - Adds operational complexity
  - Overkill for localhost deployment
  - Request/response correlation is manual
  - Does not align with MCP HTTP-based pattern
- **Reason for rejection**: External dependencies and operational complexity are unacceptable for localhost-only deployment. HTTP is simpler and sufficient.

## References
- [PRD Section 2: Transport, MCP, and Protocol Envelope](../prd/section-2-transport-and-protocol.md)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Architecture Documentation - API Specifications](../Architecture.md#4-api-and-contract-specifications)
- Protocol examples:
  - [register_player_request.json](../protocol/examples/register_player_request.json)
  - [register_referee_request.json](../protocol/examples/register_referee_request.json)
  - [match_result_report.json](../protocol/examples/match_result_report.json)

## Metadata
- **Author**: architecture-author agent
- **Date**: 2025-01-21
- **Status**: Accepted
- **Related ADRs**: None (foundational decision)
- **Related PRD Sections**:
  - Section 1: Scope and Actors
  - Section 2: Transport, MCP, and Protocol Envelope
  - Section 7: Timeouts, Errors, and Recovery
