"""Referee entry point.

This module provides the command-line interface for starting a referee.
"""

import argparse
import sys
import time

from ..common.logging_utils import setup_application_logging
from .server import RefereeServer


def main():
    """Main entry point for Referee."""
    parser = argparse.ArgumentParser(description="Agent League System - Referee")
    parser.add_argument(
        "referee_id",
        help="Unique referee identifier"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind to (default: 8001)"
    )
    parser.add_argument(
        "--league-manager-url",
        default="http://localhost:8000/mcp",
        help="League Manager URL (default: http://localhost:8000/mcp)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_application_logging(
        f"./logs/referee_{args.referee_id}.log",
        args.log_level,
        f"referee.{args.referee_id}"
    )

    # Create and start server
    server = RefereeServer(
        args.referee_id,
        args.host,
        args.port,
        args.league_manager_url
    )

    try:
        server.start()

        # Register with League Manager
        if not server.register():
            logger.error("Failed to register with League Manager")
            sys.exit(1)

        logger.info("Referee is running. Press Ctrl+C to stop.")

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
