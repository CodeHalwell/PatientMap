from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from patientmap.common.config import AgentConfig

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "reviewer_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    reviewer_agent_settings = config
except FileNotFoundError:
    # Fallback to default settings if config file not found
    reviewer_agent_settings = type('obj', (object,), {
        'agent_name': 'reviewer',
        'description': 'Agent that reviews clinical findings and evidence',
        'model': 'gemini-2.5-flash',
        'instruction': 'You are a clinical reviewer specializing in evaluating research evidence.'
    })()