"""Tests for protocol validation and envelope handling.

This module tests the protocol layer including envelope validation,
message types, and JSON-RPC structures.
"""

import uuid

import pytest

from src.common.errors import ErrorCode, ProtocolError, ValidationError
from src.common.protocol import (
    JSONRPC_VERSION,
    MCP_METHOD,
    PROTOCOL_VERSION,
    Envelope,
    JSONRPCRequest,
    JSONRPCResponse,
    MessageType,
    create_error_response,
    create_success_response,
    generate_conversation_id,
    generate_message_id,
    utc_now,
    validate_sender_format,
    validate_timestamp,
    validate_uuid,
)


class TestEnvelope:
    """Tests for Envelope class."""

    def test_envelope_creation_with_required_fields(self, sample_envelope_data):
        """Test creating an envelope with all required fields."""
        envelope = Envelope.from_dict(sample_envelope_data)

        assert envelope.protocol == 'league.v2'
        assert envelope.message_type == 'REGISTER_PLAYER_REQUEST'
        assert envelope.sender == 'player:alice'
        assert envelope.timestamp is not None
        assert envelope.conversation_id is not None

    def test_envelope_to_dict(self, sample_envelope_data):
        """Test converting envelope to dictionary."""
        envelope = Envelope.from_dict(sample_envelope_data)
        result = envelope.to_dict()

        assert result['protocol'] == 'league.v2'
        assert result['message_type'] == 'REGISTER_PLAYER_REQUEST'
        assert result['sender'] == 'player:alice'
        assert 'timestamp' in result
        assert 'conversation_id' in result

    def test_envelope_excludes_none_values(self):
        """Test that envelope dictionary excludes None values."""
        envelope = Envelope(
            protocol='league.v2',
            message_type='REGISTER_PLAYER_REQUEST',
            sender='player:alice',
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            auth_token=None,
            league_id=None
        )

        result = envelope.to_dict()
        assert 'auth_token' not in result
        assert 'league_id' not in result

    def test_envelope_includes_optional_fields(self):
        """Test envelope with optional fields."""
        envelope = Envelope(
            protocol='league.v2',
            message_type='MATCH_ASSIGNMENT',
            sender='league_manager',
            timestamp=utc_now(),
            conversation_id=generate_conversation_id(),
            auth_token='test-token',
            league_id='league-123',
            match_id='match-456',
            game_type='tic_tac_toe'
        )

        result = envelope.to_dict()
        assert result['auth_token'] == 'test-token'
        assert result['league_id'] == 'league-123'
        assert result['match_id'] == 'match-456'
        assert result['game_type'] == 'tic_tac_toe'

    def test_envelope_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        incomplete_data = {
            'protocol': 'league.v2',
            'message_type': 'REGISTER_PLAYER_REQUEST',
            # Missing sender, timestamp, conversation_id
        }

        with pytest.raises(ValidationError) as exc_info:
            Envelope.from_dict(incomplete_data)

        assert 'sender' in str(exc_info.value) or 'timestamp' in str(exc_info.value)

    def test_envelope_invalid_protocol_version(self, sample_envelope_data):
        """Test that invalid protocol version raises error."""
        sample_envelope_data['protocol'] = 'league.v1'

        with pytest.raises(ProtocolError) as exc_info:
            Envelope.from_dict(sample_envelope_data)

        assert exc_info.value.code == ErrorCode.INVALID_PROTOCOL_VERSION

    def test_envelope_invalid_message_type(self, sample_envelope_data):
        """Test that invalid message type raises error."""
        sample_envelope_data['message_type'] = 'INVALID_MESSAGE'

        with pytest.raises(ProtocolError) as exc_info:
            Envelope.from_dict(sample_envelope_data)

        assert exc_info.value.code == ErrorCode.INVALID_MESSAGE_TYPE

    def test_envelope_invalid_sender_format(self, sample_envelope_data):
        """Test that invalid sender format raises error."""
        sample_envelope_data['sender'] = 'invalid-sender'

        with pytest.raises(ValidationError):
            Envelope.from_dict(sample_envelope_data)


