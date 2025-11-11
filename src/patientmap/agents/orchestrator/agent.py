"""
Orchestrator Agent - Coordinates clinical research across multiple specialized agents
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk import Agent
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from patientmap.common.config import AgentConfig

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "orchestrator_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    orchestrator_settings = config
except FileNotFoundError:
    raise RuntimeError("Orchestrator agent configuration file not found. Please create the file at '.profiles/orchestrator_agent.yaml'.")

# Create root agent
root_agent = Agent(
    name=orchestrator_settings.agent_name,
    description=orchestrator_settings.description,
    model=orchestrator_settings.model,
    instruction=orchestrator_settings.instruction,
    tools=[google_search]
)





if __name__ == "__main__":
    print(root_agent)