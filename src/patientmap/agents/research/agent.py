"""
Research Agent - Conducts literature and clinical research
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk import Agent
from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.tools import google_search, url_context
from patientmap.common.config import AgentConfig
from patientmap.agents.knowledge_graph.agent import root_agent as kg_agent

# Load configuration
researcher_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "research" / "research_agent.yaml"
topics_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "research" / "research_topics.yaml"

try:
    researcher_config = AgentConfig(str(researcher_path)).get_agent()
    topics_config = AgentConfig(str(topics_path)).get_agent()
except FileNotFoundError:
    raise RuntimeError("Research agent configuration file not found. Please create the file at '.profiles/research/research_agent.yaml'.")


research_topics = Agent(
    name=topics_config.agent_name,
    description=topics_config.description,
    model=topics_config.model,
    instruction=topics_config.instruction,
    output_key="research_topics_list",
)


research_agent = Agent(
    name=researcher_config.agent_name,
    description=researcher_config.description,
    model=researcher_config.model,
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

root_agent = SequentialAgent(
    name="research_root_agent",
    description="An agent that coordinates the research process by first identifying topics and then conducting literature reviews.",
    sub_agents=[research_topics, research_loop_agent, kg_agent],
)

if __name__ == "__main__":
    print(root_agent)