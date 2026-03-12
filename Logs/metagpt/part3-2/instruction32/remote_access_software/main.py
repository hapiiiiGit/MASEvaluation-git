import sys
import argparse
import logging
import os
import json

# Server and client imports
from server.app import RemoteAccessServer
from client.ui import RemoteAccessClientUI

def load_config(config_path: str) -> dict:
    """Load configuration from a JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)

def setup_logging(log_level: str = "INFO"):
    """Setup logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

def main():
    parser = argparse.ArgumentParser(
        description="Remote Access Software - Secure cross-platform remote desktop and file transfer."
    )
    parser.add_argument(
        "--mode", choices=["server", "client"], required=True,
        help="Run as server or client."
    )
    parser.add_argument(
        "--config", type=str, default="config.json",
        help="Path to configuration file."
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."
    )
    args = parser.parse_args()

    setup_logging(args.log_level)
    logger = logging.getLogger("main")

    try:
        config = load_config(args.config)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    if args.mode == "server":
        logger.info("Starting Remote Access Server...")
        server = RemoteAccessServer(config)
        try:
            server.start()
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
            server.stop()
    elif args.mode == "client":
        logger.info("Starting Remote Access Client UI...")
        client_ui = RemoteAccessClientUI(config)
        try:
            client_ui.run()
        except KeyboardInterrupt:
            logger.info("Exiting client UI...")
    else:
        logger.error(f"Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()