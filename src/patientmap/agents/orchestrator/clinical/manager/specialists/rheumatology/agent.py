"""
Rheumatology Specialist Agent - Board-certified rheumatologist for autoimmune and rheumatic disease assessment
"""

from __future__ import annotations

from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.tools.research_tools import google_scholar_tool, pubmed_tool, semantic_scholar_tool, wikipedia_tool
from patientmap.common.helper_functions import retry_config, handle_tool_error

# Load configuration
try:
    rheumatology_settings = AgentConfig("./rheumatology_agent.yaml").get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError("Rheumatology agent config not found. Please ensure rheumatology_agent.yaml exists in the current directory.") from e

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
