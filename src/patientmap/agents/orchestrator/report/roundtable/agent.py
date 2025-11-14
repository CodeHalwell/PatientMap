from __future__ import annotations


from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config, handle_tool_error


try:
    review_agent_1_config = AgentConfig("./review_agent_1.yaml").get_agent()
    review_agent_2_config = AgentConfig("./review_agent_2.yaml").get_agent()
    review_agent_3_config = AgentConfig("./review_agent_3.yaml").get_agent()
except FileNotFoundError as e:
    raise RuntimeError(f"Review agent configuration file not found: {e.filename}") from e

review_agent_1 = LlmAgent(
    name=review_agent_1_config.agent_name,
    description=review_agent_1_config.description,
    model=Gemini(model_name=review_agent_1_config.model, retry_options=retry_config),
    instruction=review_agent_1_config.instruction,
    tools=[],
    on_tool_error_callback=handle_tool_error,
)

review_agent_2 = LlmAgent(
    name=review_agent_2_config.agent_name,
    description=review_agent_2_config.description,
    model=Gemini(model_name=review_agent_2_config.model, retry_options=retry_config),
    instruction=review_agent_2_config.instruction,
    tools=[],
    on_tool_error_callback=handle_tool_error,
)

review_agent_3 = LlmAgent(
    name=review_agent_3_config.agent_name,
    description=review_agent_3_config.description,
    model=Gemini(model_name=review_agent_3_config.model, retry_options=retry_config),
    instruction=review_agent_3_config.instruction,
    tools=[],
    on_tool_error_callback=handle_tool_error,
)

root_agent = LlmAgent(
    name="roundtable_report_agent",
    description="Roundtable Report Agent coordinating multiple review agents for comprehensive report generation.",
    model=Gemini(model_name="gemini-2.5-pro", retry_options=retry_config),
    instruction="You are the Roundtable Report Agent coordinating multiple review agents to generate a comprehensive patient report.",
    sub_agents=[review_agent_1, review_agent_2, review_agent_3],
    tools=[],
    on_tool_error_callback=handle_tool_error,
)

if __name__ == "__main__":
    print(f"Roundtable Report Agent: {root_agent}")