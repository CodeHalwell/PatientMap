"""
Clinical Researcher Agent - Researches medical conditions and clinical evidence
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk import Agent, Runner
from google.adk.tools import google_search
from patientmap.common.config import AgentConfig

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "clinical_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    clinical_settings = config
except (FileNotFoundError) as e:
    raise FileNotFoundError(f"Configuration file not found at {config_path}") from e
finally:
    # Clean up sys.path
    sys.path.pop(0)

# Create agent
root_agent = Agent(
    name=clinical_settings.agent_name,
    description=clinical_settings.description,
    model=clinical_settings.model,
    instruction=clinical_settings.instruction,
    tools=[google_search]
)

# Create runner
runner = Runner(
    app="patientmap",
    app_name="patientmap",
    agent=root_agent)

# Run agent
runner.run()

if __name__ == "__main__":
    print(root_agent)