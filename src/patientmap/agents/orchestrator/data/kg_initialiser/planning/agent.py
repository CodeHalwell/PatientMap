"""
Planning Agent - Analyzes patient data and creates comprehensive KG plan.
Extracts entities, relationships, and structure from patient narrative.
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
    kg_init_config = AgentConfig(str(current_dir / "kg_planner.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Planning agent config not found at {current_dir / 'kg_planner.yaml'}")

agent_tools = get_tools_from_config(kg_init_config.tools)

# Create planning agent
planning_agent = LlmAgent(
    name=kg_init_config.agent_name,
    description=kg_init_config.description,
    model=Gemini(
        model_name=kg_init_config.model,
        retry_options=retry_config
    ),
    instruction=kg_init_config.instruction,
    output_key="kg_plan",
    tools=agent_tools,
)

root_agent = planning_agent

if __name__ == "__main__":
    print(f"Planning Agent: {root_agent.name}")
