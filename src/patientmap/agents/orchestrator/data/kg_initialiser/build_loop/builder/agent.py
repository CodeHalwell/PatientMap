"""
Builder Agent - Creates and updates the patient knowledge graph.
Uses bulk operations to add nodes and relationships based on plan.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.kg_tools import (
    initialize_patient_graph,
    bulk_add_nodes,
    bulk_add_relationships,
    delete_node,
    delete_relationship,
    merge_duplicate_nodes,
    get_patient_overview,
    export_graph_summary,
    save_graph_to_disk,
    export_graph_as_cytoscape_json,
    validate_graph_structure,
)

try:
    builder_settings = AgentConfig("./kg_initialiser.yaml").get_agent()
except FileNotFoundError:
    raise RuntimeError("Builder config not found. Please ensure kg_initialiser.yaml exists in the current directory.")

# Create builder agent with KG tools
build_agent = LlmAgent(
    name=builder_settings.agent_name,
    description=builder_settings.description,
    model=Gemini(
        model_name=builder_settings.model,
        retry_options=retry_config
    ),
    instruction=builder_settings.instruction,
    tools=[
        initialize_patient_graph,
        bulk_add_nodes,
        bulk_add_relationships,
        delete_node,
        delete_relationship,
        merge_duplicate_nodes,
        get_patient_overview,
        export_graph_summary,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        validate_graph_structure,
    ],
)

root_agent = build_agent

if __name__ == "__main__":
    print(f"Builder Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
