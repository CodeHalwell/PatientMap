"""
Builder Agent - Creates and updates the patient knowledge graph.
Uses bulk operations to add nodes and relationships based on plan.
"""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.neo4j_kg_tools import (
    verify_neo4j_connection,
    initialize_neo4j_schema,
    neo4j_initialize_patient_graph,
    neo4j_bulk_add_conditions,
    neo4j_bulk_add_medications,
    neo4j_create_custom_relationship,
    neo4j_get_patient_overview,
    neo4j_export_graph_summary,
    neo4j_analyze_graph_connectivity,
    neo4j_list_all_patients,
)

current_dir = Path(__file__).parent

try:
    builder_settings = AgentConfig(str(current_dir / "kg_initialiser.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Builder config not found at {current_dir / 'kg_initialiser.yaml'}")

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
        # Neo4j persistent graph database tools
        verify_neo4j_connection,
        initialize_neo4j_schema,
        neo4j_initialize_patient_graph,
        neo4j_bulk_add_conditions,  # Batch add conditions
        neo4j_bulk_add_medications,  # Batch add medications
        neo4j_create_custom_relationship,  # For TREATS_CONDITION links
        neo4j_get_patient_overview,
        neo4j_export_graph_summary,
        neo4j_analyze_graph_connectivity,
        neo4j_list_all_patients,
    ],
)

root_agent = build_agent

if __name__ == "__main__":
    print(f"Builder Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
