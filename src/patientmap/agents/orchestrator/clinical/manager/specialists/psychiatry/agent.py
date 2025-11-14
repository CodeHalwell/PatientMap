"""
Psychiatry Specialist Agent - Board-certified psychiatrist for mental health assessment
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

# Load configuration
try:
    psychiatry_settings = AgentConfig(str(current_dir / "psychiatry_agent.yaml")).get_agent()
except (FileNotFoundError) as e:
    raise RuntimeError(f"Psychiatry agent config not found at {current_dir / 'psychiatry_agent.yaml'}") from e


# Create agent
psychiatry_agent = Agent(
    name=psychiatry_settings.agent_name,
    description=psychiatry_settings.description,
    model=Gemini(model_name=psychiatry_settings.model, retry_options=retry_config),
    instruction=psychiatry_settings.instruction,
    tools=[pubmed_tool(), google_scholar_tool(), semantic_scholar_tool(), wikipedia_tool(), AgentTool(checker_agent)],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(psychiatry_agent)