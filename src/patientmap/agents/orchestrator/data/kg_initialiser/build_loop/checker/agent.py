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
from patientmap.tools.neo4j_kg_tools import (
    neo4j_get_patient_overview,
    neo4j_find_related_research,
    neo4j_export_graph_summary,
    neo4j_analyze_graph_connectivity,
    neo4j_list_all_patients,
)

# Load configuration from .profiles
current_dir = Path(__file__).parent
try:
    config = AgentConfig(str(current_dir / "kg_checker_agent.yaml")).get_agent()
    checker_settings = config
except FileNotFoundError:
    raise RuntimeError(f"Checker config not found at {current_dir / 'kg_checker_agent.yaml'}")

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
        neo4j_get_patient_overview,
        neo4j_find_related_research,
        neo4j_export_graph_summary,
        neo4j_analyze_graph_connectivity,
        neo4j_list_all_patients,
        exit_loop,  # Critical: allows checker to end loop
    ],
)

root_agent = logic_checker_agent

if __name__ == "__main__":
    print(f"Checker Agent: {root_agent.name}")
    print(f"Has exit_loop: {exit_loop in root_agent.tools}")
