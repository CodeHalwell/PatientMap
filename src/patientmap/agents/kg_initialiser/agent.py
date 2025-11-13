from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk.agents import LoopAgent, LlmAgent, SequentialAgent
from google.adk.tools import exit_loop
from patientmap.common.config import AgentConfig
from patientmap.common.models import KnowledgeGraph
from patientmap.tools.kg_tools import (
    initialize_patient_graph,
    bulk_add_nodes,
    bulk_add_relationships,
    get_patient_overview,
    export_graph_summary,
    validate_graph_structure,
    check_node_completeness,
    bulk_check_node_completeness,
    analyze_graph_connectivity,
    list_all_nodes_by_type,
    get_node_relationships,
    save_graph_to_disk,
    load_graph_from_disk,
    export_graph_as_cytoscape_json,
    delete_node,
    delete_relationship,
    merge_duplicate_nodes,
)

from patientmap.common.helper_functions import retry_config
from google.adk.models.google_llm import Gemini

# Load configuration
kg_init_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "kg_initialiser.yaml"
kg_checker_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "kg_checker_agent.yaml"

try:
    kg_init_config = AgentConfig(str(kg_init_path)).get_agent()
    kg_checker_config = AgentConfig(str(kg_checker_path)).get_agent()
except FileNotFoundError:
    raise RuntimeError("KG initialiser agent configuration file not found. Please create the file at '.profiles/kg_initialiser.yaml'.")


planning_agent = LlmAgent(
    name="Knowledge_graph_planning_agent",
    description="An agent that extracts and plans the knowledge graph structure from actual patient data provided in context.",
    model=Gemini(model_name=kg_init_config.model, retry_options=retry_config),
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


build_agent = LlmAgent(
    name=kg_init_config.agent_name,
    description=kg_init_config.description,
    model=Gemini(model_name=kg_init_config.model, retry_options=retry_config),
    instruction=kg_init_config.instruction,
    tools=[
        initialize_patient_graph,
        bulk_add_nodes,
        bulk_add_relationships,
        delete_node,
        delete_relationship,
        merge_duplicate_nodes,
        get_patient_overview,
        export_graph_summary,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        validate_graph_structure,
    ],
)

logic_checker_agent = LlmAgent(
    name=kg_checker_config.agent_name,
    description=kg_checker_config.description,
    model=Gemini(model_name=kg_checker_config.model, retry_options=retry_config),
    instruction=kg_checker_config.instruction,
    tools=[
        validate_graph_structure,
        check_node_completeness,
        bulk_check_node_completeness,
        analyze_graph_connectivity,
        list_all_nodes_by_type,
        get_node_relationships,
        export_graph_summary,
        load_graph_from_disk,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        exit_loop,
    ],
)

loop_agent = LoopAgent(
    name="Knowledge_graph_loop_agent",
    description="An agent that provides an iterative loop for building and validating the knowledge graph. The builder creates/updates the graph, then the checker validates and provides feedback. The loop continues until the checker is satisfied.",
    sub_agents=[build_agent, logic_checker_agent],
    max_iterations=3,
)

kg_initialiser_agent = LlmAgent(
    name="Knowledge_graph_initialiser_agent",
    description="An agent that organises the building and validation of a clinical knowledge graph.",
    model=Gemini(model_name=kg_init_config.model, retry_options=retry_config),
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
    root_agent = kg_initialiser_agent
    print(root_agent)