from google.genai.types import HttpRetryOptions
from typing import Any, Optional
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import google_search, url_context, AgentTool, BaseTool

retry_config = HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

async def handle_tool_error(
    *,
    tool: BaseTool,
    tool_args: dict[str, Any],
    tool_context: ToolContext,
    error: Exception,
) -> Optional[dict]:
    """Handle tool errors gracefully by returning a fallback message."""
    error_message = f"Tool {tool.name} encountered an error: {str(error)}. Continuing without this information."
    return {
        "error": str(error),
        "tool_name": tool.name,
        "message": error_message,
        "success": False
    }