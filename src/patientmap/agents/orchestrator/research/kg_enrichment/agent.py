"""
KG Enrichment Loop - Enriches knowledge graph with research findings.
Loop agent that adds research data to graph and validates enrichment.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import transfer_to_agent, ToolContext

# Import enricher and checker sub-agents
from .enricher.agent import root_agent as knowledge_graph_agent
from .checker.agent import root_agent as enrichment_checker

from pathlib import Path

from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import handle_tool_error
from patientmap.tools.tool_registry import get_tools_from_config
current_dir = Path(__file__).parent

try:
    kg_enrichment_loop_config = AgentConfig(str(current_dir / "kg_enrichment_loop_agent.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError("kg_enrichment_loop_agent.yaml configuration file not found")

# Load tools from registry
agent_tools = get_tools_from_config(kg_enrichment_loop_config.tools)

enrichment_loop = LoopAgent(
    name="kg_enrichment_loop",
    description="An agent that enriches the knowledge graph with research findings and validates the enrichment.",
    sub_agents=[knowledge_graph_agent, enrichment_checker],
    max_iterations=3,
)

summary_agent = LlmAgent(
    name="kg_enrichment_summary_agent",
    description="Summarizes the results of the knowledge graph enrichment process.",
    model=kg_enrichment_loop_config.model,
    instruction="Summarize the key outcomes and findings from the knowledge graph enrichment process and call the transfer_to_agent tool to pass the summary to the clinical coordinator.",
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

knowledge_enrichment_loop = SequentialAgent(
    name=kg_enrichment_loop_config.agent_name,
    description=kg_enrichment_loop_config.description,
    sub_agents=[enrichment_loop, summary_agent],
)

root_agent = knowledge_enrichment_loop

if __name__ == "__main__":
    print(f"KG Enrichment Loop: {root_agent.name}")
