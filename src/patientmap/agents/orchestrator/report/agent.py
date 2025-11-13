from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for imports (needed when loaded by ADK server)
src_path = Path(__file__).parent.parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import handle_tool_error, retry_config
from patientmap.agents.orchestrator.report.roundtable.agent import root_agent as report_agent
from patientmap.agents.orchestrator.report.final_report.agent import root_agent as final_report_agent

report_manager_config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "review" / "report_manager_agent.yaml"

try:
    config = AgentConfig(str(report_manager_config_path)).get_agent()
    report_manager_settings = config
except FileNotFoundError:
    raise RuntimeError(
        f"Report manager agent configuration file not found at {report_manager_config_path}. "
        "Please ensure report_manager_agent.yaml exists in .profiles/"
    )

root_agent = Agent(
    name="report_manager",
    description="Generates comprehensive patient reports based on clinical findings and knowledge graph data.",
    model=Gemini(model_name="gemini-2.5-flash", retry_options=retry_config),
    instruction="""
    You are the Report Agent responsible for compiling detailed patient reports.
    Utilize clinical findings and knowledge graph data to create structured reports.""",
    sub_agents=[report_agent, final_report_agent],
    tools=[],
    on_tool_error_callback=handle_tool_error,
    output_key="final_report"
)

if __name__ == "__main__":
    print(f"Report Agent: {root_agent.name}")