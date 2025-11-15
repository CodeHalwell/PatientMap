from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import handle_tool_error, retry_config
from patientmap.tools.tool_registry import get_tools_from_config
from .roundtable.agent import root_agent as reporting_agent
from .final_report.agent import root_agent as final_report_agent

current_dir = Path(__file__).parent

try:
    report_manager_settings = AgentConfig(str(current_dir / "report_manager_agent.yaml")).get_agent()
except FileNotFoundError:
    raise RuntimeError(
        f"Report manager agent config not found at {current_dir / 'report_manager_agent.yaml'}"
    )

# Load tools from registry
agent_tools = get_tools_from_config(report_manager_settings.tools)

root_agent = LlmAgent(
    name=report_manager_settings.agent_name,
    description=report_manager_settings.description,
    model=Gemini(model_name=report_manager_settings.model, retry_options=retry_config),
    instruction=report_manager_settings.instruction,
    sub_agents=[reporting_agent, final_report_agent],
    tools=agent_tools,
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(f"Report Agent: {root_agent.name}")