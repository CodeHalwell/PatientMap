"""
Data Gatherer Agent - Conducts empathetic patient triage and information collection.
Collects comprehensive patient information through structured interview.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Load configuration from .profiles (maintain existing location for now)
config_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent / ".profiles" / "data" / "data_gatherer_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_gatherer_agent_settings = config
except FileNotFoundError:
    raise FileNotFoundError(f"Configuration file not found at {config_path}")

# Create the data gathering agent (no tools needed - just conversation)
data_agent = LlmAgent(
    name=data_gatherer_agent_settings.agent_name,
    description=data_gatherer_agent_settings.description,
    model=Gemini(
        model_name=data_gatherer_agent_settings.model,
        retry_options=retry_config
    ),
    instruction=data_gatherer_agent_settings.instruction,
    tools=[],
)

root_agent = data_agent

if __name__ == "__main__":
    print(f"Data Gatherer Agent: {root_agent.name}")
