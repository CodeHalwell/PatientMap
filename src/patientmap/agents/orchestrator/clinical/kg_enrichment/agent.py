"""
Clinical KG Enrichment Agent - Integrates clinical analysis into knowledge graph.
Adds clinical recommendations, specialist insights, and treatment plans to the patient KG.
"""

from __future__ import annotations

from pathlib import Path

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.tools.neo4j_kg_tools import (
    neo4j_bulk_add_conditions,
    neo4j_bulk_add_medications,
    neo4j_create_custom_relationship,
    neo4j_get_patient_overview,
    neo4j_find_related_research,
    neo4j_export_graph_summary,
    neo4j_analyze_graph_connectivity,
    neo4j_list_all_patients,
)
from patientmap.common.helper_functions import retry_config

current_dir = Path(__file__).parent

# Load configuration from .profiles
try:
    config = AgentConfig(str(current_dir / "clinical_kg_enrichment_agent.yaml")).get_agent()
    settings = config
except FileNotFoundError:
    raise RuntimeError(f"Clinical KG enrichment config not found at {current_dir / 'clinical_kg_enrichment_agent.yaml'}")

clinical_kg_enrichment_agent = Agent(
    name=settings.agent_name,
    description=settings.description,
    model=Gemini(model_name=settings.model, retry_options=retry_config),
    instruction=settings.instruction,
    tools=[
        # Neo4j tools - UPDATE existing patient graph with clinical insights ONLY
        # Domain: Add new Condition/Medication nodes + clinical relationships
        # CANNOT add research articles - that's research agent's domain
        neo4j_bulk_add_conditions,  # Add newly diagnosed conditions
        neo4j_bulk_add_medications,  # Add newly prescribed medications
        neo4j_create_custom_relationship,  # For clinical links (e.g., condition→complication)
        neo4j_get_patient_overview,
        neo4j_find_related_research,
        neo4j_export_graph_summary,
        neo4j_analyze_graph_connectivity,
        neo4j_list_all_patients,
    ]
)

root_agent = clinical_kg_enrichment_agent

if __name__ == "__main__":
    print(f"Clinical KG Enrichment Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
