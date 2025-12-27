"""
Palliative Care Specialist Agent - Board-certified palliative care specialist for quality of life and symptom management assessment
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
    palliative_settings = AgentConfig(str(current_dir / "palliative_care_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Palliative Care agent config not found at {current_dir / 'palliative_care_agent.yaml'}") from e

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(palliative_settings.tools)

# Create agent
palliative_agent = Agent(
    name=palliative_settings.agent_name,
    description=palliative_settings.description,
    model=Gemini(model_name=palliative_settings.model, retry_options=retry_config),
    instruction=palliative_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(palliative_agent)