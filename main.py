"""
PatientMap - Clinical Researcher Agent
Main entry point for the application
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from google.adk.apps import App, ResumabilityConfig
from google.adk.plugins import ContextFilterPlugin
from patientmap.agents.orchestrator.agent import root_agent


app = App(
    name="patientmap",
    root_agent=root_agent,
    plugins=[
        ContextFilterPlugin(num_invocations_to_keep=5)
    ],
    resumability_config=ResumabilityConfig(is_resumable=True)
)


if __name__ == "__main__":
    app.run()