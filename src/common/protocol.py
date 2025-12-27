"""Protocol definitions and validation for the Agent League System.

This module implements the league.v2 protocol envelope structure,
message type definitions, and validation rules as specified in the PRD.
"""

import re
import uuid
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .errors import ErrorCode, ProtocolError, ValidationError


class MessageType(str, Enum):
    """Enumeration of all valid message types in the league protocol."""

    # League Manager - Referee messages
    REGISTER_REFEREE_REQUEST = "REGISTER_REFEREE_REQUEST"
    REGISTER_REFEREE_RESPONSE = "REGISTER_REFEREE_RESPONSE"
    MATCH_ASSIGNMENT = "MATCH_ASSIGNMENT"
    MATCH_ASSIGNMENT_ACK = "MATCH_ASSIGNMENT_ACK"
    MATCH_RESULT_REPORT = "MATCH_RESULT_REPORT"
    MATCH_RESULT_ACK = "MATCH_RESULT_ACK"

    # League Manager - Player messages
    REGISTER_PLAYER_REQUEST = "REGISTER_PLAYER_REQUEST"
    REGISTER_PLAYER_RESPONSE = "REGISTER_PLAYER_RESPONSE"
    QUERY_STANDINGS = "QUERY_STANDINGS"
    STANDINGS_RESPONSE = "STANDINGS_RESPONSE"

    # League Manager - Agent Ready messages
    AGENT_READY_REQUEST = "AGENT_READY_REQUEST"
    AGENT_READY_RESPONSE = "AGENT_READY_RESPONSE"

    # League Manager - Admin messages
    ADMIN_START_LEAGUE_REQUEST = "ADMIN_START_LEAGUE_REQUEST"
    ADMIN_START_LEAGUE_RESPONSE = "ADMIN_START_LEAGUE_RESPONSE"
    ADMIN_GET_STATUS_REQUEST = "ADMIN_GET_STATUS_REQUEST"
    ADMIN_GET_STATUS_RESPONSE = "ADMIN_GET_STATUS_RESPONSE"

    # Referee - Player messages
    GAME_INVITATION = "GAME_INVITATION"
    GAME_JOIN_ACK = "GAME_JOIN_ACK"
    REQUEST_MOVE = "REQUEST_MOVE"
    MOVE_RESPONSE = "MOVE_RESPONSE"
    GAME_OVER = "GAME_OVER"


PROTOCOL_VERSION = "league.v2"
JSONRPC_VERSION = "2.0"
MCP_METHOD = "league.handle"


@dataclass
class Envelope:
    """Protocol envelope wrapping all league messages.

    The envelope contains metadata required for routing, authentication,
    and audit logging. All fields are validated according to PRD Section 2.
    """

    # Required fields (always present)
    protocol: str
    message_type: str
    sender: str
    timestamp: str
    conversation_id: str

    # Contextual fields (required when applicable)
    auth_token: Optional[str] = None
    league_id: Optional[str] = None
    round_id: Optional[str] = None
    match_id: Optional[str] = None
    game_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert envelope to dictionary, excluding None values.

        Returns:
            Dictionary representation of envelope
        """
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Envelope":
        """Create envelope from dictionary with validation.

        Args:
            data: Dictionary containing envelope fields

        Returns:
            Validated Envelope instance

        Raises:
            ValidationError: If required fields are missing or invalid
        """
        # Validate required fields
        required = ["protocol", "message_type", "sender", "timestamp", "conversation_id"]
        for field_name in required:
            if field_name not in data:
                raise ValidationError(
                    f"Missing required envelope field: {field_name}", field=field_name
                )

        # Validate protocol version
        if data["protocol"] != PROTOCOL_VERSION:
            raise ProtocolError(
                ErrorCode.INVALID_PROTOCOL_VERSION,
                f"Invalid protocol version: {data['protocol']}",
                {"expected": PROTOCOL_VERSION, "actual": data["protocol"]},
            )

        # Validate message type
        try:
            MessageType(data["message_type"])
        except ValueError as exc:
            raise ProtocolError(
                ErrorCode.INVALID_MESSAGE_TYPE,
                f"Unknown message type: {data['message_type']}",
                {"message_type": data["message_type"]},
            ) from exc

        # Validate sender format
        validate_sender_format(data["sender"])

        # Validate timestamp format
        validate_timestamp(data["timestamp"])

        # Validate conversation_id format
        validate_uuid(data["conversation_id"], "conversation_id")

        field_names = {field.name for field in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in field_names})


def validate_sender_format(sender: str) -> None:
    """Validate sender identity format.

    Valid formats:
    - league_manager
    - admin
    - referee:<referee_id>
    - player:<player_id>

    Args:
        sender: Sender identity string

    Raises:
        ValidationError: If format is invalid
    """
    if sender in ["league_manager", "admin"]:
        return

    pattern = r"^(referee|player):[a-zA-Z0-9_-]+$"
    if not re.match(pattern, sender):
        raise ValidationError(
            f"Invalid sender format: {sender}",
            field="sender",
            expected_format="league_manager|admin|referee:<id>|player:<id>",
        )


def validate_timestamp(timestamp: str) -> None:
    """Validate timestamp is ISO-8601 UTC format.

    Args:
        timestamp: ISO-8601 timestamp string

    Raises:
        ValidationError: If timestamp is invalid or not UTC
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        # Ensure it's UTC
        if dt.utcoffset().total_seconds() != 0:
            raise ValidationError(f"Timestamp must be UTC: {timestamp}", field="timestamp")
    except (ValueError, AttributeError) as e:
        raise ValidationError(
            f"Invalid timestamp format: {timestamp}", field="timestamp", error=str(e)
        ) from e


