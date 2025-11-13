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
    bulk_add_nodes,
    bulk_add_relationships,
    bulk_link_articles_to_conditions,
    analyze_graph_connectivity,
    check_node_completeness,
    bulk_check_node_completeness,
    export_graph_as_cytoscape_json,
    export_graph_summary,
    get_node_relationships,
    list_all_nodes_by_type,
    list_knowledge_graphs,
    load_graph_from_disk,
    save_graph_to_disk,
    validate_graph_structure,
    get_patient_overview,
    delete_node,
    delete_relationship,
    merge_duplicate_nodes,
)

from patientmap.common.helper_functions import retry_config
from google.adk.models.google_llm import Gemini

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
    model=Gemini(model_name=knowledge_graph_agent_settings.model, retry_options=retry_config),
    instruction=knowledge_graph_agent_settings.instruction,
    tools=[
        list_knowledge_graphs,
        load_graph_from_disk,
        bulk_add_nodes,
        bulk_add_relationships,
        bulk_link_articles_to_conditions,
        get_patient_overview,
        export_graph_summary,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        list_all_nodes_by_type,
        get_node_relationships,
        delete_node,
        delete_relationship,
        merge_duplicate_nodes,
    ]
)

# Create a separate instance of logic_checker for this loop
enrichment_checker = LlmAgent(
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