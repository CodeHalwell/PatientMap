"""
Clinical KG Enrichment Agent - Integrates clinical analysis into knowledge graph.
Adds clinical recommendations, specialist insights, and treatment plans to the patient KG.
"""

from __future__ import annotations

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.tools.kg_tools import (
    bulk_add_nodes,
    bulk_add_relationships,
    list_knowledge_graphs,
    load_graph_from_disk,
    get_patient_overview,
    export_graph_summary,
    save_graph_to_disk,
    export_graph_as_cytoscape_json,
    list_all_nodes_by_type,
    get_node_relationships,
)
from patientmap.common.helper_functions import retry_config

# Load configuration from .profiles
try:
    config = AgentConfig("./clinical_kg_enrichment_agent.yaml").get_agent()
    settings = config
except FileNotFoundError:
    raise RuntimeError("Clinical KG enrichment config not found.")

clinical_kg_enrichment_agent = Agent(
    name=settings.agent_name,
    description=settings.description,
    model=Gemini(model_name=settings.model, retry_options=retry_config),
    instruction=settings.instruction,
    tools=[
        list_knowledge_graphs,
        load_graph_from_disk,
        bulk_add_nodes,
        bulk_add_relationships,
        get_patient_overview,
        export_graph_summary,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        list_all_nodes_by_type,
        get_node_relationships,
    ]
)

root_agent = clinical_kg_enrichment_agent

if __name__ == "__main__":
    print(f"Clinical KG Enrichment Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
