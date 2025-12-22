# Section 3 - Registration and Authentication Flow

## 3.1 Purpose
This section defines how agents join the league, how identities are established, and how authentication is enforced.

The registration flow ensures:
- Only known and authorized agents participate
- All subsequent communication is authenticated
- League startup order is deterministic
- Misbehaving or late agents are rejected early

## 3.2 Registration Scope
Registration is a mandatory prerequisite for:
- Referees
- Players

The League Manager does not register; it is the root authority.

## 3.3 Registration Ordering Constraints
Registration follows a strict order:
1. Referees must register first
2. Players may register only after at least one referee is registered
3. League scheduling starts only after registration closes (policy defined by League Manager configuration)

Violations result in rejection.

## 3.4 Registration Conversation Model
- Each registration flow uses a unique `conversation_id`
- Registration is request-response
- Registration is initiated by the registering agent
- The League Manager is authoritative

## 3.5 Referee Registration

### 3.5.1 Referee Registration Request
Requirements:
- Must follow Section 2 envelope
- Must include a unique `referee_id`
- Must not include `auth_token`

### 3.5.2 Referee Registration Response
If accepted, the League Manager returns:
- Confirmation
- `auth_token`
- `league_id`

If rejected, return a league-level error response.

Normative example:
- `docs/protocol/examples/register_referee_request.json`

## 3.6 Player Registration

### 3.6.1 Preconditions
Accepted only if:
- At least one referee is registered
- Registration window is open
- `player_id` is unique

### 3.6.2 Player Registration Request
Requirements:
- Must not include `auth_token`
- Must include a unique `player_id`

### 3.6.3 Player Registration Response
If accepted, the League Manager returns:
- Confirmation
- `auth_token`
- `league_id`

Normative example:
- `docs/protocol/examples/register_player_request.json`

## 3.7 Authentication Token Semantics
- Tokens are opaque strings
- Tokens are scoped to a single league
- Tokens are bound to agent type and agent identifier
- Tokens must be included in the envelope for all post-registration messages

Tokens are invalidated when:
- League shuts down
- Agent is suspended or removed

## 3.8 Failure Handling (High Level)
- Registration requests must be answered within a fixed timeout (defined in Section 7)
- Duplicate registration attempts are rejected
- Invalid or malformed requests are rejected

## 3.9 State Transition
Upon successful registration:
- INIT → REGISTERED
- REGISTERED → ACTIVE once assigned to a match or league activity
