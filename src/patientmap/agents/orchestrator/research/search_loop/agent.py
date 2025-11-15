"""
Search Loop Agent - Conducts iterative literature searches.
Uses google_search and url_context tools to gather clinical evidence.
"""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.agents import LoopAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.tool_registry import get_tools_from_config

current_dir = Path(__file__).parent

try:
    researcher_config = AgentConfig(str(current_dir / "research_agent.yaml")).get_agent()
    reviewer_agent_config = AgentConfig(str(current_dir / "reviewer_agent.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Research agent config not found at {current_dir / 'research_agent.yaml'}")

# Load tools from central tool registry based on YAML configs
research_tools = get_tools_from_config(researcher_config.tools)
reviewer_tools = get_tools_from_config(reviewer_agent_config.tools)

research_agent = LlmAgent(
    name=researcher_config.agent_name,
    description=researcher_config.description,
    model=Gemini(model_name=researcher_config.model, retry_options=retry_config),
    instruction=f"{researcher_config.instruction}\n\nResearch topics to investigate: {{research_topics_list}}",
    tools=research_tools,
    output_key="research_findings"
)

reviewer_agent = LlmAgent(
    name=reviewer_agent_config.agent_name,
    description=reviewer_agent_config.description,
    model=Gemini(model_name=reviewer_agent_config.model, retry_options=retry_config),
    instruction=f"{reviewer_agent_config.instruction}\n\nResearch findings to review: {{research_findings}}",
    tools=reviewer_tools,
)

research_loop_agent = LoopAgent(
    name="research_loop_agent",
    description="An agent that iteratively conducts detailed literature reviews to gather clinical evidence for all research topics.",
    sub_agents=[research_agent, reviewer_agent],
    max_iterations=5,
)

root_agent = research_loop_agent

if __name__ == "__main__":
    print(f"Research Loop Agent: {root_agent.name}")
    print(f"Max Iterations: {root_agent.max_iterations}")
