"""Error codes and exceptions for the Agent League System.

This module defines all error codes and exception types used throughout
the league system, ensuring consistent error handling and reporting.
"""

from enum import IntEnum
from typing import Any, Dict, Optional


class ErrorCode(IntEnum):
    """Standard error codes for league protocol violations and failures."""

    # Protocol Errors (4xx equivalent) - Client errors
    INVALID_JSON_RPC = 4000
    INVALID_PROTOCOL_VERSION = 4001
    INVALID_METHOD = 4002
    MISSING_ENVELOPE = 4003
    INVALID_ENVELOPE_FIELD = 4004
    MISSING_REQUIRED_FIELD = 4005
    INVALID_MESSAGE_TYPE = 4006
    INVALID_SENDER_FORMAT = 4007
    INVALID_TIMESTAMP = 4008
    AUTHENTICATION_FAILED = 4009
    AUTHORIZATION_FAILED = 4010
    DUPLICATE_REGISTRATION = 4011
    REGISTRATION_CLOSED = 4012
    INVALID_AGENT_STATE = 4013
    INVALID_MATCH_ID = 4014
    INVALID_ROUND_ID = 4015
    INVALID_LEAGUE_ID = 4016
    DUPLICATE_RESULT = 4017
    VALIDATION_ERROR = 4018
    PRECONDITION_FAILED = 4019
    INVALID_REFEREE_ID = 4020
    INVALID_PLAYER_ID = 4021

    # Operational Errors (5xx equivalent) - Server errors
    INTERNAL_ERROR = 5000
    DATABASE_ERROR = 5001
    TIMEOUT_EXCEEDED = 5002
    REFEREE_UNAVAILABLE = 5003
    MATCH_EXECUTION_FAILED = 5004
    STATE_CORRUPTION = 5005
    PERSISTENCE_FAILED = 5006
    AUDIT_LOG_FAILED = 5007
    CONFIGURATION_ERROR = 5008
    COMMUNICATION_ERROR = 5009


class LeagueError(Exception):
    """Base exception for all league-related errors."""

    def __init__(self, code: ErrorCode, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a league error.

        Args:
            code: The error code
            message: Human-readable error message
            details: Optional additional context
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code.name}] {message}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for JSON-RPC responses.

        Returns:
            Dictionary with code, message, and data fields
        """
        return {
            "code": int(self.code),
            "message": self.message,
            "data": {"error_code": self.code.name, "details": self.details},
        }


class ProtocolError(LeagueError):
    """Raised when protocol validation fails (4xx errors)."""


class OperationalError(LeagueError):
    """Raised when operational failures occur (5xx errors)."""


class ValidationError(ProtocolError):
    """Raised when message validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, **details):
        """Initialize a validation error.

        Args:
            message: Error message
            field: Optional field name that failed validation
            **details: Additional context
        """
        if field:
            details["field"] = field
        super().__init__(ErrorCode.VALIDATION_ERROR, message, details)


class AuthenticationError(ProtocolError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **details):
        super().__init__(ErrorCode.AUTHENTICATION_FAILED, message, details)


class AuthorizationError(ProtocolError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Authorization failed", **details):
        super().__init__(ErrorCode.AUTHORIZATION_FAILED, message, details)


class DuplicateRegistrationError(ProtocolError):
    """Raised when an agent attempts duplicate registration."""

    def __init__(self, agent_id: str):
        super().__init__(
            ErrorCode.DUPLICATE_REGISTRATION, f"Agent {agent_id} is already registered", {"agent_id": agent_id}
        )


class RegistrationClosedError(ProtocolError):
    """Raised when registration window has closed."""

    def __init__(self):
        super().__init__(ErrorCode.REGISTRATION_CLOSED, "Registration window is closed")


class PreconditionFailedError(ProtocolError):
    """Raised when a required precondition is not met."""

    def __init__(self, message: str, **details):
        super().__init__(ErrorCode.PRECONDITION_FAILED, message, details)


class MatchTimeoutError(OperationalError):
    """Raised when an operation times out."""

    def __init__(self, message: str, timeout_ms: Optional[int] = None):
        details = {}
        if timeout_ms is not None:
            details["timeout_ms"] = timeout_ms
        super().__init__(ErrorCode.TIMEOUT_EXCEEDED, message, details)


class DatabaseError(OperationalError):
    """Raised when database operations fail."""

    def __init__(self, message: str, **details):
        super().__init__(ErrorCode.DATABASE_ERROR, message, details)


class ConfigurationError(OperationalError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, **details):
        super().__init__(ErrorCode.CONFIGURATION_ERROR, message, details)
