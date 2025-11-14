"""
Cardiology Specialist Agent - Board-certified cardiologist for cardiovascular assessment
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(src_path))
from google.adk.models.google_llm import Gemini
from google.adk import Agent
from google.adk.tools import google_search, url_context, AgentTool
from patientmap.common.config import AgentConfig
from patientmap.tools.research_tools import google_scholar_tool, pubmed_tool, semantic_scholar_tool, wikipedia_tool
from patientmap.common.helper_functions import retry_config, handle_tool_error
from ....checker.agent import checker_agent

current_dir = Path(__file__).parent

try:
    config = AgentConfig(str(current_dir / "cardiology_agent.yaml")).get_agent()
    cardiology_settings = config
except (FileNotFoundError) as e:
    raise RuntimeError(f"Cardiology agent config not found at {current_dir / 'cardiology_agent.yaml'}") from e


# Create agent
cardiology_agent = Agent(
    name=cardiology_settings.agent_name,
    description=cardiology_settings.description,
    model=Gemini(model_name=cardiology_settings.model, retry_options=retry_config),
    instruction=cardiology_settings.instruction,
    tools=[pubmed_tool(), google_scholar_tool(), semantic_scholar_tool(), wikipedia_tool(), AgentTool(checker_agent)],
    on_tool_error_callback=handle_tool_error,
)


if __name__ == "__main__":
    print(cardiology_agent)