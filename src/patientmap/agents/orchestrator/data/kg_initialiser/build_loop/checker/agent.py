"""
Checker Agent - Validates knowledge graph structure and completeness.
Provides feedback to builder and calls exit_loop when satisfied.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import exit_loop
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.kg_tools import (
    validate_graph_structure,
    check_node_completeness,
    bulk_check_node_completeness,
    analyze_graph_connectivity,
    list_all_nodes_by_type,
    get_node_relationships,
    export_graph_summary,
    load_graph_from_disk,
    save_graph_to_disk,
    export_graph_as_cytoscape_json,
)

# Load configuration from .profiles
config_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "kg_checker_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    checker_settings = config
except FileNotFoundError:
    raise RuntimeError(f"Checker config not found at {config_path}")

# Create logic checker agent
logic_checker_agent = LlmAgent(
    name=checker_settings.agent_name,
    description=checker_settings.description,
    model=Gemini(
        model_name=checker_settings.model,
        retry_options=retry_config
    ),
    instruction=checker_settings.instruction,
    tools=[
        validate_graph_structure,
        check_node_completeness,
        bulk_check_node_completeness,
        analyze_graph_connectivity,
        list_all_nodes_by_type,
        get_node_relationships,
        export_graph_summary,
        load_graph_from_disk,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        exit_loop,  # Critical: allows checker to end loop
    ],
)

root_agent = logic_checker_agent

if __name__ == "__main__":
    print(f"Checker Agent: {root_agent.name}")
    print(f"Has exit_loop: {exit_loop in root_agent.tools}")
