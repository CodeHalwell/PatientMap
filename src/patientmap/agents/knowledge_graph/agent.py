from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk import Agent
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import exit_loop
from patientmap.common.config import AgentConfig
from patientmap.tools.kg_tools import (
    add_clinical_trial,
    add_node,
    add_patient_condition,
    add_patient_medication,
    add_research_article,
    add_relationship,
    analyze_graph_connectivity,
    check_node_completeness,
    export_graph_as_cytoscape_json,
    export_graph_summary,
    get_node_relationships,
    list_all_nodes_by_type,
    list_knowledge_graphs,
    load_graph_from_disk,
    save_graph_to_disk,
    validate_graph_structure,
    get_patient_overview,
    link_article_to_condition,
    delete_node,
    delete_relationship,
    merge_duplicate_nodes,
)

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "knowledge_graph_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    knowledge_graph_agent_settings = config
except FileNotFoundError:
    raise RuntimeError("Knowledge Graph agent configuration file not found. Please create the file at '.profiles/knowledge/knowledge_graph_agent.yaml'.")

# Load logic checker configuration
kg_checker_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "kg_checker_agent.yaml"

try:
    kg_checker_config = AgentConfig(str(kg_checker_path)).get_agent()
except FileNotFoundError:
    raise RuntimeError("KG checker agent configuration file not found.")

knowledge_graph_agent = Agent(
    name=knowledge_graph_agent_settings.agent_name,
    description=knowledge_graph_agent_settings.description,
    model=knowledge_graph_agent_settings.model,
    instruction=knowledge_graph_agent_settings.instruction,
    tools=[
        list_knowledge_graphs,
        load_graph_from_disk,
        add_node,
        add_relationship,
        add_patient_condition,
        add_patient_medication,
        add_research_article,
        link_article_to_condition,
        add_clinical_trial,
        get_patient_overview,
        export_graph_summary,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        validate_graph_structure,
        list_all_nodes_by_type,
        get_node_relationships,
        delete_node,
        delete_relationship,
        merge_duplicate_nodes,
        check_node_completeness,
        analyze_graph_connectivity,
    ]
)

# Create a separate instance of logic_checker for this loop
enrichment_checker = LlmAgent(
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
        exit_loop,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
    ],
)

knowledge_enrichment_loop = LoopAgent(
    name="knowledge_enrichment_loop",
    description="Agent that enriches the patient knowledge graph with research findings, then validates the enrichment for accuracy and completeness.",
    sub_agents=[knowledge_graph_agent, enrichment_checker],
    max_iterations=5,
)

root_agent = knowledge_enrichment_loop

if __name__ == "__main__":
    print(root_agent)