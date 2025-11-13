from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk.agents import LlmAgent
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from google.adk.models.google_llm import Gemini

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "data" / "data_gatherer_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_gatherer_agent_settings = config
except FileNotFoundError:
    raise FileNotFoundError(f"Configuration file not found at {config_path}")


# Create the data gathering agent (no tools needed - just conversation)
data_agent = LlmAgent(
    name=data_gatherer_agent_settings.agent_name,
    description=data_gatherer_agent_settings.description,
    model=Gemini(model_name=data_gatherer_agent_settings.model, retry_options=retry_config),
    instruction=data_gatherer_agent_settings.instruction,
    tools=[],
)

root_agent = data_agent

if __name__ == "__main__":
    print(root_agent)