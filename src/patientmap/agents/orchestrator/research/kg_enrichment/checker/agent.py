"""
Enrichment Checker - Validates knowledge graph enrichment.
Checks structure, completeness, and clinical accuracy after enrichment.
"""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools import exit_loop
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.tools.neo4j_kg_tools import (
    neo4j_get_patient_overview,
    neo4j_find_related_research,
    neo4j_export_graph_summary,
    neo4j_analyze_graph_connectivity,
    neo4j_list_all_patients,
)
from patientmap.common.helper_functions import retry_config

current_dir = Path(__file__).parent

try:
    kg_checker_config = AgentConfig(str(current_dir / "kg_checker_agent.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"KG checker config not found at {current_dir / 'kg_checker_agent.yaml'}")

# Create a separate instance of logic_checker for this loop
enrichment_checker = LlmAgent(
    name=kg_checker_config.agent_name,
    description=kg_checker_config.description,
    model=Gemini(model_name=kg_checker_config.model, retry_options=retry_config),
    instruction=kg_checker_config.instruction,
    tools=[
        neo4j_get_patient_overview,
        neo4j_find_related_research,
        neo4j_export_graph_summary,
        neo4j_analyze_graph_connectivity,
        neo4j_list_all_patients,
        exit_loop,
    ],
)

root_agent = enrichment_checker

if __name__ == "__main__":
    print(f"Enrichment Checker: {root_agent.name}")
    print(f"Has exit_loop: {exit_loop in root_agent.tools}")
