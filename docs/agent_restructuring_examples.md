# Example Refactored Code: Data Phase Migration

This document shows **before and after** code for the data phase migration, demonstrating how to refactor agents from flat to hierarchical structure.

---

## Example 1: Data Manager Agent

### BEFORE (Flat Structure)

**File**: `src/patientmap/agents/data_manager/agent.py`

```python
from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk.agents import LlmAgent
from patientmap.common.config import AgentConfig
from google.adk.models.google_llm import Gemini

from patientmap.agents.data_gatherer.agent import root_agent as data_agent
from patientmap.agents.kg_initialiser.agent import root_agent as kg_initialiser_agent
from patientmap.common.helper_functions import retry_config

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "data" / "data_manager_agent.yaml"
try:
    config = AgentConfig(str(config_path)).get_agent()
    data_manager_agent_settings = config
except FileNotFoundError:
    raise RuntimeError("Data manager agent configuration file not found. Please create the file at '.profiles/data_manager_agent.yaml'.")

manager_agent = LlmAgent(
    name=data_manager_agent_settings.agent_name,
    description=data_manager_agent_settings.description,
    model=Gemini(model_name=data_manager_agent_settings.model, retry_options=retry_config),
    instruction=data_manager_agent_settings.instruction,
    sub_agents=[data_agent, kg_initialiser_agent],
)

root_agent = manager_agent

if __name__ == "__main__":
    print(root_agent)
```

**Problems**:
- ❌ Complex path manipulation (`parent.parent.parent.parent`)
- ❌ Config file path goes up then down directory tree
- ❌ Absolute imports from `patientmap.agents.*`
- ❌ `sys.path` manipulation required

---

### AFTER (Hierarchical Structure)

**File**: `src/patientmap/agents/orchestrator/data/agent.py`

```python
"""
Data Manager Agent - Coordinates patient data collection and knowledge graph initialization.
Part of Phase 1 of the PatientMap workflow.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Import sub-agents using relative imports
from .gatherer.agent import root_agent as data_gatherer_agent
from .kg_initialiser.agent import root_agent as kg_initialiser_agent

# Load configuration from co-located file
config_path = Path(__file__).parent / "config.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_manager_agent_settings = config
except FileNotFoundError:
    raise RuntimeError(
        f"Data manager agent configuration file not found at {config_path}. "
        "Please ensure config.yaml exists in the same directory as agent.py"
    )

# Create data manager agent
manager_agent = LlmAgent(
    name=data_manager_agent_settings.agent_name,
    description=data_manager_agent_settings.description,
    model=Gemini(
        model_name=data_manager_agent_settings.model,
        retry_options=retry_config
    ),
    instruction=data_manager_agent_settings.instruction,
    sub_agents=[data_gatherer_agent, kg_initialiser_agent],
)

# Export as root_agent for consistency
root_agent = manager_agent

if __name__ == "__main__":
    print(f"Data Manager Agent: {root_agent.name}")
    print(f"Sub-agents: {[agent.name for agent in root_agent.sub_agents]}")
```

**Improvements**:
- ✅ No `sys.path` manipulation
- ✅ Relative imports (`.gatherer`, `.kg_initialiser`)
- ✅ Config in same directory (`Path(__file__).parent / "config.yaml"`)
- ✅ Clear docstring explaining agent's role
- ✅ Better error message with actual path

**File**: `src/patientmap/agents/orchestrator/data/__init__.py`

```python
"""
Data Phase - Patient data collection and knowledge graph initialization.
Phase 1 of the PatientMap clinical workflow.
"""

from .agent import root_agent

__all__ = ['root_agent']
```

---

## Example 2: Data Gatherer Agent (Sub-Agent)

### BEFORE

**File**: `src/patientmap/agents/data_gatherer/agent.py`

```python
from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk.agents import LlmAgent
from patientmap.common.config import AgentConfig
from google.adk.models.google_llm import Gemini
from patientmap.common.helper_functions import retry_config

# Load configuration
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "data" / "data_gatherer_agent.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_gatherer_settings = config
except FileNotFoundError:
    raise RuntimeError("Data gatherer configuration file not found.")

triage_agent = LlmAgent(
    name=data_gatherer_settings.agent_name,
    description=data_gatherer_settings.description,
    model=Gemini(model_name=data_gatherer_settings.model, retry_options=retry_config),
    instruction=data_gatherer_settings.instruction,
)

root_agent = triage_agent

if __name__ == "__main__":
    print(root_agent)
```

