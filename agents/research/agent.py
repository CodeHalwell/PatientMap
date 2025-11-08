import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.adk import Agent, Runner
from google.adk.tools import google_search
from common.config import AgentConfig

config_path = project_root / ".profiles" / "research_agent.yaml"
research_agent_settings = AgentConfig(str(config_path)).get_agent()

research_agent = Agent(
    name=research_agent_settings.agent_name,
    description=research_agent_settings.description,
    model=research_agent_settings.model,
    instruction=research_agent_settings.instruction,
    tools=[google_search],
)

print(research_agent)