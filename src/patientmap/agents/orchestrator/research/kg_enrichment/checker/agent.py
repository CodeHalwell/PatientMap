"""
Enrichment Checker - Validates knowledge graph enrichment.
Checks structure, completeness, and clinical accuracy after enrichment.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import exit_loop
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
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
from patientmap.common.helper_functions import retry_config

try:
    kg_checker_config = AgentConfig("./kg_checker_agent.yaml").get_agent()
except FileNotFoundError:
    raise RuntimeError("KG checker config not found. Please ensure kg_checker_agent.yaml exists in the current directory.")

# Create a separate instance of logic_checker for this loop
enrichment_checker = LlmAgent(
    name=kg_checker_config.agent_name,
    description=kg_checker_config.description,
    model=Gemini(model_name=kg_checker_config.model, retry_options=retry_config),
    instruction=kg_checker_config.instruction,
    tools=[
        validate_graph_structure,
        check_node_completeness,
        bulk_check_node_completeness,
        analyze_graph_connectivity,
        list_all_nodes_by_type,
        get_node_relationships,
        export_graph_summary,
        load_graph_from_disk,
        exit_loop,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
    ],
)

root_agent = enrichment_checker

if __name__ == "__main__":
    print(f"Enrichment Checker: {root_agent.name}")
    print(f"Has exit_loop: {exit_loop in root_agent.tools}")
