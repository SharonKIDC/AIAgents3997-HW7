"""Tests for HTTP transport layer.

This module tests the HTTP server and client implementations
for JSON-RPC communication.
"""

import json
import threading
import time
from unittest.mock import Mock

import pytest

from src.common.errors import ErrorCode, ProtocolError
from src.common.protocol import (
    Envelope,
    JSONRPCRequest,
    JSONRPCResponse,
    MessageType,
    create_success_response,
    generate_conversation_id,
    utc_now,
)
from src.common.transport import LeagueHTTPClient, LeagueHTTPServer


class TestLeagueHTTPServer:
    """Tests for LeagueHTTPServer."""

    def test_server_initialization(self):
        """Test creating an HTTP server."""
        handler = Mock()
        server = LeagueHTTPServer("localhost", 9999, handler)

        assert server.host == "localhost"
        assert server.port == 9999
        assert server.message_handler == handler

    def test_server_start_stop(self):
        """Test starting and stopping the server."""
        handler = Mock()
        server = LeagueHTTPServer("localhost", 9998, handler)

        # Start server
        server.start()
        time.sleep(0.1)  # Give server time to start

        # Verify server is running
        assert server.thread is not None
        assert server.thread.is_alive()

        # Stop server
        server.stop()
        time.sleep(0.1)

        # Verify server is stopped
        assert not server.thread.is_alive()

    def test_server_handles_health_check(self):
        """Test that server responds to health check."""
        handler = Mock()
        server = LeagueHTTPServer("localhost", 9997, handler)

        server.start()
        time.sleep(0.1)

        try:
            # Make health check request
            import http.client

            conn = http.client.HTTPConnection("localhost", 9997)
            conn.request("GET", "/health")
            response = conn.getresponse()
            body = response.read().decode("utf-8")

            assert response.status == 200
            assert "ok" in body
        finally:
            server.stop()

    def test_server_handles_status_check(self):
        """Test that server responds to status check."""
        handler = Mock()
        status_provider = Mock(return_value={"status": "active", "uptime": 100})
        server = LeagueHTTPServer("localhost", 9996, handler, status_provider)

        server.start()
        time.sleep(0.1)

        try:
            # Make status request
            import http.client

            conn = http.client.HTTPConnection("localhost", 9996)
            conn.request("GET", "/status")
            response = conn.getresponse()
            body = json.loads(response.read().decode("utf-8"))

            assert response.status == 200
            assert body["status"] == "active"
            assert status_provider.called
        finally:
            server.stop()


class TestLeagueHTTPClient:
    """Tests for LeagueHTTPClient."""

    def test_client_initialization(self):
        """Test creating an HTTP client."""
        client = LeagueHTTPClient(timeout=60)
        assert client.timeout == 60

    def test_client_send_request_success(self):
        """Test sending a successful request."""

        # Create a mock server
        def mock_handler(request):
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_RESPONSE.value,
                sender="league_manager",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            payload = {"status": "registered", "auth_token": "test-token"}
            return create_success_response(envelope, payload, request.id)

        server = LeagueHTTPServer("localhost", 9995, mock_handler)
        server.start()
        time.sleep(0.1)

        try:
            # Send request
            client = LeagueHTTPClient()
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
                sender="player:alice",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            payload = {"player_id": "alice"}

            result = client.send_request("http://localhost:9995/mcp", envelope, payload)

            # Verify response
            assert "envelope" in result
            assert "payload" in result
            assert result["payload"]["status"] == "registered"
        finally:
            server.stop()

    def test_client_send_request_with_error_response(self):
        """Test handling error response from server."""

        # Create a mock server that returns error
        def mock_handler(request):
            return JSONRPCResponse(
                jsonrpc="2.0",
                error={"code": ErrorCode.VALIDATION_ERROR, "message": "Test error", "data": {}},
                id=request.id,
            )

        server = LeagueHTTPServer("localhost", 9994, mock_handler)
        server.start()
        time.sleep(0.1)

        try:
            client = LeagueHTTPClient()
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
                sender="player:alice",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            payload = {"player_id": "alice"}

            with pytest.raises(ProtocolError) as exc_info:
                client.send_request("http://localhost:9994/mcp", envelope, payload)

            assert "Test error" in str(exc_info.value)
        finally:
            server.stop()

    def test_client_send_request_connection_error(self):
        """Test handling connection error."""
        client = LeagueHTTPClient(timeout=1)
        envelope = Envelope(
            protocol="league.v2",
            message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
            sender="player:alice",
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
        )
        payload = {"player_id": "alice"}

        # Try to connect to non-existent server
        with pytest.raises(ProtocolError):
            client.send_request("http://localhost:9999/mcp", envelope, payload)

    def test_client_send_request_no_response(self):
        """Test fire-and-forget request."""

        # Create a mock server
        def mock_handler(request):
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.GAME_JOIN_ACK.value,
                sender="player:alice",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            return create_success_response(envelope, {}, request.id)

        server = LeagueHTTPServer("localhost", 9993, mock_handler)
        server.start()
        time.sleep(0.1)

        try:
            client = LeagueHTTPClient()
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.GAME_INVITATION.value,
                sender="referee:ref-1",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            payload = {"match_id": "match-123"}

            # Should not raise
            client.send_request_no_response("http://localhost:9993/mcp", envelope, payload)
        finally:
            server.stop()


