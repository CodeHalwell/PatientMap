"""
Research Agent - Conducts literature and clinical research
"""

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
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "research_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    research_settings = config
except FileNotFoundError:
    # Fallback to default settings
    research_settings = type('obj', (object,), {
        'agent_name': 'researcher',
        'description': 'Conducts literature and clinical research',
        'model': 'gemini-2.5-flash',
        'instruction': 'You are a research agent that conducts thorough literature reviews.'
    })()

# Create agent
root_agent = Agent(
    name=research_settings.agent_name,
    description=research_settings.description,
    model=research_settings.model,
    instruction=research_settings.instruction,
    tools=[google_search]
)

if __name__ == "__main__":
    print(root_agent)