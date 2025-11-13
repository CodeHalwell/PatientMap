"""
Data Manager Agent - Coordinates patient data collection and knowledge graph initialization.
Part of Phase 1 of the PatientMap workflow.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Import sub-agents using relative imports
from .gatherer.agent import root_agent as data_gatherer_agent
from .kg_initialiser.agent import root_agent as kg_initialiser_agent

# Load configuration from .profiles (maintain existing location for now)
config_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".profiles" / "data" / "data_manager_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_manager_agent_settings = config
except FileNotFoundError:
    raise RuntimeError(
        f"Data manager agent configuration file not found at {config_path}. "
        "Please ensure data_manager_agent.yaml exists in .profiles/data/"
    )

# Create data manager agent
manager_agent = LlmAgent(
    name=data_manager_agent_settings.agent_name,
    description=data_manager_agent_settings.description,
    model=Gemini(
        model_name=data_manager_agent_settings.model,
        retry_options=retry_config
    ),
    instruction=data_manager_agent_settings.instruction,
    sub_agents=[data_gatherer_agent, kg_initialiser_agent],
)

# Export as root_agent for consistency
root_agent = manager_agent

if __name__ == "__main__":
    print(f"Data Manager Agent: {root_agent.name}")
    print(f"Sub-agents: {[agent.name for agent in root_agent.sub_agents]}")
