# Logging configuration for symbol exploration
#
# This module provides centralized logging configuration for headless
# PyGhidra execution with custom console handling.
#
# @author Sehkah 
# @category ddon-research

import logging

from .config import ExplorerConfig


class HeadlessConsoleHandler(logging.Handler):
    """Custom logging handler for PyGhidra headless console output"""

    def __init__(self):
        super(HeadlessConsoleHandler, self).__init__()

    def emit(self, record):
        try:
            msg = self.format(record)
            print(msg)
        except Exception:
            self.handleError(record)


class LoggingConfig:
    """Centralized logging configuration for headless mode"""

    @staticmethod
    def setup_logger(name: str = "dwarf_symbol_explorer") -> logging.Logger:
        """Setup and return configured logger for PyGhidra headless mode"""
        logger = logging.getLogger(name)

        # Set log level based on configuration
        log_level = ExplorerConfig.get_log_level()
        if log_level == 'DEBUG':
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        logger.propagate = False

        # Clear old handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add headless console handler
        handler = HeadlessConsoleHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger
