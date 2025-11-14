"""
Nutrition Dietetics Specialist Agent - Board-certified dietitian nutritionist for medical nutrition therapy assessment
"""

from __future__ import annotations

from google.adk.models.google_llm import Gemini
from google.adk import Agent
from patientmap.common.config import AgentConfig
from patientmap.tools.research_tools import google_scholar_tool, pubmed_tool, semantic_scholar_tool, wikipedia_tool
from patientmap.common.helper_functions import retry_config, handle_tool_error

# Load configuration
try:
    nutrition_settings = AgentConfig("./nutrition_dietetics_agent.yaml").get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError("Nutrition Dietetics agent config not found. Please ensure nutrition_dietetics_agent.yaml exists in the current directory.") from e


# Create agent
nutrition_agent = Agent(
    name=nutrition_settings.agent_name,
    description=nutrition_settings.description,
    model=Gemini(model_name=nutrition_settings.model, retry_options=retry_config),
    instruction=nutrition_settings.instruction,
    tools=[pubmed_tool(), google_scholar_tool(), semantic_scholar_tool(), wikipedia_tool()],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(nutrition_agent)