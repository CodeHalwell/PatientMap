from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from patientmap.common.config import AgentConfig


# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "formatting_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_gatherer_agent_settings = config
except FileNotFoundError:
    raise RuntimeError("Data gatherer agent configuration file not found. Please create the file at '.profiles/formatting_agent.yaml'.")



if __name__ == "__main__":
    print(root_agent)