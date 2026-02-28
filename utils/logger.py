"""
Logging module for Douban AI Spider project.
Provides centralized logging configuration and custom logger instances.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from utils.config import LOG_LEVEL, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT, LOGS_DIR


class SpiderLogger:
    """
    Custom logger class for the spider project.
    Provides consistent logging format across all modules.
    """

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger instance with the specified name.

        Args:
            name: Logger name (typically __name__ of the module)
            log_file: Optional custom log file path

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        # Create new logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

        # Avoid adding handlers multiple times
        if logger.handlers:
            return logger

        # Create formatters
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_path = log_file or LOG_FILE
        # Ensure log directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

        cls._loggers[name] = logger
        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger instance.

    Args:
        name: Logger name (typically use __name__)

    Returns:
        Configured logger instance

    Example:
        >>> from utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting spider...")
    """
    return SpiderLogger.get_logger(name)


# Module-level logger for direct imports
logger = get_logger(__name__)


if __name__ == "__main__":
    # Test the logger
    test_logger = get_logger("test")
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")

    print(f"\nLog file created at: {LOG_FILE}")
