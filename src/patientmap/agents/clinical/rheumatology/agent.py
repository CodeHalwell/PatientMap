"""
Rheumatology Specialist Agent - Board-certified rheumatologist for autoimmune and rheumatic disease assessment
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(src_path))
from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.tools.research_tools import google_scholar_tool, pubmed_tool, semantic_scholar_tool, wikipedia_tool
from patientmap.common.helper_functions import retry_config, handle_tool_error

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".profiles" / "clinical" / "rheumatology_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    rheumatology_settings = config
except (FileNotFoundError) as e:
    raise FileNotFoundError(f"Configuration file not found at {config_path}") from e
finally:
    sys.path.pop(0)


# Create agent
rheumatology_agent = Agent(
    name=rheumatology_settings.agent_name,
    description=rheumatology_settings.description,
    model=Gemini(model_name=rheumatology_settings.model, retry_options=retry_config),
    instruction=rheumatology_settings.instruction,
    tools=[pubmed_tool(), google_scholar_tool(), semantic_scholar_tool(), wikipedia_tool()],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(rheumatology_agent)
