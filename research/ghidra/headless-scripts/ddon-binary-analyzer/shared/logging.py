# Shared Logging Configuration
# Centralized logging setup for Ghidra headless analysis
# Provides custom console handlers for both function analyzer and symbol explorer
#
# @author Sehkah
# @category ddon-research

import logging


class GhidraConsoleHandler(logging.Handler):
    """Custom logging handler for Ghidra console output in headless mode.
    
    Provides simplified output formatting optimized for PyGhidra execution
    environment where standard console handlers may not work correctly.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the console.
        
        Args:
            record: LogRecord instance containing the log message and metadata
        """
        try:
            msg = self.format(record)
            print(msg)
        except Exception:
            self.handleError(record)


class LoggingConfig:
    """Centralized logging configuration for DDON Binary Analyzer.
    
    Provides standardized logger setup with appropriate formatting and
    handlers for both DEBUG and INFO level output in headless environments.
    """

    @staticmethod
    def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
        """Setup and return configured logger for PyGhidra headless mode

        Args:
            name: Logger name
            level: Logging level ("DEBUG" or "INFO")

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)

        # Set logging level
        if level.upper() == "DEBUG":
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        logger.propagate = False

        # Clear old handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add Ghidra console handler
        handler = GhidraConsoleHandler()

        # Use minimal formatting for INFO, full formatting for DEBUG
        if level.upper() == "INFO":
            formatter = logging.Formatter("%(message)s")
        else:
            formatter = logging.Formatter("%(levelname)s: %(message)s")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger
