from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config, handle_tool_error
from patientmap.tools.tool_registry import get_tools_from_config

current_dir = Path(__file__).parent

try:
    review_agent_1_config = AgentConfig(str(current_dir / "review_agent_1.yaml")).get_agent()
    review_agent_2_config = AgentConfig(str(current_dir / "review_agent_2.yaml")).get_agent()
    review_agent_3_config = AgentConfig(str(current_dir / "review_agent_3.yaml")).get_agent()
    roundtable_agent_config = AgentConfig(str(current_dir / "roundtable_agent.yaml")).get_agent()
except FileNotFoundError as e:
    raise RuntimeError(f"Review agent configuration file not found at {current_dir}") from e

# Load tools from registry (review agents have no tools, roundtable has show_my_available_tools)
review_1_tools = get_tools_from_config(review_agent_1_config.tools)
review_2_tools = get_tools_from_config(review_agent_2_config.tools)
review_3_tools = get_tools_from_config(review_agent_3_config.tools)
roundtable_tools = get_tools_from_config(roundtable_agent_config.tools)

review_agent_1 = LlmAgent(
    name=review_agent_1_config.agent_name,
    description=review_agent_1_config.description,
    model=Gemini(model_name=review_agent_1_config.model, retry_options=retry_config),
    instruction=review_agent_1_config.instruction,
    tools=review_1_tools,
    on_tool_error_callback=handle_tool_error,
)

review_agent_2 = LlmAgent(
    name=review_agent_2_config.agent_name,
    description=review_agent_2_config.description,
    model=Gemini(model_name=review_agent_2_config.model, retry_options=retry_config),
    instruction=review_agent_2_config.instruction,
    tools=review_2_tools,
    on_tool_error_callback=handle_tool_error,
)

review_agent_3 = LlmAgent(
    name=review_agent_3_config.agent_name,
    description=review_agent_3_config.description,
    model=Gemini(model_name=review_agent_3_config.model, retry_options=retry_config),
    instruction=review_agent_3_config.instruction,
    tools=review_3_tools,
    on_tool_error_callback=handle_tool_error,
)

roundtable_loop = LoopAgent(
    name="roundtable_discussion_loop",
    description="Facilitates discussion among review agents to reach consensus on clinical findings.",
    sub_agents=[review_agent_1, review_agent_2, review_agent_3],
    max_iterations=5,
)

summary_agent = LlmAgent(
    name="roundtable_summary_agent",
    description="Summarizes the outcomes of the roundtable discussion into a coherent report.",
    model=Gemini(model_name=roundtable_agent_config.model, retry_options=retry_config),
    instruction="Summarize the key points and consensus from the roundtable discussion into a final report.",
    tools=roundtable_tools,
    on_tool_error_callback=handle_tool_error,
)

root_agent = SequentialAgent(
    name=roundtable_agent_config.agent_name,
    description=roundtable_agent_config.description,
    sub_agents=[roundtable_loop, summary_agent],
)

if __name__ == "__main__":
    print(f"Roundtable Report Agent: {root_agent}")