class TestMessageType:
    """Tests for MessageType enum."""

    def test_all_message_types_are_strings(self):
        """Test that all message types are valid strings."""
        for msg_type in MessageType:
            assert isinstance(msg_type.value, str)
            assert msg_type.value == msg_type.value.upper()

    def test_message_type_validation(self):
        """Test validating message types."""
        # Valid
        assert MessageType.REGISTER_PLAYER_REQUEST.value == 'REGISTER_PLAYER_REQUEST'
        assert MessageType.GAME_INVITATION.value == 'GAME_INVITATION'

        # Invalid
        with pytest.raises(ValueError):
            MessageType('NOT_A_REAL_MESSAGE')


class TestValidationFunctions:
    """Tests for validation helper functions."""

    def test_validate_sender_format_league_manager(self):
        """Test validating league_manager sender."""
        # Should not raise
        validate_sender_format('league_manager')

    def test_validate_sender_format_admin(self):
        """Test validating admin sender."""
        # Should not raise
        validate_sender_format('admin')

    def test_validate_sender_format_referee(self):
        """Test validating referee sender format."""
        validate_sender_format('referee:ref-001')
        validate_sender_format('referee:my_referee')
        validate_sender_format('referee:test-ref-123')

    def test_validate_sender_format_player(self):
        """Test validating player sender format."""
        validate_sender_format('player:alice')
        validate_sender_format('player:player_123')
        validate_sender_format('player:test-player')

    def test_validate_sender_format_invalid(self):
        """Test that invalid sender formats raise error."""
        invalid_senders = [
            'player',
            'referee',
            'player:',
            'referee:',
            'unknown:test',
            'player alice',
            'referee@test'
        ]

        for sender in invalid_senders:
            with pytest.raises(ValidationError):
                validate_sender_format(sender)

    def test_validate_timestamp_valid_utc(self):
        """Test validating valid UTC timestamps."""
        valid_timestamps = [
            '2025-12-21T10:30:00Z',
            '2025-12-21T10:30:00+00:00',
            '2025-01-01T00:00:00Z'
        ]

        for ts in valid_timestamps:
            validate_timestamp(ts)

    def test_validate_timestamp_invalid(self):
        """Test that invalid timestamps raise error."""
        invalid_timestamps = [
            '2025-12-21',
            'not-a-timestamp',
            '2025-12-21T10:30:00',  # Missing timezone
            '2025-12-21T10:30:00-05:00'  # Not UTC
        ]

        for ts in invalid_timestamps:
            with pytest.raises(ValidationError):
                validate_timestamp(ts)

    def test_validate_uuid_valid(self):
        """Test validating valid UUIDs."""
        valid_uuid = str(uuid.uuid4())
        validate_uuid(valid_uuid, 'test_field')

    def test_validate_uuid_invalid(self):
        """Test that invalid UUIDs raise error."""
        invalid_uuids = [
            'not-a-uuid',
            '12345',
            'abc-def-ghi'
        ]

        for invalid in invalid_uuids:
            with pytest.raises(ValidationError):
                validate_uuid(invalid, 'test_field')


class TestJSONRPCRequest:
    """Tests for JSONRPCRequest class."""

    def test_jsonrpc_request_from_dict(self, sample_jsonrpc_request):
        """Test creating JSON-RPC request from dictionary."""
        request = JSONRPCRequest.from_dict(sample_jsonrpc_request)

        assert request.jsonrpc == '2.0'
        assert request.method == 'league.handle'
        assert 'envelope' in request.params
        assert 'payload' in request.params

    def test_jsonrpc_request_to_dict(self, sample_jsonrpc_request):
        """Test converting JSON-RPC request to dictionary."""
        request = JSONRPCRequest.from_dict(sample_jsonrpc_request)
        result = request.to_dict()

        assert result['jsonrpc'] == '2.0'
        assert result['method'] == 'league.handle'
        assert 'params' in result

    def test_jsonrpc_request_invalid_version(self, sample_jsonrpc_request):
        """Test that invalid JSON-RPC version raises error."""
        sample_jsonrpc_request['jsonrpc'] = '1.0'

        with pytest.raises(ProtocolError) as exc_info:
            JSONRPCRequest.from_dict(sample_jsonrpc_request)

        assert exc_info.value.code == ErrorCode.INVALID_JSON_RPC

    def test_jsonrpc_request_invalid_method(self, sample_jsonrpc_request):
        """Test that invalid method raises error."""
        sample_jsonrpc_request['method'] = 'wrong.method'

        with pytest.raises(ProtocolError) as exc_info:
            JSONRPCRequest.from_dict(sample_jsonrpc_request)

        assert exc_info.value.code == ErrorCode.INVALID_METHOD

    def test_jsonrpc_request_missing_params(self, sample_jsonrpc_request):
        """Test that missing params raises error."""
        del sample_jsonrpc_request['params']

        with pytest.raises(ProtocolError) as exc_info:
            JSONRPCRequest.from_dict(sample_jsonrpc_request)

        assert exc_info.value.code == ErrorCode.MISSING_REQUIRED_FIELD

    def test_jsonrpc_request_missing_envelope(self, sample_jsonrpc_request):
        """Test that missing envelope in params raises error."""
        del sample_jsonrpc_request['params']['envelope']

        with pytest.raises(ProtocolError) as exc_info:
            JSONRPCRequest.from_dict(sample_jsonrpc_request)

        assert exc_info.value.code == ErrorCode.MISSING_ENVELOPE


