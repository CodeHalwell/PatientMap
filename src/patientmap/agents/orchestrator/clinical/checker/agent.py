"""
Clinical Checker Agent - Validates clinical responses for accuracy and reliability.
Verifies responses from clinical manager using google_search and url_context tools.
"""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.helper_functions import retry_config, handle_tool_error
from patientmap.common.config import AgentConfig
from patientmap.tools.tool_registry import get_tools_from_config

current_dir = Path(__file__).parent

try:
    config = AgentConfig(str(current_dir / "clinical_checker_agent.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Clinical checker agent config not found at {current_dir / 'clinical_checker_agent.yaml'}")

# Load tools from tool registry based on YAML config
agent_tools = get_tools_from_config(config.tools)

checker_agent = LlmAgent(
    name=config.agent_name,
    description=config.description,
    model=Gemini(model_name=config.model, retry_options=retry_config),
    instruction=config.instruction,
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

root_agent = checker_agent

if __name__ == "__main__":
    print(f"Clinical Checker: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