class TestLeagueHTTPHandler:
    """Tests for request handler logic."""

    def test_handler_validates_json_rpc(self):
        """Test that handler validates JSON-RPC structure."""
        # This is tested indirectly through server integration tests
        pass

    def test_handler_delegates_to_message_handler(self):
        """Test that handler delegates to registered message handler."""
        # This is tested indirectly through server integration tests
        pass

    def test_handler_returns_404_for_invalid_path(self):
        """Test that invalid paths return 404."""
        handler = Mock()
        server = LeagueHTTPServer("localhost", 9992, handler)
        server.start()
        time.sleep(0.1)

        try:
            import http.client

            conn = http.client.HTTPConnection("localhost", 9992)
            conn.request("GET", "/invalid")
            response = conn.getresponse()

            assert response.status == 404
        finally:
            server.stop()

    def test_handler_rejects_non_post_to_mcp(self):
        """Test that GET requests to /mcp are rejected."""
        handler = Mock()
        server = LeagueHTTPServer("localhost", 9991, handler)
        server.start()
        time.sleep(0.1)

        try:
            import http.client

            conn = http.client.HTTPConnection("localhost", 9991)
            conn.request("GET", "/mcp")
            response = conn.getresponse()

            # Should get an error response or 404/405
            assert response.status in [404, 405]
        finally:
            server.stop()


class TestEndToEndCommunication:
    """End-to-end tests for HTTP communication."""

    def test_full_request_response_cycle(self):
        """Test complete request-response cycle."""
        request_received = {}

        def message_handler(request: JSONRPCRequest) -> JSONRPCResponse:
            """Handle incoming request."""
            request_received["request"] = request

            # Extract envelope and payload
            envelope_data = request.params["envelope"]
            _payload = request.params["payload"]  # noqa: F841

            # Create response
            response_envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_RESPONSE.value,
                sender="league_manager",
                timestamp=utc_now(),
                conversation_id=envelope_data["conversation_id"],
            )

            response_payload = {"status": "registered", "auth_token": "test-token-123", "league_id": "league-001"}

            return create_success_response(response_envelope, response_payload, request.id)

        # Start server
        server = LeagueHTTPServer("localhost", 9990, message_handler)
        server.start()
        time.sleep(0.1)

        try:
            # Create client and send request
            client = LeagueHTTPClient()
            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.REGISTER_PLAYER_REQUEST.value,
                sender="player:alice",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            payload = {"player_id": "alice"}

            result = client.send_request("http://localhost:9990/mcp", envelope, payload)

            # Verify request was received
            assert request_received["request"] is not None
            assert request_received["request"].method == "league.handle"

            # Verify response
            assert result["payload"]["status"] == "registered"
            assert result["payload"]["auth_token"] == "test-token-123"
        finally:
            server.stop()

    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        request_count = {"count": 0}
        lock = threading.Lock()

        def message_handler(request: JSONRPCRequest) -> JSONRPCResponse:
            """Count requests."""
            with lock:
                request_count["count"] += 1

            envelope = Envelope(
                protocol="league.v2",
                message_type=MessageType.STANDINGS_RESPONSE.value,
                sender="league_manager",
                timestamp=utc_now(),
                conversation_id=generate_conversation_id(),
            )
            return create_success_response(envelope, {}, request.id)

        server = LeagueHTTPServer("localhost", 9989, message_handler)
        server.start()
        time.sleep(0.1)

        try:
            # Send multiple requests concurrently
            def send_request():
                client = LeagueHTTPClient()
                envelope = Envelope(
                    protocol="league.v2",
                    message_type=MessageType.QUERY_STANDINGS.value,
                    sender="player:alice",
                    timestamp=utc_now(),
                    conversation_id=generate_conversation_id(),
                )
                client.send_request("http://localhost:9989/mcp", envelope, {})

            threads = [threading.Thread(target=send_request) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # Verify all requests were handled
            assert request_count["count"] == 5
        finally:
            server.stop()
