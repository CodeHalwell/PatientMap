"""
KG Enrichment Loop - Enriches knowledge graph with research findings.
Loop agent that adds research data to graph and validates enrichment.
"""

from __future__ import annotations

from google.adk.agents import LoopAgent

# Import enricher and checker sub-agents
from .enricher.agent import root_agent as knowledge_graph_agent
from .checker.agent import root_agent as enrichment_checker

knowledge_enrichment_loop = LoopAgent(
    name="knowledge_enrichment_loop",
    description="Agent that enriches the patient knowledge graph with research findings, then validates the enrichment for accuracy and completeness.",
    sub_agents=[knowledge_graph_agent, enrichment_checker],
    max_iterations=5,
)

root_agent = knowledge_enrichment_loop

if __name__ == "__main__":
    print(f"KG Enrichment Loop: {root_agent.name}")
    print(f"Max Iterations: {root_agent.max_iterations}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
