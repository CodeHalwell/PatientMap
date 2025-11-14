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

# Load configuration from .profiles
current_dir = Path(__file__).parent

try:
    kg_init_config = AgentConfig(str(current_dir / "kg_planner.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Planning agent config not found at {current_dir / 'kg_planner.yaml'}")

# Create planning agent
planning_agent = LlmAgent(
    name=kg_init_config.agent_name,
    description=kg_init_config.description,
    model=Gemini(
        model_name=kg_init_config.model,
        retry_options=retry_config
    ),
    instruction=kg_init_config.instruction,
    output_key="kg_plan"
)

root_agent = planning_agent

if __name__ == "__main__":
    print(f"Planning Agent: {root_agent.name}")
