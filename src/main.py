#!/usr/bin/env python3
# src/main.py
"""
Hermes Toolkit - Main Entry Point

A visual management tool for Hermes AI Assistant.
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.app import HermesApp
from src.utils.logger import setup_logger


def main():
    """Main entry point."""
    # Setup logging
    log_dir = Path.home() / '.hermes' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(
        name='hermes-toolkit',
        level='INFO',
        log_file=str(log_dir / 'toolkit.log'),
    )

    logger.info("Starting Hermes Toolkit v0.1.0")

    try:
        # Create and run app
        app = HermesApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Hermes Toolkit interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running Hermes Toolkit: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Hermes Toolkit exited")


if __name__ == '__main__':
    main()
