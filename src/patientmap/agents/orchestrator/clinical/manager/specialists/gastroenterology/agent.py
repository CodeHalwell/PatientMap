"""
Gastroenterology Specialist Agent - Board-certified gastroenterologist for digestive disease assessment
"""

from __future__ import annotations
from pathlib import Path

from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config, handle_tool_error
from patientmap.tools.tool_registry import get_tools_from_config

current_dir = Path(__file__).parent

try:
    config = AgentConfig(str(current_dir / "gastroenterology_agent.yaml")).get_agent()
    gastroenterology_settings = config
except (FileNotFoundError) as e:
    raise RuntimeError(f"Gastroenterology agent config not found at {current_dir / 'gastroenterology_agent.yaml'}") from e

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(gastroenterology_settings.tools)

# Create agent
gastroenterology_agent = Agent(
    name=gastroenterology_settings.agent_name,
    description=gastroenterology_settings.description,
    model=Gemini(model_name=gastroenterology_settings.model, retry_options=retry_config),
    instruction=gastroenterology_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(gastroenterology_agent)