---

### AFTER

**File**: `src/patientmap/agents/orchestrator/data/gatherer/agent.py`

```python
"""
Data Gatherer Agent - Conducts empathetic patient triage and information collection.
Collects comprehensive patient information through structured interview.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Load configuration from co-located file
config_path = Path(__file__).parent / "config.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    data_gatherer_settings = config
except FileNotFoundError:
    raise RuntimeError(
        f"Data gatherer configuration not found at {config_path}"
    )

# Create triage agent
triage_agent = LlmAgent(
    name=data_gatherer_settings.agent_name,
    description=data_gatherer_settings.description,
    model=Gemini(
        model_name=data_gatherer_settings.model,
        retry_options=retry_config
    ),
    instruction=data_gatherer_settings.instruction,
)

root_agent = triage_agent

if __name__ == "__main__":
    print(f"Data Gatherer Agent: {root_agent.name}")
```

**File**: `src/patientmap/agents/orchestrator/data/gatherer/__init__.py`

```python
"""Data Gatherer - Patient triage and information collection."""

from .agent import root_agent

__all__ = ['root_agent']
```

**File**: `src/patientmap/agents/orchestrator/data/gatherer/config.yaml`

*(Copy from `.profiles/data/data_gatherer_agent.yaml`)*

---

## Example 3: KG Initialiser Agent (Complex Sub-Tree)

### BEFORE

**File**: `src/patientmap/agents/kg_initialiser/agent.py`

```python
from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for relative imports
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from google.adk.agents import LoopAgent, LlmAgent
from google.adk.tools import exit_loop
from patientmap.common.config import AgentConfig
from patientmap.tools.kg_tools import (
    initialize_patient_graph,
    bulk_add_nodes,
    bulk_add_relationships,
    # ... many more imports
)
from patientmap.common.helper_functions import retry_config
from google.adk.models.google_llm import Gemini

# Load configuration
kg_init_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "kg_initialiser.yaml"
kg_checker_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "knowledge" / "kg_checker_agent.yaml"

try:
    kg_init_config = AgentConfig(str(kg_init_path)).get_agent()
    kg_checker_config = AgentConfig(str(kg_checker_path)).get_agent()
except FileNotFoundError:
    raise RuntimeError("KG initialiser agent configuration file not found.")

# Planning agent
planning_agent = LlmAgent(
    name="Knowledge_graph_planning_agent",
    description="An agent that extracts and plans the knowledge graph structure...",
    model=Gemini(model_name=kg_init_config.model, retry_options=retry_config),
    instruction="""Analyze the patient data...""",
    output_key="kg_plan"
)

# Build agent
build_agent = LlmAgent(
    name=kg_init_config.agent_name,
    description=kg_init_config.description,
    model=Gemini(model_name=kg_init_config.model, retry_options=retry_config),
    instruction=kg_init_config.instruction,
    tools=[initialize_patient_graph, bulk_add_nodes, ...],
)

# Logic checker
logic_checker_agent = LlmAgent(
    name=kg_checker_config.agent_name,
    description=kg_checker_config.description,
    model=Gemini(model_name=kg_checker_config.model, retry_options=retry_config),
    instruction=kg_checker_config.instruction,
    tools=[validate_graph_structure, exit_loop, ...],
)

# Loop agent
loop_agent = LoopAgent(
    name="Knowledge_graph_loop_agent",
    description="Iterative loop for building and validating the knowledge graph.",
    sub_agents=[build_agent, logic_checker_agent],
    max_iterations=3,
)

# Coordinator
kg_initialiser_agent = LlmAgent(
    name="Knowledge_graph_initialiser_agent",
    description="Orchestrates knowledge graph creation workflow.",
    model=Gemini(model_name=kg_init_config.model, retry_options=retry_config),
    instruction="""You are the Knowledge Graph Initialiser coordinator...""",
    sub_agents=[planning_agent, loop_agent],
)

root_agent = kg_initialiser_agent
```

---

### AFTER (Split into Sub-Directories)

**File**: `src/patientmap/agents/orchestrator/data/kg_initialiser/agent.py`

