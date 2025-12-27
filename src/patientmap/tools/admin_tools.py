"""
Administrative Tools for PatientMap Agents

Provides meta-tools that help agents understand their capabilities
and prevent hallucination of non-existent tools.
"""

from __future__ import annotations
from typing import Optional
from google.adk.tools.tool_context import ToolContext


def show_my_available_tools(tool_context: ToolContext) -> str:
    """
    Show the agent what tools it has access to with full descriptions.
    
    This tool helps prevent LLM hallucination by explicitly documenting
    what tools are available. Agents should call this tool when they:
    - Are unsure what tools they can use
    - Need to verify a tool exists before attempting to call it
    - Want to see usage examples for a tool
    
    The tool will return a comprehensive list of all tools the agent
    has been configured with, including:
    - Tool name
    - Category (ADK Built-in, Research, Neo4j, etc.)
    - Description of what the tool does
    - Usage signature showing parameters
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with all available tools and their metadata
        
    Example Output:
        {
          "total_tools": 5,
          "tools_by_category": {
            "ADK Built-in": [
              {
                "name": "google_search",
                "description": "Search Google for current information",
                "usage": "google_search(query: str) -> str"
              }
            ],
            "Research": [...]
          }
        }
    """
    # Import here to avoid circular import
    from patientmap.tools.tool_registry import get_available_tools
    
    # Note: In practice, agents would pass their own tool list here
    # For now, we return all available tools
    # A more sophisticated implementation would introspect the calling agent
    
    return get_available_tools(tool_names=None)


def check_tool_exists(tool_name: str, tool_context: ToolContext) -> str:
    """
    Check if a specific tool exists in the registry.
    
    Use this tool BEFORE attempting to call a tool you're unsure about.
    This prevents runtime errors from calling non-existent tools.
    
    Args:
        tool_name: Name of the tool to check (e.g., "google_search")
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string indicating if tool exists and its details if found
        
    Example:
        >>> check_tool_exists("google_search", tool_context)
        {
          "exists": true,
          "tool_name": "google_search",
          "category": "ADK Built-in",
          "description": "Search Google for current information",
          "usage": "google_search(query: str) -> str"
        }
        
        >>> check_tool_exists("fake_tool", tool_context)
        {
          "exists": false,
          "tool_name": "fake_tool",
          "error": "Tool not found in registry"
        }
    """
    import json
    # Import here to avoid circular import
    from patientmap.tools.tool_registry import TOOL_DESCRIPTIONS
    
    if tool_name in TOOL_DESCRIPTIONS:
        tool_info = TOOL_DESCRIPTIONS[tool_name].copy()
        tool_info["exists"] = True
        tool_info["tool_name"] = tool_name
        return json.dumps(tool_info, indent=2)
    else:
        return json.dumps({
            "exists": False,
            "tool_name": tool_name,
            "error": "Tool not found in registry",
            "suggestion": "Call show_my_available_tools to see all available tools"
        }, indent=2)


def list_tools_by_category(category: str, tool_context: ToolContext) -> str:
    """
    List all tools in a specific category.
    
    Useful for discovering what tools are available for a specific purpose.
    
    Available categories:
    - "ADK Built-in": Google search, URL context, loop control
    - "Research": Academic literature search tools
    - "Neo4j Connection": Database connection management
    - "Neo4j Initialization": Patient graph setup
    - "Neo4j Nodes": Create conditions, medications, articles
    - "Neo4j Relationships": Link entities together
    - "Neo4j Queries": Query and analyze the graph
    - "Neo4j Persistence": Save and manage graph data
    - "Neo4j Generic": Custom node/relationship creation
    
    Args:
        category: Category name to filter by
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with all tools in that category
    """
    import json
    # Import here to avoid circular import
    from patientmap.tools.tool_registry import TOOL_DESCRIPTIONS
    
    tools_in_category = [
        {
            "name": name,
            **info
        }
        for name, info in TOOL_DESCRIPTIONS.items()
        if info["category"] == category
    ]
    
    if not tools_in_category:
        available_categories = sorted(set(
            info["category"] for info in TOOL_DESCRIPTIONS.values()
        ))
        return json.dumps({
            "error": f"Category '{category}' not found",
            "available_categories": available_categories
        }, indent=2)
    
    return json.dumps({
        "category": category,
        "total_tools": len(tools_in_category),
        "tools": tools_in_category
    }, indent=2)


# Tool registry for admin tools (to be added to main TOOL_REGISTRY if needed)
ADMIN_TOOLS = {
    "show_my_available_tools": show_my_available_tools,
    "check_tool_exists": check_tool_exists,
    "list_tools_by_category": list_tools_by_category,
}
