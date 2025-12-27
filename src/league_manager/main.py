"""League Manager entry point.

This module provides the command-line interface for starting the League Manager.
"""

import argparse
import sys

from ..common.cli_helpers import add_host_port_args, add_log_level_arg, run_server_loop
from ..common.config import load_config
from ..common.logging_utils import AuditLogger, setup_application_logging
from ..common.persistence import LeagueDatabase
from .server import LeagueManagerServer


def main():
    """Main entry point for League Manager."""
    parser = argparse.ArgumentParser(description="Agent League System - League Manager")
    add_host_port_args(parser, default_port=8000)
    parser.add_argument("--config-dir", default="./config", help="Configuration directory (default: ./config)")
    add_log_level_arg(parser)

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config_dir)
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Unexpected error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Setup logging
    log_level = args.log_level
    if config.logging:
        log_level = config.logging.log_level
        app_log_path = config.logging.application_log_path
        audit_log_path = config.logging.audit_log_path
    else:
        app_log_path = "./logs/league_manager.log"
        audit_log_path = "./logs/audit.jsonl"

    logger = setup_application_logging(app_log_path, log_level, "league_manager")
    audit_logger = AuditLogger(audit_log_path)
    audit_logger.open()

    # Initialize database
    db_path = config.database.path if config.database else "./data/league.db"
    database = LeagueDatabase(db_path)
    database.initialize_schema()

    # Create and start server
    server = LeagueManagerServer(args.host, args.port, config=config, database=database, audit_logger=audit_logger)

    # Start server
    server.start()

    # Define cleanup function
    def cleanup():
        """Clean up resources on shutdown."""
        server.stop()
        audit_logger.close()
        database.close()

    # Run server loop
    run_server_loop(logger, "League Manager is running", cleanup)


if __name__ == "__main__":
    main()
