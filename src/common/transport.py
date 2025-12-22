"""HTTP transport layer for the Agent League System.

This module provides HTTP server and client implementations for
JSON-RPC communication between league agents.
"""

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Dict, Any, Optional
from urllib.parse import urlparse
import http.client
import threading

from .protocol import (
    JSONRPCRequest,
    JSONRPCResponse,
    Envelope,
    create_error_response,
    JSONRPC_VERSION
)
from .errors import LeagueError, ProtocolError, ErrorCode

logger = logging.getLogger(__name__)


class LeagueHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for league protocol endpoints.

    This handler processes POST requests to /mcp and delegates
    message handling to a registered handler function.
    """

    def __init__(self, *args, message_handler: Optional[Callable] = None, **kwargs):
        """Initialize the handler.

        Args:
            message_handler: Function to handle validated requests
        """
        self.message_handler = message_handler
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests to /mcp endpoint."""
        if self.path != '/mcp':
            self.send_error(404, "Not Found")
            return

        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            # Parse JSON
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError as e:
                response = create_error_response(
                    ErrorCode.INVALID_JSON_RPC,
                    f"Invalid JSON: {str(e)}",
                    request_id=None
                )
                self._send_json_response(response.to_dict())
                return

            # Validate JSON-RPC structure
            try:
                request = JSONRPCRequest.from_dict(data)
            except (ProtocolError, LeagueError) as e:
                response = create_error_response(
                    int(e.code) if hasattr(e, 'code') else ErrorCode.INVALID_JSON_RPC,
                    str(e),
                    error_data=e.details if hasattr(e, 'details') else {},
                    request_id=data.get('id')
                )
                self._send_json_response(response.to_dict())
                return

            # Delegate to message handler
            if self.message_handler:
                try:
                    response = self.message_handler(request)
                    self._send_json_response(response.to_dict())
                except LeagueError as e:
                    response = create_error_response(
                        int(e.code),
                        e.message,
                        error_data=e.details,
                        request_id=request.id
                    )
                    self._send_json_response(response.to_dict())
                except Exception as e:
                    logger.exception("Unexpected error handling request")
                    response = create_error_response(
                        ErrorCode.INTERNAL_ERROR,
                        f"Internal error: {str(e)}",
                        request_id=request.id
                    )
                    self._send_json_response(response.to_dict())
            else:
                response = create_error_response(
                    ErrorCode.INTERNAL_ERROR,
                    "No message handler configured",
                    request_id=request.id
                )
                self._send_json_response(response.to_dict())

        except Exception as e:
            logger.exception("Error processing request")
            self.send_error(500, str(e))

    def do_GET(self):
        """Handle GET requests for health checks."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        elif self.path == '/status':
            # Status endpoint - handler should set this via server attribute
            status = getattr(self.server, 'status_provider', lambda: {"status": "unknown"})()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

    def _send_json_response(self, data: Dict[str, Any]):
        """Send JSON response.

        Args:
            data: Dictionary to send as JSON
        """
        response_body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        """Override to use standard logging."""
        logger.info(format % args)


class LeagueHTTPServer:
    """HTTP server for league agents.

    This server listens on a configured port and delegates message
    handling to a registered handler function.
    """

    def __init__(
        self,
        host: str,
        port: int,
        message_handler: Callable[[JSONRPCRequest], JSONRPCResponse],
        status_provider: Optional[Callable[[], Dict[str, Any]]] = None
    ):
        """Initialize the HTTP server.

        Args:
            host: Host to bind to
            port: Port to bind to
            message_handler: Function to handle validated requests
            status_provider: Optional function to provide status info
        """
        self.host = host
        self.port = port
        self.message_handler = message_handler
        self.status_provider = status_provider

        # Create handler factory
        def handler_factory(*args, **kwargs):
            return LeagueHTTPHandler(
                *args,
                message_handler=message_handler,
                **kwargs
            )

        self.server = HTTPServer((host, port), handler_factory)
        if status_provider:
            self.server.status_provider = status_provider
        self.thread = None

    def start(self):
        """Start the server in a background thread."""
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        logger.info(f"HTTP server started on {self.host}:{self.port}")

    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            if self.thread:
                self.thread.join()
            logger.info(f"HTTP server stopped on {self.host}:{self.port}")


class LeagueHTTPClient:
    """HTTP client for sending JSON-RPC requests to other league agents."""

    def __init__(self, timeout: int = 30):
        """Initialize the HTTP client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def send_request(
        self,
        url: str,
        envelope: Envelope,
        payload: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a JSON-RPC request to another agent.

        Args:
            url: Target URL (e.g., http://localhost:8000/mcp)
            envelope: Protocol envelope
            payload: Message payload
            request_id: Optional request ID (generated if not provided)

        Returns:
            Response payload dictionary

        Raises:
            LeagueError: If request fails or returns an error
        """
        from .protocol import generate_message_id

        if request_id is None:
            request_id = generate_message_id()

        # Construct JSON-RPC request
        request = JSONRPCRequest(
            jsonrpc=JSONRPC_VERSION,
            method="league.handle",
            params={
                "envelope": envelope.to_dict(),
                "payload": payload
            },
            id=request_id
        )

        # Parse URL
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 80

        try:
            # Create connection
            conn = http.client.HTTPConnection(host, port, timeout=self.timeout)

            # Send request
            body = json.dumps(request.to_dict()).encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'Content-Length': str(len(body))
            }
            conn.request('POST', parsed.path or '/mcp', body, headers)

            # Get response
            response = conn.getresponse()
            response_body = response.read().decode('utf-8')

            # Parse response
            response_data = json.loads(response_body)

            # Check for JSON-RPC error
            if 'error' in response_data:
                error = response_data['error']
                raise ProtocolError(
                    ErrorCode(error.get('code', ErrorCode.INTERNAL_ERROR)),
                    error.get('message', 'Unknown error'),
                    error.get('data', {})
                )

            # Extract result
            if 'result' not in response_data:
                raise ProtocolError(
                    ErrorCode.INVALID_JSON_RPC,
                    "Response missing 'result' field"
                )

            return response_data['result']

        except http.client.HTTPException as e:
            raise ProtocolError(
                ErrorCode.INTERNAL_ERROR,
                f"HTTP error: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise ProtocolError(
                ErrorCode.INVALID_JSON_RPC,
                f"Invalid JSON response: {str(e)}"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def send_request_no_response(
        self,
        url: str,
        envelope: Envelope,
        payload: Dict[str, Any]
    ) -> None:
        """Send a request without waiting for meaningful response.

        This is used for fire-and-forget messages where we only care
        about delivery, not the response content.

        Args:
            url: Target URL
            envelope: Protocol envelope
            payload: Message payload
        """
        try:
            self.send_request(url, envelope, payload)
        except Exception as e:
            logger.warning(f"Fire-and-forget request failed: {e}")
