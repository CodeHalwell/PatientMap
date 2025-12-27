"""
Physical Medicine Rehabilitation Specialist Agent - Board-certified PM&R specialist for functional restoration assessment
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
    pmr_settings = AgentConfig(str(current_dir / "physical_medicine_rehabilitation_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Physical Medicine Rehabilitation agent config not found at {current_dir / 'physical_medicine_rehabilitation_agent.yaml'}") from e

# Load tools from registry
agent_tools = get_tools_from_config(pmr_settings.tools)

# Create agent
physical_agent = Agent(
    name=pmr_settings.agent_name,
    description=pmr_settings.description,
    model=Gemini(model_name=pmr_settings.model, retry_options=retry_config),
    instruction=pmr_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(physical_agent)