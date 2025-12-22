"""Logging utilities for the Agent League System.

This module provides audit logging functionality for recording all
protocol messages in an append-only format.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import uuid

from .protocol import Envelope, JSONRPCRequest, JSONRPCResponse


class AuditLogger:
    """Append-only audit logger for protocol messages.

    Logs all JSON-RPC messages in JSON Lines format for replay and verification.
    """

    def __init__(self, log_path: str):
        """Initialize the audit logger.

        Args:
            log_path: Path to audit log file
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._file = None

    def open(self):
        """Open the audit log file for appending."""
        with self._lock:
            if self._file is None:
                self._file = open(self.log_path, 'a', encoding='utf-8')

    def close(self):
        """Close the audit log file."""
        with self._lock:
            if self._file is not None:
                self._file.close()
                self._file = None

    def log_request(
        self,
        request: JSONRPCRequest,
        source: str,
        destination: str
    ) -> None:
        """Log a JSON-RPC request.

        Args:
            request: The JSON-RPC request
            source: Source agent identity
            destination: Destination agent identity
        """
        envelope = request.params.get('envelope', {})
        log_entry = {
            'log_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'direction': 'request',
            'source': source,
            'destination': destination,
            'conversation_id': envelope.get('conversation_id', 'unknown'),
            'message': request.to_dict()
        }
        self._write_entry(log_entry)

    def log_response(
        self,
        response: JSONRPCResponse,
        source: str,
        destination: str,
        conversation_id: Optional[str] = None
    ) -> None:
        """Log a JSON-RPC response.

        Args:
            response: The JSON-RPC response
            source: Source agent identity
            destination: Destination agent identity
            conversation_id: Optional conversation ID
        """
        # Try to extract conversation_id from response
        if conversation_id is None and response.result:
            envelope = response.result.get('envelope', {})
            conversation_id = envelope.get('conversation_id', 'unknown')

        log_entry = {
            'log_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'direction': 'response',
            'source': source,
            'destination': destination,
            'conversation_id': conversation_id or 'unknown',
            'message': response.to_dict()
        }
        self._write_entry(log_entry)

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """Write a log entry to the audit log.

        Args:
            entry: Log entry dictionary
        """
        with self._lock:
            if self._file is None:
                self.open()
            line = json.dumps(entry, separators=(',', ':'))
            self._file.write(line + '\n')
            self._file.flush()

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def setup_application_logging(
    log_path: str,
    log_level: str = 'INFO',
    logger_name: Optional[str] = None
) -> logging.Logger:
    """Set up application logging.

    Args:
        log_path: Path to application log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Optional logger name (default: root logger)

    Returns:
        Configured logger instance
    """
    # Create log directory
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    # Get logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # File handler with structured format
    file_handler = logging.FileHandler(log_path)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger
