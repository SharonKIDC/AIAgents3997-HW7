"""CLI argument parsing helpers.

This module provides common CLI argument patterns used across
Player, Referee, and League Manager entry points.
"""

import argparse
import sys
import time


def add_host_port_args(parser: argparse.ArgumentParser, default_port: int):
    """Add host and port arguments to parser.

    Args:
        parser: ArgumentParser instance
        default_port: Default port number
    """
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"Port to bind to (default: {default_port})"
    )


def add_league_manager_url_arg(parser: argparse.ArgumentParser):
    """Add league manager URL argument to parser.

    Args:
        parser: ArgumentParser instance
    """
    parser.add_argument(
        "--league-manager-url",
        default="http://localhost:8000/mcp",
        help="League Manager URL (default: http://localhost:8000/mcp)"
    )


def add_log_level_arg(parser: argparse.ArgumentParser):
    """Add log level argument to parser.

    Args:
        parser: ArgumentParser instance
    """
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )


def create_agent_parser(description: str, agent_type: str) -> argparse.ArgumentParser:
    """Create argument parser for agent (player/referee).

    Args:
        description: Parser description
        agent_type: Type of agent ("player" or "referee")

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        f"{agent_type}_id",
        help=f"Unique {agent_type} identifier"
    )
    return parser


def run_server_loop(logger, message: str, cleanup_callback=None):
    """Run server main loop with standard shutdown logic.

    Args:
        logger: Logger instance
        message: Message to log when running
        cleanup_callback: Optional callback function to run on shutdown
    """
    try:
        logger.info("%s. Press Ctrl+C to stop.", message)

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if cleanup_callback:
            cleanup_callback()


def run_agent_server(server, logger, error_message: str):
    """Run agent server with standard startup/shutdown logic.

    Args:
        server: Server instance with start(), register(), send_ready(), stop() methods
        logger: Logger instance
        error_message: Error message prefix for log messages
    """
    server.start()

    # Register with League Manager
    if not server.register():
        logger.error("%s: Failed to register with League Manager", error_message)
        sys.exit(1)

    # Send ready signal
    if not server.send_ready():
        logger.error("%s: Failed to send ready signal to League Manager", error_message)
        sys.exit(1)

    run_server_loop(
        logger,
        f"{error_message} is running and ACTIVE",
        server.stop
    )