```python
"""
Knowledge Graph Initialiser - Coordinates KG creation workflow.
Orchestrates planning → building → validation loop.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Import sub-agents using relative imports
from .planning.agent import root_agent as planning_agent
from .build_loop.agent import root_agent as loop_agent

# Load configuration
config_path = Path(__file__).parent / "config.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    kg_init_settings = config
except FileNotFoundError:
    raise RuntimeError(f"KG initialiser config not found at {config_path}")

# Create coordinator agent
kg_initialiser_agent = LlmAgent(
    name=kg_init_settings.agent_name,
    description=kg_init_settings.description,
    model=Gemini(
        model_name=kg_init_settings.model,
        retry_options=retry_config
    ),
    instruction=kg_init_settings.instruction,
    sub_agents=[planning_agent, loop_agent],
)

root_agent = kg_initialiser_agent

if __name__ == "__main__":
    print(f"KG Initialiser: {root_agent.name}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
```

**File**: `src/patientmap/agents/orchestrator/data/kg_initialiser/planning/agent.py`

```python
"""
Planning Agent - Analyzes patient data and creates comprehensive KG plan.
Extracts entities, relationships, and structure from patient narrative.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config

# Load configuration
config_path = Path(__file__).parent / "config.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    planning_settings = config
except FileNotFoundError:
    raise RuntimeError(f"Planning agent config not found at {config_path}")

# Create planning agent
planning_agent = LlmAgent(
    name=planning_settings.agent_name,
    description=planning_settings.description,
    model=Gemini(
        model_name=planning_settings.model,
        retry_options=retry_config
    ),
    instruction=planning_settings.instruction,
    output_key="kg_plan"
)

root_agent = planning_agent

if __name__ == "__main__":
    print(f"Planning Agent: {root_agent.name}")
```

**File**: `src/patientmap/agents/orchestrator/data/kg_initialiser/build_loop/agent.py`

```python
"""
Build Loop - Iterative knowledge graph construction and validation.
LoopAgent that builds graph, validates, provides feedback, and iterates.
"""

from __future__ import annotations

from google.adk.agents import LoopAgent

# Import builder and checker sub-agents
from .builder.agent import root_agent as build_agent
from .checker.agent import root_agent as logic_checker_agent

# Create loop agent
loop_agent = LoopAgent(
    name="Knowledge_graph_build_loop",
    description=(
        "Iterative loop for building and validating the knowledge graph. "
        "Builder creates/updates graph, checker validates and provides feedback. "
        "Loop continues until checker calls exit_loop (max 3 iterations)."
    ),
    sub_agents=[build_agent, logic_checker_agent],
    max_iterations=3,
)

root_agent = loop_agent

if __name__ == "__main__":
    print(f"Build Loop: {root_agent.name}")
    print(f"Max Iterations: {root_agent.max_iterations}")
    print(f"Sub-agents: {[a.name for a in root_agent.sub_agents]}")
```

**File**: `src/patientmap/agents/orchestrator/data/kg_initialiser/build_loop/builder/agent.py`

```python
"""
Builder Agent - Creates and updates the patient knowledge graph.
Uses bulk operations to add nodes and relationships based on plan.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.kg_tools import (
    initialize_patient_graph,
    bulk_add_nodes,
    bulk_add_relationships,
    delete_node,
    delete_relationship,
    merge_duplicate_nodes,
    get_patient_overview,
    export_graph_summary,
    save_graph_to_disk,
    export_graph_as_cytoscape_json,
    validate_graph_structure,
)

# Load configuration
config_path = Path(__file__).parent / "config.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    builder_settings = config
except FileNotFoundError:
    raise RuntimeError(f"Builder config not found at {config_path}")

# Create builder agent with KG tools
build_agent = LlmAgent(
    name=builder_settings.agent_name,
    description=builder_settings.description,
    model=Gemini(
        model_name=builder_settings.model,
        retry_options=retry_config
    ),
    instruction=builder_settings.instruction,
    tools=[
        initialize_patient_graph,
        bulk_add_nodes,
        bulk_add_relationships,
        delete_node,
        delete_relationship,
        merge_duplicate_nodes,
        get_patient_overview,
        export_graph_summary,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        validate_graph_structure,
    ],
)

root_agent = build_agent

if __name__ == "__main__":
    print(f"Builder Agent: {root_agent.name}")
    print(f"Tools: {len(root_agent.tools)}")
```

**File**: `src/patientmap/agents/orchestrator/data/kg_initialiser/build_loop/checker/agent.py`

