"""
Nephrology Specialist Agent - Board-certified nephrologist for kidney disease assessment
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
    nephrology_settings = AgentConfig(str(current_dir / "nephrology_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Nephrology agent config not found at {current_dir / 'nephrology_agent.yaml'}") from e

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(nephrology_settings.tools)

# Create agent
nephrology_agent = Agent(
    name=nephrology_settings.agent_name,
    description=nephrology_settings.description,
    model=Gemini(model_name=nephrology_settings.model, retry_options=retry_config),
    instruction=nephrology_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(nephrology_agent)