"""Referee entry point.

This module provides the command-line interface for starting a referee.
"""

from ..common.cli_helpers import (
    add_host_port_args,
    add_league_manager_url_arg,
    add_log_level_arg,
    create_agent_parser,
    run_agent_server,
)
from ..common.logging_utils import setup_application_logging
from .server import RefereeServer


def main():
    """Main entry point for Referee."""
    parser = create_agent_parser("Agent League System - Referee", "referee")
    add_host_port_args(parser, default_port=8001)
    add_league_manager_url_arg(parser)
    add_log_level_arg(parser)

    args = parser.parse_args()

    # Setup logging
    logger = setup_application_logging(
        f"./logs/referee_{args.referee_id}.log", args.log_level, f"referee.{args.referee_id}"
    )

    # Create server
    server = RefereeServer(args.referee_id, args.host, args.port, args.league_manager_url)

    # Run server with standard startup/shutdown logic
    run_agent_server(server, logger, "Referee")


if __name__ == "__main__":
    main()
