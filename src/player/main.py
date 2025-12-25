"""Player entry point.

This module provides the command-line interface for starting a player.
"""

import argparse
import sys
import time

from ..common.logging_utils import setup_application_logging
from .server import PlayerServer


def main():
    """Main entry point for Player."""
    parser = argparse.ArgumentParser(description="Agent League System - Player")
    parser.add_argument(
        "player_id",
        help="Unique player identifier"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9001,
        help="Port to bind to (default: 9001)"
    )
    parser.add_argument(
        "--league-manager-url",
        default="http://localhost:8000/mcp",
        help="League Manager URL (default: http://localhost:8000/mcp)"
    )
    parser.add_argument(
        "--strategy",
        choices=["smart", "random"],
        default="smart",
        help="Strategy to use (default: smart)"
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
        f"./logs/player_{args.player_id}.log",
        args.log_level,
        f"player.{args.player_id}"
    )

    # Create and start server
    server = PlayerServer(
        args.player_id,
        args.host,
        args.port,
        args.league_manager_url,
        args.strategy
    )

    try:
        server.start()

        # Register with League Manager
        if not server.register():
            logger.error("Failed to register with League Manager")
            sys.exit(1)

        # Send ready signal (agent is initialized and ready for matches)
        if not server.send_ready():
            logger.error("Failed to send ready signal to League Manager")
            sys.exit(1)

        logger.info("Player is running and ACTIVE. Press Ctrl+C to stop.")

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
