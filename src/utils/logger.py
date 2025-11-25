"""Structured logging utilities for maf-local.

Provides a centralized logger configuration for consistent logging across all
agents, workflows, and modules. Replaces ad-hoc print() statements with proper
structured logging for better observability.
"""

import logging
import sys
from typing import Optional


# Global log level - can be configured via environment variable
DEFAULT_LOG_LEVEL = logging.INFO


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        level: Optional log level override
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting workflow execution")
        >>> logger.error("Failed to process task", exc_info=True)
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured (avoid duplicate handlers)
    if not logger.handlers:
        logger.setLevel(level or DEFAULT_LOG_LEVEL)
        
        # Console handler with formatted output
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level or DEFAULT_LOG_LEVEL)
        
        # Format: [LEVEL] module_name: message
        formatter = logging.Formatter(
            fmt='[%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger


# Convenience function for quick setup
def configure_logging(level: int = DEFAULT_LOG_LEVEL):
    """Configure root logger for the entire application.
    
    Args:
        level: Log level (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=level,
        format='[%(levelname)s] %(name)s: %(message)s',
        stream=sys.stdout
    )
