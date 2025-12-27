"""
Research Agent - Coordinates literature and clinical research workflow.
Orchestrates topic generation → literature search → KG enrichment.
Uses deterministic SequentialAgent for reliable phase transitions.
"""

from __future__ import annotations

from google.adk.agents import SequentialAgent, LlmAgent

from pathlib import Path

current_dir = Path(__file__).parent

# Import sub-agents using relative imports
from .topics.agent import root_agent as research_topics_agent
from .search_loop.agent import root_agent as research_loop_agent
from .kg_enrichment.agent import root_agent as kg_enrichment_agent

transfer_agent = LlmAgent(
    name="research_transfer_agent",
    description="Transfers research findings to the clinical coordinator for further action.",
    model="gemini-2.5-flash",
    instruction="Transfer the compiled research findings and transfer to the orchestrator by calling the transfer_to_agent tool.",
    sub_agents=[],
)

root_agent = SequentialAgent(
    name="research_manager_agent",
    description=(
        "Coordinates research workflow with deterministic phase transitions. "
        "Executes: (1) topic generation, (2) iterative literature search with review, "
        "(3) knowledge graph enrichment with findings."
    ),
    sub_agents=[research_topics_agent, research_loop_agent, kg_enrichment_agent, transfer_agent],
)

if __name__ == "__main__":
    print(f"Research Root Agent: {root_agent.name}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
