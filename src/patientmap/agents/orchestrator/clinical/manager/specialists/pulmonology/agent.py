"""
Pulmonology Specialist Agent - Board-certified pulmonologist for respiratory disease assessment
"""

from __future__ import annotations
from pathlib import Path

from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.tools.tool_registry import get_tools_from_config
from patientmap.common.helper_functions import retry_config, handle_tool_error

current_dir = Path(__file__).parent

# Load configuration
try:
    pulmonology_settings = AgentConfig(str(current_dir / "pulmonology_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Pulmonology agent config not found at {current_dir / 'pulmonology_agent.yaml'}") from e

# Load tools from registry
agent_tools = get_tools_from_config(pulmonology_settings.tools)

# Create agent
pulmonology_agent = Agent(
    name=pulmonology_settings.agent_name,
    description=pulmonology_settings.description,
    model=Gemini(model_name=pulmonology_settings.model, retry_options=retry_config),
    instruction=pulmonology_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(pulmonology_agent)