```python
"""
Checker Agent - Validates knowledge graph structure and completeness.
Provides feedback to builder and calls exit_loop when satisfied.
"""

from __future__ import annotations
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import exit_loop
from patientmap.common.config import AgentConfig
from patientmap.common.helper_functions import retry_config
from patientmap.tools.kg_tools import (
    validate_graph_structure,
    check_node_completeness,
    bulk_check_node_completeness,
    analyze_graph_connectivity,
    list_all_nodes_by_type,
    get_node_relationships,
    export_graph_summary,
    load_graph_from_disk,
    save_graph_to_disk,
    export_graph_as_cytoscape_json,
)

# Load configuration
config_path = Path(__file__).parent / "config.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    checker_settings = config
except FileNotFoundError:
    raise RuntimeError(f"Checker config not found at {config_path}")

# Create logic checker agent
logic_checker_agent = LlmAgent(
    name=checker_settings.agent_name,
    description=checker_settings.description,
    model=Gemini(
        model_name=checker_settings.model,
        retry_options=retry_config
    ),
    instruction=checker_settings.instruction,
    tools=[
        validate_graph_structure,
        check_node_completeness,
        bulk_check_node_completeness,
        analyze_graph_connectivity,
        list_all_nodes_by_type,
        get_node_relationships,
        export_graph_summary,
        load_graph_from_disk,
        save_graph_to_disk,
        export_graph_as_cytoscape_json,
        exit_loop,  # Critical: allows checker to end loop
    ],
)

root_agent = logic_checker_agent

if __name__ == "__main__":
    print(f"Checker Agent: {root_agent.name}")
    print(f"Has exit_loop: {exit_loop in root_agent.tools}")
```

**File Structure**:
```
orchestrator/data/kg_initialiser/
├── __init__.py
├── agent.py                    # Coordinator
├── config.yaml
│
├── planning/                   # Step 1: Plan
│   ├── __init__.py
│   ├── agent.py
│   └── config.yaml
│
└── build_loop/                 # Step 2: Build & Validate Loop
    ├── __init__.py
    ├── agent.py                # LoopAgent wrapper
    │
    ├── builder/                # Builder sub-agent
    │   ├── __init__.py
    │   ├── agent.py
    │   └── config.yaml
    │
    └── checker/                # Checker sub-agent
        ├── __init__.py
        ├── agent.py
        └── config.yaml
```

---

## Example 4: Orchestrator Updates

### BEFORE

**File**: `src/patientmap/agents/orchestrator/agent.py`

```python
from patientmap.agents.data_manager.agent import root_agent as data_manager_agent
from patientmap.agents.research.agent import root_agent as research_agent
from patientmap.agents.clinical.agent import root_agent as clinical_agent
```

---

### AFTER

**File**: `src/patientmap/agents/orchestrator/agent.py`

```python
"""
Orchestrator Agent - Coordinates PatientMap clinical workflow.
Manages sequential execution: Data → Research → Clinical phases.
"""

from __future__ import annotations
from pathlib import Path

from google.adk import Agent
from google.adk.tools import google_search
from patientmap.common.config import AgentConfig

# Import phase agents using relative imports (clean!)
from .data.agent import root_agent as data_manager_agent
from .research.agent import root_agent as research_agent
from .clinical.agent import root_agent as clinical_agent

# Load configuration
config_path = Path(__file__).parent / "config.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    orchestrator_settings = config
except FileNotFoundError:
    raise RuntimeError(f"Orchestrator config not found at {config_path}")

# Create root agent
root_agent = Agent(
    name=orchestrator_settings.agent_name,
    description=orchestrator_settings.description,
    model=orchestrator_settings.model,
    instruction=orchestrator_settings.instruction,
    sub_agents=[data_manager_agent, research_agent, clinical_agent],
    tools=[google_search]
)

if __name__ == "__main__":
    print(f"Orchestrator Agent: {root_agent.name}")
    print(f"Phase agents: {[a.name for a in root_agent.sub_agents]}")
```

---

## Example 5: Clinical Manager with Specialists

### AFTER (Showing Clean Import Pattern)

**File**: `src/patientmap/agents/orchestrator/clinical/manager/agent.py`

