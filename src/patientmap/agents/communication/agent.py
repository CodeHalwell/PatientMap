from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk import Agent, Runner
from google.adk.tools import google_search
from patientmap.common.config import AgentConfig

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "communication_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    communication_agent_settings = config
except FileNotFoundError:
    raise RuntimeError("Communication agent configuration file not found. Please create the file at '.profiles/communication_agent.yaml'.")