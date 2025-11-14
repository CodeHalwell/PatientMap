"""
Hematology Specialist Agent - Board-certified hematologist for blood disorders assessment
"""

from __future__ import annotations
from pathlib import Path

from google.adk.models.google_llm import Gemini
from google.adk import Agent
from google.adk.tools import AgentTool
from patientmap.common.config import AgentConfig
from patientmap.tools.research_tools import google_scholar_tool, pubmed_tool, semantic_scholar_tool, wikipedia_tool
from patientmap.common.helper_functions import retry_config, handle_tool_error
from patientmap.agents.orchestrator.clinical.checker.agent import checker_agent

current_dir = Path(__file__).parent

try:
    hematology_settings = AgentConfig(str(current_dir / "hematology_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Hematology agent config not found at {current_dir / 'hematology_agent.yaml'}") from e

# Create agent
hematology_agent = Agent(
    name=hematology_settings.agent_name,
    description=hematology_settings.description,
    model=Gemini(model_name=hematology_settings.model, retry_options=retry_config),
    instruction=hematology_settings.instruction,
    tools=[pubmed_tool(), google_scholar_tool(), semantic_scholar_tool(), wikipedia_tool(), AgentTool(checker_agent)],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(hematology_agent)