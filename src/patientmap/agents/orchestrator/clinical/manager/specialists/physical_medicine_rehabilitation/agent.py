"""
Physical Medicine Rehabilitation Specialist Agent - Board-certified PM&R specialist for functional restoration assessment
"""

from __future__ import annotations

from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.tools.research_tools import google_scholar_tool, pubmed_tool, semantic_scholar_tool, wikipedia_tool
from patientmap.common.helper_functions import retry_config, handle_tool_error

# Load configuration
try:
    pmr_settings = AgentConfig("./physical_medicine_rehabilitation_agent.yaml").get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError("Physical Medicine Rehabilitation agent config not found. Please ensure physical_medicine_rehabilitation_agent.yaml exists in the current directory.") from e


# Create agent
physical_agent = Agent(
    name=pmr_settings.agent_name,
    description=pmr_settings.description,
    model=Gemini(model_name=pmr_settings.model, retry_options=retry_config),
    instruction=pmr_settings.instruction,
    tools=[pubmed_tool(), google_scholar_tool(), semantic_scholar_tool(), wikipedia_tool()],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(physical_agent)