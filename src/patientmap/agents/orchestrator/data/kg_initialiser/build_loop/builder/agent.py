"""
Builder Agent - Creates and updates the patient knowledge graph.
Uses bulk operations to add nodes and relationships based on plan.
"""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.tool_registry import get_tools_from_config

current_dir = Path(__file__).parent

try:
    builder_settings = AgentConfig(str(current_dir / "kg_initialiser.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Builder config not found at {current_dir / 'kg_initialiser.yaml'}")

# Load tools from registry
agent_tools = get_tools_from_config(builder_settings.tools)

# Create builder agent with KG tools
build_agent = LlmAgent(
    name=builder_settings.agent_name,
    description=builder_settings.description,
    model=Gemini(
        model_name=builder_settings.model,
        retry_options=retry_config
    ),
    instruction=builder_settings.instruction,
    tools=agent_tools,
)

root_agent = build_agent

if __name__ == "__main__":
    print(f"Builder Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
