# Logging Configuration - Centralized logging setup for Ghidra analysis
# Provides logging configuration and custom handlers for Ghidra console output

import logging


class GhidraConsoleHandler(logging.Handler):
    """Custom logging handler for Ghidra console output"""

    def emit(self, record):
        try:
            msg = self.format(record)
            print(msg)
        except Exception:
            self.handleError(record)


class LoggingConfig:
    """Centralized logging configuration for function analyzer"""

    @staticmethod
    def setup_logger(name: str = "function_decompilation_analyzer", level: str = "DEBUG") -> logging.Logger:
        """Setup and return configured logger
        
        Args:
            name: Logger name
            level: Logging level ("DEBUG" or "INFO")
        """
        logger = logging.getLogger(name)

        # Set logging level based on parameter
        if level.upper() == "INFO":
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

        logger.propagate = False

        # Clear old handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add Ghidra console handler
        handler = GhidraConsoleHandler()
        if level.upper() == "INFO":
            formatter = logging.Formatter("%(message)s")  # No prefixes for INFO level
        else:
            formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    @staticmethod
    def setup_info_logger(name: str = "function_decompilation_analyzer") -> logging.Logger:
        """Setup logger for INFO level output (minimal information)"""
        return LoggingConfig.setup_logger(name, "INFO")
