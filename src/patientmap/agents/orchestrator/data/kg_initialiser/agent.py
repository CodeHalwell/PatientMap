"""
Knowledge Graph Initialiser - Coordinates KG creation workflow.
Orchestrates planning → building → validation loop.
Uses deterministic SequentialAgent for reliable execution flow.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import SequentialAgent, LlmAgent
from patientmap.common.helper_functions import handle_tool_error

# Import sub-agents using relative imports
from .planning.agent import root_agent as planning_agent
from .build_loop.agent import root_agent as loop_agent

# Load configuration from local directory
current_dir = Path(__file__).parent

summary_agent = LlmAgent(
    name="summary_of_kg",
    description="Summarises the output from the knowldge graph building process.",
    model="gemini-2.5-flash",
    instruction="Summarise the output from the knowledge graph building process to report back to the data manager.",
    sub_agents=[],
    on_tool_error_callback=handle_tool_error,
)


# Use SequentialAgent for deterministic flow: planning → build loop
# This ensures planning always completes before the build/validation loop starts
kg_initialiser_agent = SequentialAgent(
    name="Knowledge_graph_initialiser_agent",
    description=(
        "Coordinates knowledge graph initialization workflow. "
        "First, planning agent creates the structure, then build loop iteratively "
        "constructs and validates the graph until checker is satisfied."
    ),
    sub_agents=[planning_agent, loop_agent, summary_agent],
)

root_agent = kg_initialiser_agent

if __name__ == "__main__":
    print(f"KG Initialiser: {root_agent.name}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