def validate_uuid(value: str, field_name: str) -> None:
    """Validate string is a valid UUID.

    Args:
        value: String to validate
        field_name: Name of field being validated

    Raises:
        ValidationError: If not a valid UUID
    """
    try:
        uuid.UUID(value)
    except ValueError as exc:
        raise ValidationError(
            f"Invalid UUID format for {field_name}: {value}", field=field_name
        ) from exc


@dataclass
class JSONRPCRequest:
    """JSON-RPC 2.0 request structure."""

    jsonrpc: str
    method: str
    params: Dict[str, Any]
    id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JSONRPCRequest":
        """Create request from dictionary with validation.

        Args:
            data: Dictionary containing JSON-RPC fields

        Returns:
            Validated JSONRPCRequest instance

        Raises:
            ProtocolError: If validation fails
        """
        # Validate JSON-RPC version
        if data.get("jsonrpc") != JSONRPC_VERSION:
            raise ProtocolError(
                ErrorCode.INVALID_JSON_RPC,
                f"Invalid JSON-RPC version: {data.get('jsonrpc')}",
                {"expected": JSONRPC_VERSION},
            )

        # Validate method
        if data.get("method") != MCP_METHOD:
            raise ProtocolError(
                ErrorCode.INVALID_METHOD,
                f"Invalid method: {data.get('method')}",
                {"expected": MCP_METHOD},
            )

        # Validate params structure
        if "params" not in data or not isinstance(data["params"], dict):
            raise ProtocolError(
                ErrorCode.MISSING_REQUIRED_FIELD, "Missing or invalid 'params' field"
            )

        # Validate envelope exists
        if "envelope" not in data["params"]:
            raise ProtocolError(ErrorCode.MISSING_ENVELOPE, "Missing 'envelope' in params")

        return cls(
            jsonrpc=data["jsonrpc"],
            method=data["method"],
            params=data["params"],
            id=data.get("id", ""),
        )


@dataclass
class JSONRPCResponse:
    """JSON-RPC 2.0 response structure."""

    jsonrpc: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        response = {"jsonrpc": self.jsonrpc}
        if self.result is not None:
            response["result"] = self.result
        if self.error is not None:
            response["error"] = self.error
        # Always include id field (per JSON-RPC 2.0 spec)
        response["id"] = self.id
        return response


def create_success_response(
    envelope: Envelope, payload: Dict[str, Any], request_id: str
) -> JSONRPCResponse:
    """Create a success JSON-RPC response.

    Args:
        envelope: Response envelope
        payload: Response payload
        request_id: Original request ID

    Returns:
        JSONRPCResponse with result
    """
    return JSONRPCResponse(
        jsonrpc=JSONRPC_VERSION,
        result={"envelope": envelope.to_dict(), "payload": payload},
        id=request_id,
    )


def create_error_response(
    error_code: int,
    error_message: str,
    error_data: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> JSONRPCResponse:
    """Create an error JSON-RPC response.

    Args:
        error_code: Error code
        error_message: Error message
        error_data: Optional additional error data
        request_id: Original request ID (may be None if request was invalid)

    Returns:
        JSONRPCResponse with error
    """
    return JSONRPCResponse(
        jsonrpc=JSONRPC_VERSION,
        error={"code": error_code, "message": error_message, "data": error_data or {}},
        id=request_id,
    )


def generate_conversation_id() -> str:
    """Generate a new UUID v4 conversation ID.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def generate_message_id() -> str:
    """Generate a new UUID v4 message/request ID.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def utc_now() -> str:
    """Get current UTC timestamp in ISO-8601 format.

    Returns:
        ISO-8601 timestamp string with Z suffix
    """
    return datetime.utcnow().isoformat() + "Z"