class TestJSONRPCResponse:
    """Tests for JSONRPCResponse class."""

    def test_jsonrpc_response_success(self):
        """Test creating success response."""
        response = JSONRPCResponse(
            jsonrpc='2.0',
            result={'status': 'ok'},
            id='test-id'
        )

        result = response.to_dict()
        assert result['jsonrpc'] == '2.0'
        assert result['result'] == {'status': 'ok'}
        assert result['id'] == 'test-id'
        assert 'error' not in result

    def test_jsonrpc_response_error(self):
        """Test creating error response."""
        response = JSONRPCResponse(
            jsonrpc='2.0',
            error={'code': 4000, 'message': 'Test error'},
            id='test-id'
        )

        result = response.to_dict()
        assert result['jsonrpc'] == '2.0'
        assert result['error'] == {'code': 4000, 'message': 'Test error'}
        assert result['id'] == 'test-id'
        assert 'result' not in result


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_create_success_response(self, sample_envelope_data):
        """Test creating success response."""
        envelope = Envelope.from_dict(sample_envelope_data)
        payload = {'status': 'registered'}

        response = create_success_response(envelope, payload, 'req-123')

        result = response.to_dict()
        assert result['jsonrpc'] == '2.0'
        assert 'result' in result
        assert result['result']['envelope']['protocol'] == 'league.v2'
        assert result['result']['payload'] == payload
        assert result['id'] == 'req-123'

    def test_create_error_response(self):
        """Test creating error response."""
        response = create_error_response(
            ErrorCode.VALIDATION_ERROR,
            'Test validation error',
            {'field': 'test'},
            'req-123'
        )

        result = response.to_dict()
        assert result['jsonrpc'] == '2.0'
        assert 'error' in result
        assert result['error']['code'] == ErrorCode.VALIDATION_ERROR
        assert result['error']['message'] == 'Test validation error'
        assert result['id'] == 'req-123'

    def test_create_error_response_no_request_id(self):
        """Test creating error response without request ID."""
        response = create_error_response(
            ErrorCode.INVALID_JSON_RPC,
            'Invalid JSON',
            None,
            None
        )

        result = response.to_dict()
        assert result['id'] is None

    def test_generate_conversation_id(self):
        """Test generating conversation IDs."""
        conv_id = generate_conversation_id()

        assert isinstance(conv_id, str)
        # Should be valid UUID
        uuid.UUID(conv_id)

    def test_generate_message_id(self):
        """Test generating message IDs."""
        msg_id = generate_message_id()

        assert isinstance(msg_id, str)
        # Should be valid UUID
        uuid.UUID(msg_id)

    def test_utc_now(self):
        """Test UTC timestamp generation."""
        timestamp = utc_now()

        assert isinstance(timestamp, str)
        assert timestamp.endswith('Z')
        # Should be valid timestamp
        validate_timestamp(timestamp)

    def test_generated_ids_are_unique(self):
        """Test that generated IDs are unique."""
        ids = [generate_conversation_id() for _ in range(100)]
        assert len(ids) == len(set(ids))


class TestConstants:
    """Tests for protocol constants."""

    def test_protocol_version(self):
        """Test protocol version constant."""
        assert PROTOCOL_VERSION == 'league.v2'

    def test_jsonrpc_version(self):
        """Test JSON-RPC version constant."""
        assert JSONRPC_VERSION == '2.0'

    def test_mcp_method(self):
        """Test MCP method constant."""
        assert MCP_METHOD == 'league.handle'
