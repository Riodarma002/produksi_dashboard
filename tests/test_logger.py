"""
Unit tests for logger utility
"""
import pytest
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger, get_logger, LoggerContext


class TestSetupLogger:
    """Test cases for setup_logger function"""

    def test_setup_logger_default(self):
        """Test logger creation with default parameters"""
        logger = setup_logger("test_logger")

        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logger_custom_level(self):
        """Test logger creation with custom log level"""
        logger = setup_logger("test_logger_debug", log_level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_setup_logger_file_handler(self):
        """Test that file handler is created"""
        logger = setup_logger("test_file_logger")

        # Check if file handler exists
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

    def test_logger_output(self, caplog):
        """Test that logger actually logs messages"""
        logger = setup_logger("test_output")

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert "Test message" in caplog.text
        assert "test_output" in caplog.text


class TestGetLogger:
    """Test cases for get_logger function"""

    def test_get_logger_new(self):
        """Test getting a new logger"""
        logger = get_logger("new_test_logger")

        assert logger.name == "new_test_logger"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_existing(self):
        """Test getting an existing logger returns same instance"""
        logger1 = get_logger("existing_logger")
        logger2 = get_logger("existing_logger")

        assert logger1 is logger2


class TestLoggerContext:
    """Test cases for LoggerContext context manager"""

    def test_logger_context_success(self, caplog):
        """Test LoggerContext on successful execution"""
        logger = setup_logger("test_context")

        with caplog.at_level(logging.INFO):
            with LoggerContext(logger, "test_operation"):
                pass

        assert "Starting: test_operation" in caplog.text
        assert "Completed: test_operation" in caplog.text

    def test_logger_context_exception(self, caplog):
        """Test LoggerContext on exception"""
        logger = setup_logger("test_context_error")

        with caplog.at_level(logging.INFO):  # Capture INFO level to see both messages
            with pytest.raises(ValueError):
                with LoggerContext(logger, "test_operation_fail"):
                    raise ValueError("Test error")

        assert "Starting: test_operation_fail" in caplog.text
        assert "Failed: test_operation_fail" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
