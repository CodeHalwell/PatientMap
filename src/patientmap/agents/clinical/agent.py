"""
Clinical Researcher Agent - Researches medical conditions and clinical evidence
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk.models.google_llm import Gemini
from google.genai import types
from google.adk import Agent
from google.adk.agents import LoopAgent
from google.adk.tools import google_search, AgentTool, url_context
from patientmap.common.config import AgentConfig
from patientmap.common.logging import configure_logging
from patientmap.agents.clinical.cardiology import cardiology_agent

# Configure logging to suppress harmless LangChain shutdown warnings
configure_logging()
from patientmap.agents.clinical.neurology import neurology_agent
from patientmap.agents.clinical.psychiatry import psychiatry_agent
from patientmap.agents.clinical.endocrinology import endocrinology_agent
from patientmap.agents.clinical.clinical_pharmacy import pharmacy_agent
from patientmap.agents.clinical.gastroenterology import gastroenterology_agent
from patientmap.agents.clinical.geriatrics import geriatrics_agent
from patientmap.agents.clinical.hematology import hematology_agent
from patientmap.agents.clinical.nephrology import nephrology_agent
from patientmap.agents.clinical.pulmonology import pulmonology_agent
from patientmap.agents.clinical.physical_medicine_rehabilitation import physical_agent
from patientmap.agents.clinical.infectious_disease import infectious_disease_agent
from patientmap.agents.clinical.nutrition_dietetics import nutrition_agent
from patientmap.agents.clinical.pain_medicine import pain_agent
from patientmap.agents.clinical.rheumatology import rheumatology_agent
from patientmap.agents.clinical.palliative_care import palliative_agent

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "clinical" / "clinical_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    clinical_settings = config
except (FileNotFoundError) as e:
    raise FileNotFoundError(f"Configuration file not found at {config_path}") from e
finally:
    # Clean up sys.path
    sys.path.pop(0)

# Create agent
clinical_manager = Agent(
    name=clinical_settings.agent_name,
    description=clinical_settings.description,
    model=Gemini(model_name=clinical_settings.model, retry_options=retry_config),
    instruction=clinical_settings.instruction,
    tools=[
        AgentTool(agent=cardiology_agent),
        AgentTool(agent=neurology_agent),
        AgentTool(agent=psychiatry_agent),
        AgentTool(agent=endocrinology_agent),
        AgentTool(agent=pharmacy_agent),
        AgentTool(agent=gastroenterology_agent),
        AgentTool(agent=geriatrics_agent),
        AgentTool(agent=hematology_agent),
        AgentTool(agent=nephrology_agent),
        AgentTool(agent=pulmonology_agent),
        AgentTool(agent=physical_agent),
        AgentTool(agent=infectious_disease_agent),
        AgentTool(agent=nutrition_agent),
        AgentTool(agent=pain_agent),
        AgentTool(agent=rheumatology_agent),
        AgentTool(agent=palliative_agent),
    ],
    output_key="clinical_response"
)

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

loop_agent = LoopAgent(
    name="clinical_loop_agent",
    description="Coordinates the clinical research and checking agents to ensure accurate and reliable clinical information.",
    sub_agents=[clinical_manager, checker_agent],
    max_iterations=3,
)

root_agent = loop_agent


if __name__ == "__main__":
    print(root_agent)