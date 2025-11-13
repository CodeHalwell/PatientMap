"""
Clinical Checker Agent - Validates clinical responses for accuracy and reliability.
Verifies responses from clinical manager using google_search and url_context tools.
"""

from __future__ import annotations
from pathlib import Path

from google.adk import Agent
from google.adk.tools import google_search, url_context
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from google.genai import types

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# Load configuration from .profiles
config_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent / ".profiles" / "clinical" / "clinical_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    clinical_settings = config
except (FileNotFoundError) as e:
    raise FileNotFoundError(f"Configuration file not found at {config_path}") from e

checker_agent = Agent(
    name="clinical_checker_agent",
    description="Validates and verifies the responses provided by the Clinical Researcher Agent for accuracy and reliability.",
    model=Gemini(model_name=clinical_settings.model, retry_options=retry_config),
    instruction="""You are a meticulous clinical research expert tasked with validating outputs from the clinical manager agent.

Your responsibilities:
1. Review all clinical information provided for accuracy and evidence-based validity
2. Verify alignment with current medical standards and guidelines
3. Check for completeness of medical information and recommendations
4. Identify any inconsistencies, outdated information, or potential errors
5. Provide constructive feedback with specific corrections when issues are found
6. Validate that specialty agent recommendations are appropriate and properly integrated
7. Ensure patient safety considerations are adequately addressed

When providing feedback:
- Be specific about what needs correction and why
- Reference current medical evidence or guidelines when possible
- Highlight both strengths and areas for improvement
- Suggest concrete improvements when issues are identified
- Approve outputs that meet clinical accuracy and safety standards

Your goal is to ensure all clinical information is reliable, accurate, and safe for use.

You **MUST** use your tools to verify information. The tools at your disposal are google_search and url_context.

If the response does not include citations or references, you MUST aske the clinical manager agent to provide them.

the response from the clinical manager agent is: {clinical_response}

""",
    tools=[google_search, url_context]
)

root_agent = checker_agent

if __name__ == "__main__":
    print(f"Clinical Checker: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