```python
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
from patientmap.common.helper_functions import retry_config

# Import all 16 specialists using relative imports
from .specialists.cardiology.agent import root_agent as cardiology_agent
from .specialists.neurology.agent import root_agent as neurology_agent
from .specialists.psychiatry.agent import root_agent as psychiatry_agent
from .specialists.endocrinology.agent import root_agent as endocrinology_agent
from .specialists.clinical_pharmacy.agent import root_agent as pharmacy_agent
from .specialists.gastroenterology.agent import root_agent as gastro_agent
from .specialists.geriatrics.agent import root_agent as geriatrics_agent
from .specialists.hematology.agent import root_agent as hematology_agent
from .specialists.nephrology.agent import root_agent as nephrology_agent
from .specialists.pulmonology.agent import root_agent as pulmonology_agent
from .specialists.physical_medicine_rehabilitation.agent import root_agent as physical_agent
from .specialists.infectious_disease.agent import root_agent as infectious_agent
from .specialists.nutrition_dietetics.agent import root_agent as nutrition_agent
from .specialists.pain_medicine.agent import root_agent as pain_agent
from .specialists.rheumatology.agent import root_agent as rheumatology_agent
from .specialists.palliative_care.agent import root_agent as palliative_agent

# Load configuration
config_path = Path(__file__).parent / "config.yaml"

try:
    config = AgentConfig(str(config_path)).get_agent()
    clinical_settings = config
except FileNotFoundError:
    raise RuntimeError(f"Clinical manager config not found at {config_path}")

# Create clinical manager with all specialists as tools
clinical_manager = Agent(
    name=clinical_settings.agent_name,
    description=clinical_settings.description,
    model=Gemini(
        model_name=clinical_settings.model,
        retry_options=retry_config
    ),
    instruction=clinical_settings.instruction,
    tools=[
        AgentTool(agent=cardiology_agent),
        AgentTool(agent=neurology_agent),
        AgentTool(agent=psychiatry_agent),
        AgentTool(agent=endocrinology_agent),
        AgentTool(agent=pharmacy_agent),
        AgentTool(agent=gastro_agent),
        AgentTool(agent=geriatrics_agent),
        AgentTool(agent=hematology_agent),
        AgentTool(agent=nephrology_agent),
        AgentTool(agent=pulmonology_agent),
        AgentTool(agent=physical_agent),
        AgentTool(agent=infectious_agent),
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
```

**Benefits**:
- ✅ All imports are relative (`.specialists.*`)
- ✅ Clear namespace hierarchy
- ✅ Easy to add/remove specialists
- ✅ No path manipulation needed

---

## Key Patterns Summary

### Pattern 1: Config Loading
```python
# OLD (complex path traversal)
config_path = Path(__file__).parent.parent.parent.parent.parent / ".profiles" / "data" / "agent.yaml"

# NEW (co-located)
config_path = Path(__file__).parent / "config.yaml"
```

### Pattern 2: Sub-Agent Imports
```python
# OLD (absolute imports + sys.path)
import sys
sys.path.insert(0, str(src_path))
from patientmap.agents.sub_agent.agent import root_agent

# NEW (relative imports)
from .sub_agent.agent import root_agent
```

### Pattern 3: __init__.py Pattern
```python
"""Agent module - Brief description."""

from .agent import root_agent

__all__ = ['root_agent']
```

### Pattern 4: Docstrings
```python
"""
Agent Name - Brief one-line description.
Longer description of agent's role and responsibilities.
Part of [Phase/Parent] workflow.
"""
```

---

## Testing Refactored Agents

### Test Individual Agent
```python
# Test importing refactored agent
python -c "from patientmap.agents.orchestrator.data.agent import root_agent; print(root_agent)"
```

### Test Full Chain
```python
# Test complete import chain
python -c "
from patientmap.agents.orchestrator.agent import root_agent
print(f'Root: {root_agent.name}')
for agent in root_agent.sub_agents:
    print(f'  Sub: {agent.name}')
"
```

### Test Main Entry Point
```python
# Ensure main.py still works
python main.py --help
```

---

## Common Issues & Solutions

### Issue 1: Circular Imports
**Symptom**: `ImportError: cannot import name 'root_agent'`

**Solution**: Ensure `__init__.py` files only import from `.agent`, never cross-import between siblings

### Issue 2: Config Not Found
**Symptom**: `RuntimeError: config not found`

**Solution**: Verify `config.yaml` exists in same directory as `agent.py`

### Issue 3: Module Not Found
**Symptom**: `ModuleNotFoundError: No module named 'patientmap.agents.orchestrator.data'`

**Solution**: Ensure all intermediate directories have `__init__.py` files

### Issue 4: sys.path Still Referenced
**Symptom**: Tests fail with import errors

**Solution**: Remove ALL `sys.path.insert()` calls, use only relative/absolute imports from `patientmap.*`

---

This example demonstrates the complete transformation from flat to hierarchical structure. The key is **consistency**: every agent follows the same patterns for imports, config loading, and module structure.
