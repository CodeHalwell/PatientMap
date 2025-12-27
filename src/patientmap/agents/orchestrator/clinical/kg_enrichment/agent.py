"""
Clinical KG Enrichment Agent - Integrates clinical analysis into knowledge graph.
Adds clinical recommendations, specialist insights, and treatment plans to the patient KG.
"""

from __future__ import annotations

from pathlib import Path

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.tools.tool_registry import get_tools_from_config
from patientmap.common.helper_functions import retry_config

current_dir = Path(__file__).parent

# Load configuration from .profiles
try:
    config = AgentConfig(str(current_dir / "clinical_kg_enrichment_agent.yaml")).get_agent()
    settings = config
except FileNotFoundError:
    raise RuntimeError(f"Clinical KG enrichment config not found at {current_dir / 'clinical_kg_enrichment_agent.yaml'}")

# Load tools from tool registry based on YAML config
agent_tools = get_tools_from_config(settings.tools)

clinical_kg_enrichment_agent = Agent(
    name=settings.agent_name,
    description=settings.description,
    model=Gemini(model_name=settings.model, retry_options=retry_config),
    instruction=settings.instruction,
    tools=agent_tools
)

root_agent = clinical_kg_enrichment_agent

if __name__ == "__main__":
    print(f"Clinical KG Enrichment Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
