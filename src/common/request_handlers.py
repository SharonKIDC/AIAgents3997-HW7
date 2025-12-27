"""Common request handling utilities.

This module provides shared error handling patterns for JSON-RPC
request handlers.
"""

import logging
from typing import Callable

from .errors import ErrorCode, LeagueError
from .protocol import (
    JSONRPCRequest,
    JSONRPCResponse,
    create_error_response,
)

logger = logging.getLogger(__name__)


def create_league_error_response(error: LeagueError, request_id: str) -> JSONRPCResponse:
    """Create error response from LeagueError.

    Args:
        error: LeagueError exception
        request_id: Request ID

    Returns:
        JSON-RPC error response
    """
    logger.warning("League error: %s", error)
    return create_error_response(int(error.code), error.message, error.details, request_id)


def create_validation_error_response(error: Exception, request_id: str) -> JSONRPCResponse:
    """Create error response from validation error.

    Args:
        error: Validation exception
        request_id: Request ID

    Returns:
        JSON-RPC error response
    """
    logger.error("Invalid request data: %s", error)
    return create_error_response(
        ErrorCode.INVALID_MESSAGE_TYPE, f"Invalid request: {str(error)}", request_id=request_id
    )


def create_internal_error_response(error: Exception, request_id: str) -> JSONRPCResponse:
    """Create error response from internal error.

    Args:
        error: Exception
        request_id: Request ID

    Returns:
        JSON-RPC error response
    """
    logger.exception("Unexpected error handling request")
    return create_error_response(
        ErrorCode.INTERNAL_ERROR, f"Internal error: {str(error)}", request_id=request_id
    )


def handle_request_errors(
    request: JSONRPCRequest, handler: Callable[[JSONRPCRequest], JSONRPCResponse]
) -> JSONRPCResponse:
    """Wrap request handler with standard error handling.

    Args:
        request: JSON-RPC request
        handler: Request handler function

    Returns:
        JSON-RPC response (success or error)
    """
    try:
        return handler(request)
    except LeagueError as e:
        return create_league_error_response(e, request.id)
    except (ValueError, KeyError) as e:
        return create_validation_error_response(e, request.id)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return create_internal_error_response(e, request.id)
