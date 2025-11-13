"""
Clinical Manager - Routes patient cases to appropriate medical specialists.
Coordinates analysis across 16 clinical specialties.
"""

from __future__ import annotations
from pathlib import Path

from google.adk import Agent
from google.adk.tools import AgentTool
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from google.genai import types

# Configure logging to suppress harmless LangChain shutdown warnings
from patientmap.common.logging import configure_logging
configure_logging()

# Import all 16 specialists using relative imports
from .specialists.cardiology import cardiology_agent
from .specialists.neurology import neurology_agent
from .specialists.psychiatry import psychiatry_agent
from .specialists.endocrinology import endocrinology_agent
from .specialists.clinical_pharmacy import pharmacy_agent
from .specialists.gastroenterology import gastroenterology_agent
from .specialists.geriatrics import geriatrics_agent
from .specialists.hematology import hematology_agent
from .specialists.nephrology import nephrology_agent
from .specialists.pulmonology import pulmonology_agent
from .specialists.physical_medicine_rehabilitation import physical_agent
from .specialists.infectious_disease import infectious_disease_agent
from .specialists.nutrition_dietetics import nutrition_agent
from .specialists.pain_medicine import pain_agent
from .specialists.rheumatology import rheumatology_agent
from .specialists.palliative_care import palliative_agent

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

# Create clinical manager with all specialists as tools
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

root_agent = clinical_manager

if __name__ == "__main__":
    print(f"Clinical Manager: {root_agent.name}")
    print(f"Specialists: {len(root_agent.tools)}")
