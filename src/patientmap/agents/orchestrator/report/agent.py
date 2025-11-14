from __future__ import annotations

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import handle_tool_error, retry_config
from .roundtable.agent import root_agent as reporting_agent
from .final_report.agent import root_agent as final_report_agent

try:
    report_manager_settings = AgentConfig("./report_manager_agent.yaml").get_agent()
except FileNotFoundError:
    raise RuntimeError(
        "Report manager agent config not found. Please ensure report_manager_agent.yaml exists in the current directory."
    )

root_agent = Agent(
    name=report_manager_settings.agent_name,
    description=report_manager_settings.description,
    model=Gemini(model_name=report_manager_settings.model, retry_options=retry_config),
    instruction=report_manager_settings.instruction,
    sub_agents=[reporting_agent, final_report_agent],
    tools=[],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(f"Report Agent: {root_agent.name}")