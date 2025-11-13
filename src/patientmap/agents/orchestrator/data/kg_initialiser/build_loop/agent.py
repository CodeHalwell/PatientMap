"""
Build Loop - Iterative knowledge graph construction and validation.
LoopAgent that builds graph, validates, provides feedback, and iterates.
"""

from __future__ import annotations

from google.adk.agents import LoopAgent

# Import builder and checker sub-agents
from .builder.agent import root_agent as build_agent
from .checker.agent import root_agent as logic_checker_agent

# Create loop agent
loop_agent = LoopAgent(
    name="Knowledge_graph_loop_agent",
    description=(
        "An agent that provides an iterative loop for building and validating the knowledge graph. "
        "The builder creates/updates the graph, then the checker validates and provides feedback. "
        "The loop continues until the checker is satisfied."
    ),
    sub_agents=[build_agent, logic_checker_agent],
    max_iterations=3,
)

root_agent = loop_agent

if __name__ == "__main__":
    print(f"Build Loop: {root_agent.name}")
    print(f"Max Iterations: {root_agent.max_iterations}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
