import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from __future__ import annotations

from google.adk import Agent, Runner
from common.config import AgentConfig

config_path = project_root / ".profiles" / "data_gatherer_agent.yaml"
data_gatherer_agent_settings = AgentConfig(str(config_path)).get_agent()