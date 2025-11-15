"""
Central Tool Registry for PatientMap Agents

This module provides a single source of truth for all tools available to agents.
By explicitly registering tools here, we help prevent LLM hallucination of non-existent tools.

Usage Pattern:
1. All tools are registered in TOOL_REGISTRY with their actual Python objects
2. Agents load tools from their YAML configs using get_tools_from_config()
3. Agents can call get_available_tools() to see what tools they have access to

Tool Categories:
- ADK Built-in Tools: google_search, url_context, exit_loop (from Google ADK)
- Research Tools: Google Scholar, PubMed, Semantic Scholar, Wikipedia
- Neo4j KG Tools: Graph creation, querying, and relationship management
- Specialist Agents: 16 clinical specialists exposed as AgentTool instances
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
import json
import sys
from pathlib import Path

# Add src to path if running directly
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Google ADK built-in tools
from google.adk.tools import google_search, url_context, exit_loop, AgentTool

# Research tools from our custom module
from patientmap.tools.research_tools import (
    google_scholar_tool,
    pubmed_tool,
    semantic_scholar_tool,
    wikipedia_tool
)

# Admin/Meta tools
from patientmap.tools.admin_tools import (
    show_my_available_tools,
    check_tool_exists,
    list_tools_by_category,
)

# Neo4j KG tools - import all functions from neo4j_kg_tools
from patientmap.tools.neo4j_kg_tools import (
    # Connection Management
    verify_neo4j_connection,
    initialize_neo4j_schema,
    
    # Graph Initialization
    neo4j_initialize_patient_graph,
    
    # Node Operations
    neo4j_add_condition,
    neo4j_add_medication,
    neo4j_bulk_add_conditions,
    neo4j_bulk_add_medications,
    neo4j_add_research_article,
    neo4j_add_clinical_trial,
    
    # Relationship Operations
    neo4j_link_article_to_condition,
    neo4j_bulk_link_articles_to_conditions,
    neo4j_bulk_link_articles_to_medications,
    
    # Query Operations
    neo4j_get_patient_overview,
    neo4j_find_related_research,
    neo4j_export_graph_summary,
    neo4j_analyze_graph_connectivity,
    
    # Persistence Operations
    neo4j_clear_patient_graph,
    neo4j_list_all_patients,
    
    # Generic Node and Relationship Tools
    neo4j_create_custom_node,
    neo4j_create_custom_relationship,
    neo4j_delete_node,
    neo4j_bulk_create_custom_nodes,
    neo4j_bulk_create_custom_relationships,
)


# ==============================================================================
# TOOL REGISTRY - Single Source of Truth for All Available Tools
# ==============================================================================

TOOL_REGISTRY: Dict[str, Any] = {
    # -------------------------------------------------------------------------
    # ADK Built-in Tools (provided by Google Agent Development Kit)
    # -------------------------------------------------------------------------
    "google_search": google_search,
    "url_context": url_context,
    "exit_loop": exit_loop,
    
    # -------------------------------------------------------------------------
    # Admin/Meta Tools (help agents understand their capabilities)
    # -------------------------------------------------------------------------
    "show_my_available_tools": show_my_available_tools,
    "check_tool_exists": check_tool_exists,
    "list_tools_by_category": list_tools_by_category,
    
    # -------------------------------------------------------------------------
    # Research Tools (LangChain-based literature search)
    # -------------------------------------------------------------------------
    "google_scholar_tool": google_scholar_tool(),
    "pubmed_tool": pubmed_tool(),
    "semantic_scholar_tool": semantic_scholar_tool(),
    "wikipedia_tool": wikipedia_tool(),
    
    # -------------------------------------------------------------------------
    # Neo4j Knowledge Graph Tools - Connection Management
    # -------------------------------------------------------------------------
    "verify_neo4j_connection": verify_neo4j_connection,
    "initialize_neo4j_schema": initialize_neo4j_schema,
    
    # -------------------------------------------------------------------------
    # Neo4j Knowledge Graph Tools - Graph Initialization
    # -------------------------------------------------------------------------
    "neo4j_initialize_patient_graph": neo4j_initialize_patient_graph,
    
    # -------------------------------------------------------------------------
    # Neo4j Knowledge Graph Tools - Node Operations
    # -------------------------------------------------------------------------
    "neo4j_add_condition": neo4j_add_condition,
    "neo4j_add_medication": neo4j_add_medication,
    "neo4j_bulk_add_conditions": neo4j_bulk_add_conditions,
    "neo4j_bulk_add_medications": neo4j_bulk_add_medications,
    "neo4j_add_research_article": neo4j_add_research_article,
    "neo4j_add_clinical_trial": neo4j_add_clinical_trial,
    
    # -------------------------------------------------------------------------
    # Neo4j Knowledge Graph Tools - Relationship Operations
    # -------------------------------------------------------------------------
    "neo4j_link_article_to_condition": neo4j_link_article_to_condition,
    "neo4j_bulk_link_articles_to_conditions": neo4j_bulk_link_articles_to_conditions,
    "neo4j_bulk_link_articles_to_medications": neo4j_bulk_link_articles_to_medications,
    
    # -------------------------------------------------------------------------
    # Neo4j Knowledge Graph Tools - Query Operations
    # -------------------------------------------------------------------------
    "neo4j_get_patient_overview": neo4j_get_patient_overview,
    "neo4j_find_related_research": neo4j_find_related_research,
    "neo4j_export_graph_summary": neo4j_export_graph_summary,
    "neo4j_analyze_graph_connectivity": neo4j_analyze_graph_connectivity,
    
    # -------------------------------------------------------------------------
    # Neo4j Knowledge Graph Tools - Persistence Operations
    # -------------------------------------------------------------------------
    "neo4j_clear_patient_graph": neo4j_clear_patient_graph,
    "neo4j_list_all_patients": neo4j_list_all_patients,
    
    # -------------------------------------------------------------------------
    # Neo4j Knowledge Graph Tools - Generic Node and Relationship Creation
    # -------------------------------------------------------------------------
    "neo4j_create_custom_node": neo4j_create_custom_node,
    "neo4j_create_custom_relationship": neo4j_create_custom_relationship,
    "neo4j_delete_node": neo4j_delete_node,
    "neo4j_bulk_create_custom_nodes": neo4j_bulk_create_custom_nodes,
    "neo4j_bulk_create_custom_relationships": neo4j_bulk_create_custom_relationships,
}


# ==============================================================================
# TOOL METADATA - Descriptions for Agent Context
# ==============================================================================

TOOL_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    # ADK Built-in Tools
    "google_search": {
        "category": "ADK Built-in",
        "description": "Search Google for current information and web resources",
        "usage": "google_search(query: str) -> str"
    },
    "url_context": {
        "category": "ADK Built-in",
        "description": "Fetch and extract content from a URL",
        "usage": "url_context(url: str) -> str"
    },
    "exit_loop": {
        "category": "ADK Built-in",
        "description": "Exit a loop agent iteration (only available in LoopAgent checker agents)",
        "usage": "exit_loop() -> None"
    },
    
    # Admin/Meta Tools
    "show_my_available_tools": {
        "category": "Admin/Meta",
        "description": "Show agent what tools it has access to with full descriptions - prevents hallucination",
        "usage": "show_my_available_tools(tool_context: ToolContext) -> str"
    },
    "check_tool_exists": {
        "category": "Admin/Meta",
        "description": "Check if a specific tool exists before attempting to call it",
        "usage": "check_tool_exists(tool_name: str, tool_context: ToolContext) -> str"
    },
    "list_tools_by_category": {
        "category": "Admin/Meta",
        "description": "List all tools in a specific category",
        "usage": "list_tools_by_category(category: str, tool_context: ToolContext) -> str"
    },
    
    # Research Tools
    "google_scholar_tool": {
        "category": "Research",
        "description": "Search Google Scholar for academic papers and citations",
        "usage": "google_scholar_tool(query: str) -> str"
    },
    "pubmed_tool": {
        "category": "Research",
        "description": "Search PubMed for medical research articles",
        "usage": "pubmed_tool(query: str) -> str"
    },
    "semantic_scholar_tool": {
        "category": "Research",
        "description": "Search Semantic Scholar for academic papers with citation data",
        "usage": "semantic_scholar_tool(query: str) -> str"
    },
    "wikipedia_tool": {
        "category": "Research",
        "description": "Search Wikipedia for general medical and scientific information",
        "usage": "wikipedia_tool(query: str) -> str"
    },
    
    # Neo4j Connection Tools
    "verify_neo4j_connection": {
        "category": "Neo4j Connection",
        "description": "Verify Neo4j database connection and get server info",
        "usage": "verify_neo4j_connection(tool_context: ToolContext) -> str"
    },
    "initialize_neo4j_schema": {
        "category": "Neo4j Connection",
        "description": "Initialize database constraints and indexes (call once per session)",
        "usage": "initialize_neo4j_schema(tool_context: ToolContext) -> str"
    },
    
    # Neo4j Graph Initialization
    "neo4j_initialize_patient_graph": {
        "category": "Neo4j Initialization",
        "description": "Create a new Patient node to anchor the knowledge graph",
        "usage": "neo4j_initialize_patient_graph(patient_id: str, patient_name: str, tool_context: ToolContext) -> str"
    },
    
    # Neo4j Node Creation
    "neo4j_add_condition": {
        "category": "Neo4j Nodes",
        "description": "Add a single medical condition to patient's knowledge graph",
        "usage": "neo4j_add_condition(patient_id: str, condition_id: str, condition_name: str, icd_code: str, symptoms: list, tool_context: ToolContext) -> str"
    },
    "neo4j_add_medication": {
        "category": "Neo4j Nodes",
        "description": "Add a single medication to patient's knowledge graph",
        "usage": "neo4j_add_medication(patient_id: str, medication_id: str, medication_name: str, dosage: str, frequency: str, side_effects: list, tool_context: ToolContext) -> str"
    },
    "neo4j_bulk_add_conditions": {
        "category": "Neo4j Nodes",
        "description": "Add multiple conditions efficiently using batch processing",
        "usage": "neo4j_bulk_add_conditions(patient_id: str, conditions: list[dict], tool_context: ToolContext) -> str"
    },
    "neo4j_bulk_add_medications": {
        "category": "Neo4j Nodes",
        "description": "Add multiple medications efficiently using batch processing",
        "usage": "neo4j_bulk_add_medications(patient_id: str, medications: list[dict], tool_context: ToolContext) -> str"
    },
    "neo4j_add_research_article": {
        "category": "Neo4j Nodes",
        "description": "Add a research article node with citation metadata",
        "usage": "neo4j_add_research_article(article_id: str, article_title: str, authors: list, publication_date: str, journal: str, url: str, abstract: str, keywords: list, tool_context: ToolContext) -> str"
    },
    "neo4j_add_clinical_trial": {
        "category": "Neo4j Nodes",
        "description": "Add a clinical trial node with study details",
        "usage": "neo4j_add_clinical_trial(trial_id: str, trial_title: str, phase: str, status: str, conditions: list, interventions: list, url: str, enrollment: int, start_date: str, completion_date: str, tool_context: ToolContext) -> str"
    },
    
    # Neo4j Relationships
    "neo4j_link_article_to_condition": {
        "category": "Neo4j Relationships",
        "description": "Link a research article to a medical condition with relevance metadata",
        "usage": "neo4j_link_article_to_condition(article_id: str, condition_id: str, relevance: str, confidence: float, tool_context: ToolContext) -> str"
    },
    "neo4j_bulk_link_articles_to_conditions": {
        "category": "Neo4j Relationships",
        "description": "Create multiple article-condition links efficiently",
        "usage": "neo4j_bulk_link_articles_to_conditions(links: list[dict], tool_context: ToolContext) -> str"
    },
    "neo4j_bulk_link_articles_to_medications": {
        "category": "Neo4j Relationships",
        "description": "Create multiple article-medication links efficiently",
        "usage": "neo4j_bulk_link_articles_to_medications(links: list[dict], tool_context: ToolContext) -> str"
    },
    
    # Neo4j Queries
    "neo4j_get_patient_overview": {
        "category": "Neo4j Queries",
        "description": "Get comprehensive overview of patient's knowledge graph",
        "usage": "neo4j_get_patient_overview(patient_id: str, tool_context: ToolContext) -> str"
    },
    "neo4j_find_related_research": {
        "category": "Neo4j Queries",
        "description": "Find research articles related to a specific condition",
        "usage": "neo4j_find_related_research(condition_id: str, max_results: int, tool_context: ToolContext) -> str"
    },
    "neo4j_export_graph_summary": {
        "category": "Neo4j Queries",
        "description": "Export statistics about the entire knowledge graph",
        "usage": "neo4j_export_graph_summary(tool_context: ToolContext) -> str"
    },
    "neo4j_analyze_graph_connectivity": {
        "category": "Neo4j Queries",
        "description": "Analyze connectivity patterns and graph completeness",
        "usage": "neo4j_analyze_graph_connectivity(patient_id: str, tool_context: ToolContext) -> str"
    },
    
    # Neo4j Persistence
    "neo4j_clear_patient_graph": {
        "category": "Neo4j Persistence",
        "description": "Delete all data for a specific patient (WARNING: irreversible)",
        "usage": "neo4j_clear_patient_graph(patient_id: str, tool_context: ToolContext) -> str"
    },
    "neo4j_list_all_patients": {
        "category": "Neo4j Persistence",
        "description": "List all patients in the database with basic stats",
        "usage": "neo4j_list_all_patients(tool_context: ToolContext) -> str"
    },
    
    # Neo4j Generic Tools
    "neo4j_create_custom_node": {
        "category": "Neo4j Generic",
        "description": "Create a custom node with any label and properties",
        "usage": "neo4j_create_custom_node(node_id: str, node_label: str, properties: dict, tool_context: ToolContext) -> str"
    },
    "neo4j_create_custom_relationship": {
        "category": "Neo4j Generic",
        "description": "Create a custom relationship between any two nodes",
        "usage": "neo4j_create_custom_relationship(from_node_id: str, from_node_label: str, to_node_id: str, to_node_label: str, relationship_type: str, properties: dict, tool_context: ToolContext) -> str"
    },
    "neo4j_delete_node": {
        "category": "Neo4j Generic",
        "description": "Delete a specific node and all its relationships",
        "usage": "neo4j_delete_node(node_id: str, node_label: str, tool_context: ToolContext) -> str"
    },
    "neo4j_bulk_create_custom_nodes": {
        "category": "Neo4j Generic",
        "description": "Create multiple custom nodes with the same label efficiently",
        "usage": "neo4j_bulk_create_custom_nodes(nodes: list[dict], node_label: str, tool_context: ToolContext) -> str"
    },
    "neo4j_bulk_create_custom_relationships": {
        "category": "Neo4j Generic",
        "description": "Create multiple custom relationships of the same type efficiently",
        "usage": "neo4j_bulk_create_custom_relationships(relationships: list[dict], relationship_type: str, tool_context: ToolContext) -> str"
    },
}


# ==============================================================================
# SPECIALIST AGENT REGISTRY
# ==============================================================================
# Note: Specialist agents are loaded dynamically at runtime in clinical/manager/agent.py
# They are NOT included in TOOL_REGISTRY because they're AgentTool instances,
# not function tools. Specialists are:
#
# - cardiology_agent (Cardiology)
# - neurology_agent (Neurology)
# - psychiatry_agent (Psychiatry)
# - endocrinology_agent (Endocrinology)
# - pharmacy_agent (Clinical Pharmacy)
# - gastroenterology_agent (Gastroenterology)
# - geriatrics_agent (Geriatrics)
# - hematology_agent (Hematology)
# - nephrology_agent (Nephrology)
# - pulmonology_agent (Pulmonology)
# - physical_agent (Physical Medicine & Rehabilitation)
# - infectious_disease_agent (Infectious Disease)
# - nutrition_agent (Nutrition & Dietetics)
# - pain_agent (Pain Medicine)
# - rheumatology_agent (Rheumatology)
# - palliative_agent (Palliative Care)
#
# These are only available to clinical_manager_agent as AgentTool instances.


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_tools_from_config(tool_names: List[str]) -> List[Any]:
    """
    Convert a list of tool names from YAML config to actual tool objects.
    
    Args:
        tool_names: List of tool name strings from agent YAML config
        
    Returns:
        List of actual tool objects that can be passed to LlmAgent/Agent
        
    Example:
        >>> tools = get_tools_from_config(["google_search", "url_context", "exit_loop"])
        >>> # Returns [google_search, url_context, exit_loop] objects
    """
    tools = []
    for tool_name in tool_names:
        if tool_name in TOOL_REGISTRY:
            tools.append(TOOL_REGISTRY[tool_name])
        else:
            raise ValueError(
                f"Tool '{tool_name}' not found in TOOL_REGISTRY. "
                f"Available tools: {list(TOOL_REGISTRY.keys())}"
            )
    return tools


def get_available_tools(tool_names: Optional[List[str]] = None) -> str:
    """
    Get a formatted list of available tools with descriptions.
    
    This function is designed to be called by LLM agents to see what tools
    they have access to, helping prevent hallucination of non-existent tools.
    
    Args:
        tool_names: Optional list of tool names to filter by. If None, returns all tools.
        
    Returns:
        JSON string with tool information formatted for LLM consumption
        
    Example:
        >>> # Agent with specific tools
        >>> info = get_available_tools(["google_search", "url_context"])
        >>> print(info)
        {
          "total_tools": 2,
          "tools": [
            {
              "name": "google_search",
              "category": "ADK Built-in",
              "description": "Search Google for current information",
              "usage": "google_search(query: str) -> str"
            },
            ...
          ]
        }
    """
    if tool_names is None:
        # Return all tools
        tool_names = list(TOOL_REGISTRY.keys())
    
    # Filter to only requested tools
    available = []
    unavailable = []
    
    for tool_name in tool_names:
        if tool_name in TOOL_DESCRIPTIONS:
            tool_info = TOOL_DESCRIPTIONS[tool_name].copy()
            tool_info["name"] = tool_name
            available.append(tool_info)
        else:
            unavailable.append(tool_name)
    
    # Group by category
    by_category: Dict[str, List[Dict[str, str]]] = {}
    for tool in available:
        category = tool["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(tool)
    
    result = {
        "total_tools": len(available),
        "tools_by_category": by_category,
        "all_tools": available,
    }
    
    if unavailable:
        result["warning"] = f"Requested tools not found in registry: {unavailable}"
    
    return json.dumps(result, indent=2)


def list_all_tools_by_category() -> str:
    """
    List all tools in the registry organized by category.
    
    Useful for documentation and debugging.
    
    Returns:
        JSON string with all tools grouped by category
    """
    return get_available_tools(tool_names=None)


def validate_agent_tools(agent_name: str, tool_names: List[str]) -> Dict[str, Any]:
    """
    Validate that all tools requested by an agent exist in the registry.
    
    Args:
        agent_name: Name of the agent for error messages
        tool_names: List of tool names from agent's YAML config
        
    Returns:
        Dictionary with validation results:
        - valid: bool (True if all tools exist)
        - missing_tools: list of tool names not found
        - available_tools: list of valid tool names
        
    Example:
        >>> result = validate_agent_tools("research_agent", ["google_search", "fake_tool"])
        >>> print(result)
        {
          "valid": False,
          "missing_tools": ["fake_tool"],
          "available_tools": ["google_search"]
        }
    """
    available = []
    missing = []
    
    for tool_name in tool_names:
        if tool_name in TOOL_REGISTRY:
            available.append(tool_name)
        else:
            missing.append(tool_name)
    
    return {
        "agent_name": agent_name,
        "valid": len(missing) == 0,
        "missing_tools": missing,
        "available_tools": available,
        "total_requested": len(tool_names),
        "total_valid": len(available)
    }


# ==============================================================================
# CONSTANTS FOR AGENT DEVELOPERS
# ==============================================================================

# List of all available tool names (for quick reference)
ALL_TOOL_NAMES = sorted(TOOL_REGISTRY.keys())

# Tools by category (for easier navigation)
ADK_BUILTIN_TOOLS = ["google_search", "url_context", "exit_loop"]
ADMIN_META_TOOLS = ["show_my_available_tools", "check_tool_exists", "list_tools_by_category"]
RESEARCH_TOOLS = ["google_scholar_tool", "pubmed_tool", "semantic_scholar_tool", "wikipedia_tool"]
NEO4J_CONNECTION_TOOLS = ["verify_neo4j_connection", "initialize_neo4j_schema"]
NEO4J_INIT_TOOLS = ["neo4j_initialize_patient_graph"]
NEO4J_NODE_TOOLS = [
    "neo4j_add_condition", "neo4j_add_medication", 
    "neo4j_bulk_add_conditions", "neo4j_bulk_add_medications",
    "neo4j_add_research_article", "neo4j_add_clinical_trial"
]
NEO4J_RELATIONSHIP_TOOLS = [
    "neo4j_link_article_to_condition",
    "neo4j_bulk_link_articles_to_conditions",
    "neo4j_bulk_link_articles_to_medications"
]
NEO4J_QUERY_TOOLS = [
    "neo4j_get_patient_overview", "neo4j_find_related_research",
    "neo4j_export_graph_summary", "neo4j_analyze_graph_connectivity"
]
NEO4J_PERSISTENCE_TOOLS = ["neo4j_clear_patient_graph", "neo4j_list_all_patients"]
NEO4J_GENERIC_TOOLS = [
    "neo4j_create_custom_node", "neo4j_create_custom_relationship",
    "neo4j_delete_node", "neo4j_bulk_create_custom_nodes",
    "neo4j_bulk_create_custom_relationships"
]

# All Neo4j tools combined
ALL_NEO4J_TOOLS = (
    NEO4J_CONNECTION_TOOLS + NEO4J_INIT_TOOLS + NEO4J_NODE_TOOLS +
    NEO4J_RELATIONSHIP_TOOLS + NEO4J_QUERY_TOOLS + 
    NEO4J_PERSISTENCE_TOOLS + NEO4J_GENERIC_TOOLS
)


if __name__ == "__main__":
    # Print registry summary when run directly
    print("=" * 80)
    print("PATIENTMAP TOOL REGISTRY SUMMARY")
    print("=" * 80)
    print(f"\nTotal tools registered: {len(TOOL_REGISTRY)}")
    print(f"\nADK Built-in Tools: {len(ADK_BUILTIN_TOOLS)}")
    print(f"Research Tools: {len(RESEARCH_TOOLS)}")
    print(f"Neo4j Tools: {len(ALL_NEO4J_TOOLS)}")
    print("\n" + "=" * 80)
    print("\nAll tools by category:")
    print("=" * 80)
    print(list_all_tools_by_category())
