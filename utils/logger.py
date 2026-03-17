"""
Logger Utility Module

Provides centralized logging configuration for the dashboard application.
Logs to both file (logs/dashboard.log) and console with appropriate formatting.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "dashboard",
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True
) -> logging.Logger:
    """
    Setup and configure a logger with file and console handlers.

    Args:
        name: Logger name (default: "dashboard")
        log_level: Logging level (default: logging.INFO)
        log_to_file: Enable file logging (default: True)
        log_to_console: Enable console logging (default: True)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger()
        >>> logger.info("Application started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create log file with date in filename
        log_filename = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"

        try:
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Fallback to console if file handler fails
            print(f"Warning: Could not create file handler: {e}", file=sys.stderr)

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "dashboard") -> logging.Logger:
    """
    Get an existing logger or create a new one if it doesn't exist.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # Setup logger if it has no handlers
    if not logger.handlers:
        return setup_logger(name)

    return logger


class LoggerContext:
    """
    Context manager for logging execution time of code blocks.

    Example:
        >>> with LoggerContext(logger, "data_loading"):
        ...     load_data()
    """

    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        duration_ms = duration.total_seconds() * 1000

        if exc_type is None:
            self.logger.info(f"Completed: {self.operation_name} (took {duration_ms:.2f}ms)")
        else:
            self.logger.error(
                f"Failed: {self.operation_name} after {duration_ms:.2f}ms",
                exc_info=(exc_type, exc_val, exc_tb)
            )
        return False


# Create default logger instance
default_logger = setup_logger()
