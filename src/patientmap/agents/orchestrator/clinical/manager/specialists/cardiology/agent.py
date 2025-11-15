"""
Cardiology Specialist Agent - Board-certified cardiologist for cardiovascular assessment
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(src_path))
from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config, handle_tool_error
from patientmap.tools.tool_registry import get_tools_from_config

current_dir = Path(__file__).parent

try:
    config = AgentConfig(str(current_dir / "cardiology_agent.yaml")).get_agent()
    cardiology_settings = config
except (FileNotFoundError) as e:
    raise RuntimeError(f"Cardiology agent config not found at {current_dir / 'cardiology_agent.yaml'}") from e

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(cardiology_settings.tools)

# Create agent
cardiology_agent = Agent(
    name=cardiology_settings.agent_name,
    description=cardiology_settings.description,
    model=Gemini(model_name=cardiology_settings.model, retry_options=retry_config),
    instruction=cardiology_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)


if __name__ == "__main__":
    print(cardiology_agent)