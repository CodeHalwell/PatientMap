"""
Data Gatherer Agent - Conducts empathetic patient triage and information collection.
Collects comprehensive patient information through structured interview.
"""

from __future__ import annotations

import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.tool_registry import get_tools_from_config

# Get the directory where this file is located
current_dir = Path(__file__).parent

try:
    config = AgentConfig(str(current_dir / "data_gatherer_agent.yaml")).get_agent()
    data_gatherer_agent_settings = config
except FileNotFoundError:
    raise FileNotFoundError(f"Configuration file not found at {current_dir / 'data_gatherer_agent.yaml'}")

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(data_gatherer_agent_settings.tools)

# Create the data gathering agent
data_agent = LlmAgent(
    name=data_gatherer_agent_settings.agent_name,
    description=data_gatherer_agent_settings.description,
    model=Gemini(
        model_name=data_gatherer_agent_settings.model,
        retry_options=retry_config
    ),
    instruction=data_gatherer_agent_settings.instruction,
    tools=agent_tools,
)

root_agent = data_agent

if __name__ == "__main__":
    print(f"Data Gatherer Agent: {root_agent.name}")
