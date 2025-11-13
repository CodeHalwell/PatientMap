from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk import Agent
from google.adk.tools import google_search
from patientmap.common.config import AgentConfig

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "data_extraction_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_extraction_agent_settings = config
except FileNotFoundError:
    # Fallback to default settings if config file not found
    data_extraction_agent_settings = type('obj', (object,), {
        'agent_name': 'data_extraction',
        'description': 'Agent that extracts relevant data from clinical sources',
        'model': 'gemini-2.5-flash',
        'instruction': 'You are a data extraction agent specializing in clinical information retrieval.'
    })()

root_agent = Agent(
    name=data_extraction_agent_settings.agent_name,
    description=data_extraction_agent_settings.description,
    model=data_extraction_agent_settings.model,
    instruction=data_extraction_agent_settings.instruction,
    tools=[google_search]
)

if __name__ == "__main__":
    print(root_agent)