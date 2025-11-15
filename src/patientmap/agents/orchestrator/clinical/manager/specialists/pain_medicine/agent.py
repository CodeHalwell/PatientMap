"""
Pain Medicine Specialist Agent - Board-certified pain medicine specialist for pain management assessment
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
    pain_settings = AgentConfig(str(current_dir / "pain_medicine_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Pain Medicine agent config not found at {current_dir / 'pain_medicine_agent.yaml'}") from e

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(pain_settings.tools)

# Create agent
pain_agent = Agent(
    name=pain_settings.agent_name,
    description=pain_settings.description,
    model=Gemini(model_name=pain_settings.model, retry_options=retry_config),
    instruction=pain_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(pain_agent)