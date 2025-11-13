"""
Logging configuration for PatientMap agents
"""
import logging
import atexit
import warnings
from google.adk.plugins.logging_plugin import (
    LoggingPlugin, 
)


def _suppress_shutdown_warnings():
    """Suppress aiohttp unclosed session warnings that occur during shutdown."""
    # Suppress ResourceWarnings from aiohttp during shutdown
    warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")
    # Temporarily increase asyncio logging level to suppress shutdown errors
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)


def configure_logging():
    """Configure logging to suppress harmless shutdown warnings from LangChain tools."""
    # Register cleanup handler to suppress warnings during application shutdown
    atexit.register(_suppress_shutdown_warnings)
    
    # Note: These "Unclosed client session" errors are internal to LangChain's HTTP tools
    # and don't affect functionality. They only appear during shutdown.

async def get_logging_plugin() -> LoggingPlugin:
    """Create and return a LoggingPlugin instance for logging agent activities."""
    logging_plugin = LoggingPlugin()
    return logging_plugin