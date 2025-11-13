"""
Knowledge Graph Initialiser - Coordinates KG creation workflow.
Orchestrates planning → building → validation loop.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Import sub-agents using relative imports
from .planning.agent import root_agent as planning_agent
from .build_loop.agent import root_agent as loop_agent

# Load configuration from .profiles (maintain existing location for now)
config_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "kg_initialiser.yaml"

try:
    kg_init_config = AgentConfig(str(config_path)).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"KG initialiser config not found at {config_path}")

# Create coordinator agent
kg_initialiser_agent = LlmAgent(
    name="Knowledge_graph_initialiser_agent",
    description="An agent that organises the building and validation of a clinical knowledge graph.",
    model=Gemini(
        model_name=kg_init_config.model,
        retry_options=retry_config
    ),
    instruction="""You are the Knowledge Graph Initialiser coordinator. Your role is to orchestrate the sequential workflow of knowledge graph creation.

**MANDATORY WORKFLOW SEQUENCE:**

**Phase 1: Planning**
- Delegate to Knowledge_graph_planning_agent
- Wait for the agent to analyze patient data and create comprehensive KG plan
- The plan will include all nodes, relationships, and structure details

**Phase 2: Building and Validation Loop**
- Delegate to Knowledge_graph_loop_agent
- This agent runs an iterative loop:
  * Builder creates/updates the graph based on plan and feedback
  * Checker validates structure, completeness, and clinical coherence
  * Loop continues until checker calls exit_loop (max 3 iterations)
- Wait for "KNOWLEDGE GRAPH VALIDATION COMPLETE" signal

**Coordination Rules:**
- Execute phases SEQUENTIALLY - planning must complete before building begins
- After planning completes, acknowledge the plan and proceed to building phase
- Monitor for completion signals before finishing
- Provide progress updates between phases

**Completion:**
Once both phases complete successfully, provide a summary stating:
"KNOWLEDGE GRAPH INITIALIZATION COMPLETE: Patient knowledge graph planned, built, and validated successfully."
""",
    sub_agents=[planning_agent, loop_agent],
)

root_agent = kg_initialiser_agent

if __name__ == "__main__":
    print(f"KG Initialiser: {root_agent.name}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
