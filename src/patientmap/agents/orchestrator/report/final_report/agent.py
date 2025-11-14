from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

try:
    report_agent_config = AgentConfig("./final_report_agent.yaml").get_agent()
except FileNotFoundError as e:
    raise RuntimeError(f"Report agent configuration file not found: {e.filename}") from e

root_agent = LlmAgent(
    name=report_agent_config.agent_name,
    description=report_agent_config.description,
    model=Gemini(model_name=report_agent_config.model, retry_options=retry_config),
    instruction=report_agent_config.instruction,
    tools=[],
)

if __name__ == "__main__":
    print(f"Final Report Agent: {root_agent}")