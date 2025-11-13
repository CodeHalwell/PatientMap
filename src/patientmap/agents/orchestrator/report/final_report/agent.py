from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for imports (needed when loaded by ADK server)
src_path = Path(__file__).parent.parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

report_agent_config_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent / ".profiles" / "review" / "final_report_agent.yaml"

try:
    report_agent_config = AgentConfig(str(report_agent_config_path)).get_agent()
except FileNotFoundError as e:
    raise RuntimeError(f"Report agent configuration file not found: {e.filename}") from e

report_agent = LlmAgent(
    name=report_agent_config.agent_name,
    description=report_agent_config.description,
    model=Gemini(model_name=report_agent_config.model, retry_options=retry_config),
    instruction=report_agent_config.instruction,
    tools=[],
)

root_agent = report_agent

if __name__ == "__main__":
    print(f"Final Report Agent: {root_agent.name}")
    print(f"Sub-agents: {[agent.name for agent in root_agent.sub_agents]}")