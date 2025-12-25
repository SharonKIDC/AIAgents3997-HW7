"""League Manager entry point.

This module provides the command-line interface for starting the League Manager.
"""

import argparse
import sys
import time

from ..common.config import load_config
from ..common.logging_utils import AuditLogger, setup_application_logging
from ..common.persistence import LeagueDatabase
from .server import LeagueManagerServer


def main():
    """Main entry point for League Manager."""
    parser = argparse.ArgumentParser(description="Agent League System - League Manager")
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--config-dir",
        default="./config",
        help="Configuration directory (default: ./config)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config_dir)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
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
    server = LeagueManagerServer(
        args.host,
        args.port,
        config,
        database,
        audit_logger
    )

    try:
        server.start()
        logger.info("League Manager is running. Press Ctrl+C to stop.")

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        server.stop()
        audit_logger.close()
        database.close()


if __name__ == "__main__":
    main()
