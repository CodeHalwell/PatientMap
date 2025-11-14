"""
Enricher Agent - Adds research findings to the knowledge graph.
Uses KG tools to load, enrich, and save the patient knowledge graph.
"""

from __future__ import annotations

from pathlib import Path

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.tools.neo4j_kg_tools import (
    neo4j_add_research_article,
    neo4j_add_clinical_trial,
    neo4j_link_article_to_condition,
    neo4j_bulk_link_articles_to_conditions,
    neo4j_create_custom_relationship,
    neo4j_get_patient_overview,
    neo4j_find_related_research,
    neo4j_export_graph_summary,
    neo4j_analyze_graph_connectivity,
    neo4j_list_all_patients,
)
from patientmap.common.helper_functions import retry_config

current_dir = Path(__file__).parent

try:
    knowledge_graph_agent_settings = AgentConfig(str(current_dir / "knowledge_graph_agent.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Knowledge Graph agent config not found at {current_dir / 'knowledge_graph_agent.yaml'}")

knowledge_graph_agent = Agent(
    name=knowledge_graph_agent_settings.agent_name,
    description=knowledge_graph_agent_settings.description,
    model=Gemini(model_name=knowledge_graph_agent_settings.model, retry_options=retry_config),
    instruction=knowledge_graph_agent_settings.instruction,
    tools=[
        # Neo4j tools - UPDATE existing patient graph with research ONLY
        # Domain: ResearchArticle and ClinicalTrial nodes + links to existing conditions/medications
        neo4j_add_research_article,
        neo4j_add_clinical_trial,
        neo4j_link_article_to_condition,
        neo4j_bulk_link_articles_to_conditions,
        neo4j_create_custom_relationship,  # For article→medication links
        neo4j_get_patient_overview,
        neo4j_find_related_research,
        neo4j_export_graph_summary,
        neo4j_analyze_graph_connectivity,
        neo4j_list_all_patients,
    ]
)

root_agent = knowledge_graph_agent

if __name__ == "__main__":
    print(f"Enricher Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
