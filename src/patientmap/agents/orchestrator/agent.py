"""
Orchestrator Agent - Coordinates clinical research across multiple specialized agents
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk import Agent
from google.adk.apps.app import App, EventsCompactionConfig

from patientmap.common.config import AgentConfig
from patientmap.agents.data_manager.agent import root_agent as data_manager_agent
from patientmap.agents.research.agent import root_agent as research_agent
from patientmap.agents.clinical.agent import root_agent as clinical_agent
from patientmap.common.helper_functions import retry_config
from google.adk.models.google_llm import Gemini

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "orchestrator_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    orchestrator_settings = config
except FileNotFoundError:
    raise RuntimeError("Orchestrator agent configuration file not found. Please create the file at '.profiles/orchestrator_agent.yaml'.")

# Create root agent
root_agent = Agent(
    name=orchestrator_settings.agent_name,
    description=orchestrator_settings.description,
    model=Gemini(model_name=orchestrator_settings.model, retry_options=retry_config),
    instruction=orchestrator_settings.instruction,
    sub_agents=[data_manager_agent, research_agent, clinical_agent],
)

if __name__ == "__main__":
    # For standalone testing
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.memory import InMemoryMemoryService
    
    app = App(
        name='orchestrator',
        root_agent=root_agent,
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=3,
            overlap_size=1
        ),
    )
    
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    
    runner = Runner(
        app=app,
        session_service=session_service,
        memory_service=memory_service,
    )
    
    runner.run_async(
        user_id="test_user",
        session_id="test_session"
    )