"""
Search Loop Agent - Conducts iterative literature searches.
Uses google_search and url_context tools to gather clinical evidence.
"""

from __future__ import annotations
from pathlib import Path

from google.adk import Agent
from google.adk.agents import LoopAgent
from google.adk.tools import google_search, url_context
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Load configuration from .profiles
config_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent / ".profiles" / "research" / "research_agent.yaml"

try:
    researcher_config = AgentConfig(str(config_path)).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Research agent config not found at {config_path}")

research_agent = Agent(
    name=researcher_config.agent_name,
    description=researcher_config.description,
    model=Gemini(model_name=researcher_config.model, retry_options=retry_config),
    instruction=f"{researcher_config.instruction}\n\nResearch topics to investigate: {{research_topics_list}}",
    tools=[google_search, url_context],
    output_key="research_findings"
)

research_loop_agent = LoopAgent(
    name="research_loop_agent",
    description="An agent that iteratively conducts detailed literature reviews to gather clinical evidence for all research topics.",
    sub_agents=[research_agent],
    max_iterations=10,
)

root_agent = research_loop_agent

if __name__ == "__main__":
    print(f"Research Loop Agent: {root_agent.name}")
    print(f"Max Iterations: {root_agent.max_iterations}")
