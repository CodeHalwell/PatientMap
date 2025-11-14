"""
Research Agent - Coordinates literature and clinical research workflow.
Orchestrates topic generation → literature search → KG enrichment.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.helper_functions import retry_config

# Import sub-agents using relative imports
from .topics.agent import root_agent as research_topics_agent
from .search_loop.agent import root_agent as research_loop_agent
from .kg_enrichment.agent import root_agent as kg_enrichment_agent

# Create research coordinator
root_agent = LlmAgent(
    name="research_root_agent",
    description="Coordinates research by identifying topics, conducting literature reviews, and enriching the knowledge graph.",
    model=Gemini(model_name='gemini-2.5-pro', retry_options=retry_config),
    instruction="""Execute these steps in order:

1. Generate research topics from patient data
2. Conduct literature reviews for each topic
3. Integrate findings into the knowledge graph

Detect completion of each step and proceed to the next automatically.

Wait for each step to complete before proceeding to the next.

Detect completion of each step and proceed to the next automatically, notifying
  the user briefly at each transition.""",
    sub_agents=[research_topics_agent, research_loop_agent, kg_enrichment_agent],
)

if __name__ == "__main__":
    print(f"Research Root Agent: {root_agent.name}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
