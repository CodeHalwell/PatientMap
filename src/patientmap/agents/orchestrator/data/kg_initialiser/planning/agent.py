"""
Planning Agent - Analyzes patient data and creates comprehensive KG plan.
Extracts entities, relationships, and structure from patient narrative.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Load configuration from .profiles
config_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "kg_initialiser.yaml"

try:
    kg_init_config = AgentConfig(str(config_path)).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Planning agent config not found at {config_path}")

# Create planning agent
planning_agent = LlmAgent(
    name="Knowledge_graph_planning_agent",
    description="An agent that extracts and plans the knowledge graph structure from actual patient data provided in context.",
    model=Gemini(
        model_name=kg_init_config.model,
        retry_options=retry_config
    ),
    instruction="""Analyze the patient data provided and create a comprehensive plan for the knowledge graph.

CRITICAL: Extract ACTUAL information from the patient narrative:
- Use the REAL patient name, demographics, and ID
- Extract ALL medical conditions mentioned (with ICD codes if available)
- Extract ALL medications with dosages and schedules
- Extract practitioners, organizations, procedures mentioned
- Identify key symptoms, lifestyle factors, and social determinants

Your plan should be structured with:
- **Patient Node**: ID, name, demographics
- **Condition Nodes**: Each with node_id, node_type="Condition", label, ICD code (properties)
- **Medication Nodes**: Each with node_id, node_type="Medication", label, dosage/schedule (properties)
- **Practitioner/Organization Nodes**: Each with appropriate type and properties
- **Relationships**: Clear source → relationship_type → target mappings

Provide a comprehensive, detailed plan that includes:
1. List all nodes to create (with IDs, types, labels, and key properties)
2. List all relationships to create (with source_id, target_id, relationship_type)
3. Brief description of the overall knowledge graph structure

Be thorough - include all relevant clinical information from the patient data.
Do NOT create generic examples like "John Doe" or "Patient 1" - use the ACTUAL patient information.

Output your plan in clear, structured text format that the builder agent can easily follow.""",
    output_key="kg_plan"
)

root_agent = planning_agent

if __name__ == "__main__":
    print(f"Planning Agent: {root_agent.name}")
