"""
Clinical Agent - Coordinates clinical research, validation, and KG enrichment workflow.
Sequences: clinical analysis loop → knowledge graph enrichment
"""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LoopAgent, LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.helper_functions import retry_config

# Import manager, checker, and kg enrichment sub-agents
from .manager.agent import root_agent as clinical_manager
from .checker.agent import root_agent as checker_agent
from .kg_enrichment.agent import root_agent as clinical_kg_enrichment_agent
from patientmap.common.config import AgentConfig

current_dir = Path(__file__).parent

try:
    clinical_config = AgentConfig(str(current_dir / "clinical_coordinator.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Clinical agent config not found at {current_dir / 'clinical_coordinator.yaml'}")

# Clinical analysis loop (manager + checker)
clinical_loop_agent = LoopAgent(
    name="clinical_analysis_loop",
    description="Coordinates the clinical research and checking agents to ensure accurate and reliable clinical information.",
    sub_agents=[clinical_manager, checker_agent],
    max_iterations=3,
)

# Clinical coordinator that sequences analysis → KG enrichment
clinical_coordinator = LlmAgent(
    name=clinical_config.agent_name,
    description=clinical_config.description,
    model=Gemini(model_name=clinical_config.model, retry_options=retry_config),
    instruction=clinical_config.instruction,
    sub_agents=[clinical_loop_agent, clinical_kg_enrichment_agent],
)

root_agent = clinical_coordinator

if __name__ == "__main__":
    print(f"Clinical Coordinator: {root_agent.name}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
    print(f"  - Analysis loop iterations: {clinical_loop_agent.max_iterations}")
