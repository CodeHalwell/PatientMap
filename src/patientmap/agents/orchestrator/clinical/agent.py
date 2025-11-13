"""
Clinical Agent - Coordinates clinical research, validation, and KG enrichment workflow.
Sequences: clinical analysis loop → knowledge graph enrichment
"""

from __future__ import annotations

from google.adk.agents import LoopAgent, LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.helper_functions import retry_config

# Import manager, checker, and kg enrichment sub-agents
from .manager.agent import root_agent as clinical_manager
from .checker.agent import root_agent as checker_agent
from .kg_enrichment.agent import root_agent as clinical_kg_enrichment_agent

# Clinical analysis loop (manager + checker)
clinical_loop_agent = LoopAgent(
    name="clinical_analysis_loop",
    description="Coordinates the clinical research and checking agents to ensure accurate and reliable clinical information.",
    sub_agents=[clinical_manager, checker_agent],
    max_iterations=3,
)

# Clinical coordinator that sequences analysis → KG enrichment
clinical_coordinator = LlmAgent(
    name="clinical_coordinator",
    description="Coordinates clinical workflow: analysis → validation → knowledge graph enrichment",
    model=Gemini(model_name='gemini-2.5-flash', retry_options=retry_config),
    instruction="""Execute these steps in order:

1. **Clinical Analysis**: Delegate to clinical_analysis_loop
   - Specialist consultations and recommendations
   - Clinical validation and accuracy checking
   - Wait for loop completion

2. **Knowledge Graph Integration**: Delegate to clinical_knowledge_graph_enrichment_agent
   - Integrate all clinical recommendations into patient knowledge graph
   - Add treatment plans, monitoring protocols, and clinical alerts
   - Save enriched graph to disk
   - Wait for completion message

Detect completion of each step and proceed to the next automatically.
Provide brief status updates between phases.""",
    sub_agents=[clinical_loop_agent, clinical_kg_enrichment_agent],
)

root_agent = clinical_coordinator

if __name__ == "__main__":
    print(f"Clinical Coordinator: {root_agent.name}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
    print(f"  - Analysis loop iterations: {clinical_loop_agent.max_iterations}")
