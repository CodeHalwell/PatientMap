from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk import Agent, Runner
from google.adk.agents import LoopAgent, LlmAgent
from google.adk.tools import exit_loop
from patientmap.common.config import AgentConfig
from patientmap.common.models import PatientRecord


# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "formatting_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_gatherer_agent_settings = config
except FileNotFoundError:
    raise RuntimeError("Data gatherer agent configuration file not found. Please create the file at '.profiles/formatting_agent.yaml'.")

# Create the iterative data gathering agent
format_agent = LlmAgent(
    name=data_gatherer_agent_settings.agent_name,
    description=data_gatherer_agent_settings.description,
    model=data_gatherer_agent_settings.model,
    instruction=data_gatherer_agent_settings.instruction,
    output_schema=PatientRecord,
)

if __name__ == "__main__":
    root_agent = format_agent
    print(root_agent)