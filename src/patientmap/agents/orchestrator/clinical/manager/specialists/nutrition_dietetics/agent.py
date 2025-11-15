"""
Nutrition Dietetics Specialist Agent - Board-certified dietitian nutritionist for medical nutrition therapy assessment
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
    nutrition_settings = AgentConfig(str(current_dir / "nutrition_dietetics_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Nutrition Dietetics agent config not found at {current_dir / 'nutrition_dietetics_agent.yaml'}") from e

# Load tools from tool registry based on YAML config (show_my_available_tools)
agent_tools = get_tools_from_config(nutrition_settings.tools)

# Create agent
nutrition_agent = Agent(
    name=nutrition_settings.agent_name,
    description=nutrition_settings.description,
    model=Gemini(model_name=nutrition_settings.model, retry_options=retry_config),
    instruction=nutrition_settings.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(nutrition_agent)