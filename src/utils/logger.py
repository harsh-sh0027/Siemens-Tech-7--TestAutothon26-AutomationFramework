"""Structured logging with correlation ID (test name + worker ID)."""

import logging
import os
from datetime import datetime
from typing import Optional
import threading
import re

from src.utils.config import ConfigLoader


class StructuredLogger:
    """
    Structured logging with correlation ID and PII redaction.
    
    Every log line includes:
    - Timestamp
    - Level (DEBUG, INFO, WARN, ERROR)
    - Correlation ID (test name + thread/worker ID)
    - Class name
    - Message (with credentials masked)
    
    Thread-safe: uses threading.local() for correlation ID.
    """
    
    # Thread-local storage for correlation ID
    _correlation_id = threading.local()
    
    # Patterns to redact from log messages (PII, credentials, tokens)
    REDACT_PATTERNS = [
        (r'(password|passwd)["\']?\s*[=:]\s*["\']?[^\s"\'\n]+["\']?', r'\1: [REDACTED]'),
        (r'(otp|otpcode|otp_code)["\']?\s*[=:]\s*["\']?[^\s"\'\n]+["\']?', r'\1: [REDACTED]'),
        (r'(mobile|phone|number)["\']?\s*[=:]\s*["\']?\d+["\']?', r'\1: [REDACTED]'),
        (r'(token|api_key|apikey)["\']?\s*[=:]\s*["\']?[^\s"\'\n]+["\']?', r'\1: [REDACTED]'),
        (r'(auth|authorization)["\']?\s*[=:]\s*Bearer\s+[^\s"\'\n]+', r'\1: [REDACTED]'),
        (r'(pin|secret)["\']?\s*[=:]\s*["\']?[^\s"\'\n]+["\']?', r'\1: [REDACTED]'),
    ]
    
    @classmethod
    def set_correlation_id(cls, test_name: str, worker_id: Optional[str] = None):
        """
        Set correlation ID for current thread/worker.
        
        Args:
            test_name: Name of the test (used as prefix).
            worker_id: Worker ID (thread ID used if None).
        """
        worker = worker_id or str(threading.get_ident())
        cls._correlation_id.value = f"{test_name}-{worker}"
    
    @classmethod
    def get_correlation_id(cls) -> str:
        """
        Get correlation ID for current thread/worker.
        
        Generates default ID if not set.
        
        Returns:
            str: Correlation ID in format "test-name-<worker-id>".
        """
        if not hasattr(cls._correlation_id, 'value'):
            cls.set_correlation_id("unknown")
        return cls._correlation_id.value
    
    @classmethod
    def redact(cls, message: str) -> str:
        """
        Mask credentials, tokens, and PII in log message.
        
        Args:
            message: Original log message.
            
        Returns:
            str: Message with redacted sensitive values.
        """
        for pattern, replacement in cls.REDACT_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        return message
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get logger instance with correlation ID in every message.
        
        Initializes file handler and formatter once; subsequent calls return cached logger.
        
        Args:
            name: Logger name (typically __name__).
            
        Returns:
            logging.Logger: Logger with correlation ID formatter.
        """
        logger = logging.getLogger(name)
        
        # Configure handler only once per logger
        if not logger.handlers:
            log_dir = ConfigLoader.log_dir()
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")
            
            handler = logging.FileHandler(log_file)
            
            # Custom formatter that injects correlation ID
            class CorrelationIDFormatter(logging.Formatter):
                """Formatter that includes correlation ID and redacts sensitive data."""
                
                def format(self, record):
                    record.correlation_id = StructuredLogger.get_correlation_id()
                    msg = super().format(record)
                    # Redact PII before returning
                    return StructuredLogger.redact(msg)
            
            formatter = CorrelationIDFormatter(
                '%(asctime)s [%(levelname)s] [%(correlation_id)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            
            # Also print to console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
