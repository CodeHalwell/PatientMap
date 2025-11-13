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
from google.adk.agents import LoopAgent, SequentialAgent, LlmAgent
from google.adk.tools import google_search, url_context
from patientmap.common.config import AgentConfig
from patientmap.agents.knowledge_graph.agent import root_agent as kg_agent
from patientmap.common.helper_functions import retry_config
from google.adk.models.google_llm import Gemini

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
    model=Gemini(model_name=topics_config.model, retry_options=retry_config),
    instruction=topics_config.instruction,
    output_key="research_topics_list",
)


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

root_agent = LlmAgent(
    name="research_root_agent",
    description="Coordinates research by identifying topics, conducting literature reviews, and enriching the knowledge graph.",
    model=Gemini(model_name='gemini-2.5-pro', retry_options=retry_config),
    instruction="""Execute these steps in order:

1. Generate research topics from patient data
2. Conduct literature reviews for each topic
3. Integrate findings into the knowledge graph

Detect completion of each step and proceed to the next automatically.

Wait for each step to complete before proceeding to the next.""",
    sub_agents=[research_topics, research_loop_agent, kg_agent],
)

if __name__ == "__main__":
    print(root_agent)