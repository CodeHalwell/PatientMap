"""
Clinical Researcher Agent - Researches medical conditions and clinical evidence
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
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "clinical_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    clinical_settings = config
except FileNotFoundError:
    # Fallback to default settings
    clinical_settings = type('obj', (object,), {
        'agent_name': 'clinical_researcher',
        'description': 'Researches medical conditions and clinical evidence',
        'model': 'gemini-2.5-flash',
        'instruction': """You are a clinical researcher specializing in medical literature analysis.
        Your role is to research medical conditions, analyze peer-reviewed evidence,
        and synthesize clinical findings into actionable insights."""
    })()

# Create agent
root_agent = Agent(
    name=clinical_settings.agent_name,
    description=clinical_settings.description,
    model=clinical_settings.model,
    instruction=clinical_settings.instruction,
    tools=[google_search]
)

if __name__ == "__main__":
    print(root_agent)