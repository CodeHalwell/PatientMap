"""
Infectious Disease Specialist Agent - Board-certified infectious disease specialist for infectious disease assessment
"""

from __future__ import annotations
from pathlib import Path

from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config, handle_tool_error
from patientmap.tools.tool_registry import get_tools_from_config

current_dir = Path(__file__).parent

# Load configuration
try:
    infectious_disease_settings = AgentConfig(str(current_dir / "infectious_disease_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Infectious disease agent config not found at {current_dir / 'infectious_disease_agent.yaml'}") from e

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(infectious_disease_settings.tools)

# Create agent
infectious_disease_agent = Agent(
    name=infectious_disease_settings.agent_name,
    description=infectious_disease_settings.description,
    model=Gemini(model_name=infectious_disease_settings.model, retry_options=retry_config),
    instruction=infectious_disease_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(infectious_disease_agent)