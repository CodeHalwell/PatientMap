from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk.agents import Agent
from patientmap.common.config import AgentConfig

from patientmap.agents.data_gatherer.agent import root_agent as data_agent
from patientmap.agents.kg_initialiser.agent import root_agent as kg_initialiser_agent

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "data" / "data_manager_agent.yaml"
try:
    config = AgentConfig(str(config_path)).get_agent()
    data_manager_agent_settings = config
except FileNotFoundError:
    raise RuntimeError("Data manager agent configuration file not found. Please create the file at '.profiles/data_manager_agent.yaml'.")

manager_agent = Agent(
    name=data_manager_agent_settings.agent_name,
    description=data_manager_agent_settings.description,
    model=data_manager_agent_settings.model,
    instruction=data_manager_agent_settings.instruction,
    sub_agents=[data_agent, kg_initialiser_agent]
)

root_agent = manager_agent

if __name__ == "__main__":
    print(root_agent)