"""
Neurology Specialist Agent - Board-certified neurologist for neurological disease assessment
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
    neurology_settings = AgentConfig(str(current_dir / "neurology_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Neurology agent config not found at {current_dir / 'neurology_agent.yaml'}") from e

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(neurology_settings.tools)

# Create agent
neurology_agent = Agent(
    name=neurology_settings.agent_name,
    description=neurology_settings.description,
    model=Gemini(model_name=neurology_settings.model, retry_options=retry_config),
    instruction=neurology_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(neurology_agent)