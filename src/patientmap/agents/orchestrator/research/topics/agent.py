"""
Research Topics Agent - Generates research topics from patient data.
Identifies key clinical areas requiring literature review.
"""

from __future__ import annotations

from pathlib import Path

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.tool_registry import get_tools_from_config

current_dir = Path(__file__).parent

try:
    topics_config = AgentConfig(str(current_dir / "research_topics.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Research topics config not found at {current_dir / 'research_topics.yaml'}")

agent_tools = get_tools_from_config(topics_config.tools)

research_topics = Agent(
    name=topics_config.agent_name,
    description=topics_config.description,
    model=Gemini(model_name=topics_config.model, retry_options=retry_config),
    instruction=topics_config.instruction,
    output_key="research_topics_list",
    tools=agent_tools,
)

root_agent = research_topics

if __name__ == "__main__":
    print(f"Research Topics Agent: {root_agent.name}")
