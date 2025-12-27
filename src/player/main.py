"""Player entry point.

This module provides the command-line interface for starting a player.
"""

from ..common.cli_helpers import (
    add_host_port_args,
    add_league_manager_url_arg,
    add_log_level_arg,
    create_agent_parser,
    run_agent_server,
)
from ..common.logging_utils import setup_application_logging
from .server import PlayerServer


def main():
    """Main entry point for Player."""
    parser = create_agent_parser("Agent League System - Player", "player")
    add_host_port_args(parser, default_port=9001)
    add_league_manager_url_arg(parser)
    parser.add_argument(
        "--strategy",
        choices=["smart", "random"],
        default="smart",
        help="Strategy to use (default: smart)"
    )
    add_log_level_arg(parser)

    args = parser.parse_args()

    # Setup logging
    logger = setup_application_logging(
        f"./logs/player_{args.player_id}.log",
        args.log_level,
        f"player.{args.player_id}"
    )

    # Create server
    server = PlayerServer(
        args.player_id,
        args.host,
        args.port,
        league_manager_url=args.league_manager_url,
        strategy_type=args.strategy
    )

    # Run server with standard startup/shutdown logic
    run_agent_server(server, logger, "Player")


if __name__ == "__main__":
    main()
