"""
Endocrinology Specialist Agent - Board-certified endocrinologist for metabolic disease assessment
"""

from __future__ import annotations


from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.tools.research_tools import google_scholar_tool, pubmed_tool, semantic_scholar_tool, wikipedia_tool
from patientmap.common.helper_functions import retry_config, handle_tool_error

try:
    config = AgentConfig("./endocrinology_agent.yaml").get_agent()
    endocrinology_settings = config
except (FileNotFoundError) as e:
    raise RuntimeError("Endocrinology agent config not found. Please ensure endocrinology_agent.yaml exists in the current directory.") from e

# Create agent
endocrinology_agent = Agent(
    name=endocrinology_settings.agent_name,
    description=endocrinology_settings.description,
    model=Gemini(model_name=endocrinology_settings.model, retry_options=retry_config),
    instruction=endocrinology_settings.instruction,
    tools=[pubmed_tool(), google_scholar_tool(), semantic_scholar_tool(), wikipedia_tool()],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(endocrinology_agent)