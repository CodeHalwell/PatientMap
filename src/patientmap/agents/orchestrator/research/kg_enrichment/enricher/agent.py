"""
Enricher Agent - Adds research findings to the knowledge graph.
Uses KG tools to load, enrich, and save the patient knowledge graph.
"""

from __future__ import annotations

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.tools.kg_tools import (
    bulk_add_nodes,
    bulk_add_relationships,
    bulk_link_articles_to_conditions,
    list_all_nodes_by_type,
    get_node_relationships,
    list_knowledge_graphs,
    load_graph_from_disk,
    get_patient_overview,
    export_graph_summary,
    save_graph_to_disk,
    export_graph_as_cytoscape_json,
    delete_node,
    delete_relationship,
    merge_duplicate_nodes,
)
from patientmap.common.helper_functions import retry_config

try:
    knowledge_graph_agent_settings = AgentConfig("./knowledge_graph_agent.yaml").get_agent()
except FileNotFoundError:
    raise RuntimeError("Knowledge Graph agent config not found. Please ensure knowledge_graph_agent.yaml exists in the current directory.")

knowledge_graph_agent = Agent(
    name=knowledge_graph_agent_settings.agent_name,
    description=knowledge_graph_agent_settings.description,
    model=Gemini(model_name=knowledge_graph_agent_settings.model, retry_options=retry_config),
    instruction=knowledge_graph_agent_settings.instruction,
    tools=[
        list_knowledge_graphs,
        load_graph_from_disk,
        bulk_add_nodes,
        bulk_add_relationships,
        bulk_link_articles_to_conditions,
        get_patient_overview,
        export_graph_summary,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        list_all_nodes_by_type,
        get_node_relationships,
        delete_node,
        delete_relationship,
        merge_duplicate_nodes,
    ]
)

root_agent = knowledge_graph_agent

if __name__ == "__main__":
    print(f"Enricher Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
