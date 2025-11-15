"""
Enricher Agent - Adds research findings to the knowledge graph.
Uses KG tools to load, enrich, and save the patient knowledge graph.
"""

from __future__ import annotations

from pathlib import Path

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.tools.tool_registry import get_tools_from_config
from patientmap.common.helper_functions import retry_config

current_dir = Path(__file__).parent

try:
    knowledge_graph_agent_settings = AgentConfig(str(current_dir / "knowledge_graph_agent.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(f"Knowledge Graph agent config not found at {current_dir / 'knowledge_graph_agent.yaml'}")

# Load tools from tool registry based on YAML config
agent_tools = get_tools_from_config(knowledge_graph_agent_settings.tools)

knowledge_graph_agent = Agent(
    name=knowledge_graph_agent_settings.agent_name,
    description=knowledge_graph_agent_settings.description,
    model=Gemini(model_name=knowledge_graph_agent_settings.model, retry_options=retry_config),
    instruction=knowledge_graph_agent_settings.instruction,
    tools=agent_tools
)

root_agent = knowledge_graph_agent

if __name__ == "__main__":
    print(f"Enricher Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
