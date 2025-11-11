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
    add_node,
    add_relationship,
    add_patient_condition,
    add_patient_medication,
    get_patient_overview,
    export_graph_summary,
    validate_graph_structure,
    check_node_completeness,
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
    description="An agent that plans the steps required to build and refine a knowledge graph based on patient data and clinical research findings.",
    model=kg_init_config.model,
    instruction="Plan the steps needed to build and refine the knowledge graph.",
    output_schema=KnowledgeGraph,
    output_key="kg_plan"
)


build_agent = LlmAgent(
    name=kg_init_config.agent_name,
    description=kg_init_config.description,
    model=kg_init_config.model,
    instruction=kg_init_config.instruction,
    tools=[
        initialize_patient_graph,
        add_node,
        add_relationship,
        add_patient_condition,
        add_patient_medication,
        delete_node,
        delete_relationship,
        merge_duplicate_nodes,
        get_patient_overview,
        export_graph_summary,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
    ],
)

logic_checker_agent = LlmAgent(
    name=kg_checker_config.agent_name,
    description=kg_checker_config.description,
    model=kg_checker_config.model,
    instruction=kg_checker_config.instruction,
    tools=[
        validate_graph_structure,
        check_node_completeness,
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
    max_iterations=5,
)

kg_initialiser_agent = SequentialAgent(
    name="Knowledge_graph_initialiser_agent",
    description="An agent that organises the building and validation of a clinical knowledge graph.",
    sub_agents=[planning_agent, loop_agent],
)

root_agent = kg_initialiser_agent

if __name__ == "__main__":
    root_agent = kg_initialiser_agent
    print(root_agent)