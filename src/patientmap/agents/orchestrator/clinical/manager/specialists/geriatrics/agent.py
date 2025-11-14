"""
Geriatrics Specialist Agent - Board-certified geriatrician for elderly care assessment
"""

from __future__ import annotations


from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.tools.research_tools import google_scholar_tool, pubmed_tool, semantic_scholar_tool, wikipedia_tool
from patientmap.common.helper_functions import retry_config, handle_tool_error

# Load configuration
try:
    config = AgentConfig("./geriatrics_agent.yaml").get_agent()
    geriatrics_settings = config
except (FileNotFoundError) as e:
    raise RuntimeError("Geriatrics agent config not found. Please ensure geriatrics_agent.yaml exists in the current directory.") from e


# Create agent
geriatrics_agent = Agent(
    name=geriatrics_settings.agent_name,
    description=geriatrics_settings.description,
    model=Gemini(model_name=geriatrics_settings.model, retry_options=retry_config),
    instruction=geriatrics_settings.instruction,
    tools=[pubmed_tool(), google_scholar_tool(), semantic_scholar_tool(), wikipedia_tool()],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(geriatrics_agent)