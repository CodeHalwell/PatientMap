"""
Checker Agent - Validates knowledge graph structure and completeness.
Provides feedback to builder and calls exit_loop when satisfied.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.tool_registry import get_tools_from_config

# Load configuration from .profiles
current_dir = Path(__file__).parent
try:
    config = AgentConfig(str(current_dir / "kg_checker_agent.yaml")).get_agent()
    checker_settings = config
except FileNotFoundError:
    raise RuntimeError(f"Checker config not found at {current_dir / 'kg_checker_agent.yaml'}")

# Load tools from tool registry based on YAML config
agent_tools = get_tools_from_config(checker_settings.tools)

# Create logic checker agent
logic_checker_agent = LlmAgent(
    name=checker_settings.agent_name,
    description=checker_settings.description,
    model=Gemini(
        model_name=checker_settings.model,
        retry_options=retry_config
    ),
    instruction=checker_settings.instruction,
    tools=agent_tools,
)

root_agent = logic_checker_agent

if __name__ == "__main__":
    print(f"Checker Agent: {root_agent.name}")
