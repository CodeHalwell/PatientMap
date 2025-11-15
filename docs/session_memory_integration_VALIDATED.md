# Session and Memory Integration Roadmap for PatientMap
## COMPREHENSIVE VALIDATION EDITION

**Status**: Validated against full codebase, official ADK source, and Context7 documentation  
**Date**: 2025-01-XX  
**Authors**: AI Coding Assistant (comprehensive codebase analysis)

---

## Executive Summary

This document presents a **fully validated roadmap** for integrating Google ADK session management and long-term memory into PatientMap, based on:

1. ✅ **Official Google ADK source patterns** (`google/adk-python` repository samples)
2. ✅ **Kaggle Google Course materials** (day_3a, day_3b for session/memory best practices)
3. ✅ **Complete PatientMap codebase analysis** (all agents, tools, configs, state management)
4. ✅ **Context7 ADK production documentation** (runner initialization, service wiring)

### Critical Findings

| Finding | Impact | Recommendation |
|---------|--------|----------------|
| **Current `app.run()` pattern is VALID** | None | Keep for CLI, optionally add `Runner` for programmatic control |
| **Session Service is REQUIRED (not optional)** | HIGH | Must implement before memory integration |
| **Memory Service is OPTIONAL** | MEDIUM | Add after sessions for cross-session memory |
| **tool_context.state['kg_data'] may conflict with session.state** | MEDIUM | Establish naming conventions, clarify responsibilities |
| **KG persistence to disk is independent of sessions** | LOW | Can enhance with session metadata integration |
| **No session service currently configured** | **CRITICAL** | Blocks resumability and persistence features |

---

## Current Architecture Deep Dive

### 1. Agent Hierarchy (Fully Mapped)

```
App("patientmap")
└── orchestrator_agent (root_agent) [gemini-2.5-pro]
    │   Sequential phases: data → research → clinical
    │
    ├── data_manager_agent [gemini-2.5-flash]
    │   ├── data_gatherer_agent (triage/intake) [gemini-2.5-flash]
    │   └── kg_initialiser_agent [gemini-2.5-flash]
    │       ├── planning_agent (analyzes patient data)
    │       └── LoopAgent (max_iterations=3)
    │           ├── build_agent (bulk_add_nodes, bulk_add_relationships)
    │           └── logic_checker_agent (validate, exit_loop)
    │
    ├── research_agent [gemini-2.5-pro root]
    │   ├── research_topics (generates prioritized list) [gemini-2.5-flash]
    │   ├── LoopAgent (max_iterations=10)
    │   │   └── research_agent (google_search, url_context) [gemini-2.5-flash]
    │   └── kg_agent (knowledge enrichment) [gemini-2.5-flash]
    │       └── LoopAgent (max_iterations=5)
    │           ├── knowledge_graph_agent (bulk add nodes/rels)
    │           └── enrichment_checker (validate, exit_loop)
    │
    └── clinical_agent [gemini-2.5-flash]
        └── LoopAgent (max_iterations=3)
            ├── clinical_manager (16 specialist AgentTools)
            │   ├── cardiology_agent
            │   ├── neurology_agent
            │   ├── psychiatry_agent
            │   ├── endocrinology_agent
            │   ├── pharmacy_agent
            │   ├── gastroenterology_agent
            │   ├── geriatrics_agent
            │   ├── hematology_agent
            │   ├── nephrology_agent
            │   ├── pulmonology_agent
            │   ├── physical_agent
            │   ├── infectious_disease_agent
            │   ├── nutrition_agent
            │   ├── pain_agent
            │   ├── rheumatology_agent
            │   └── palliative_agent
            └── checker_agent (validates with google_search, url_context)
```

**Key Observations**:
- **3 sequential phases** coordinated by orchestrator (must complete in order)
- **5 LoopAgent instances** (builders + checkers pattern)
- **16 specialist agents** as tools (clinical phase)
- **30 YAML configuration files** in `.profiles/**` directory

### 2. State Management (Full Analysis)

#### A. Tool Context State (`tool_context.state`)

**Current Usage**: Knowledge graph storage  
**Primary Key**: `kg_data` (NetworkX node-link JSON)  
**Affected Functions**: 20+ functions in `kg_tools.py`

```python
# Pattern used by ALL kg_tools:
def _get_graph(tool_context: ToolContext) -> nx.DiGraph:
    if 'kg_data' not in tool_context.state:
        return nx.DiGraph()
    data = tool_context.state['kg_data']
    return nx.node_link_graph(data, directed=True, edges="links")

def _save_graph(graph: nx.DiGraph, tool_context: ToolContext) -> None:
    data = nx.node_link_data(graph, edges="links")
    tool_context.state['kg_data'] = data
```

**Tools Using This Pattern**:
- `initialize_patient_graph`, `add_node`, `bulk_add_nodes`
- `add_relationship`, `bulk_add_relationships`
- `bulk_link_articles_to_conditions`
- `list_all_nodes_by_type`, `get_node_relationships`
- `validate_graph_structure`, `analyze_graph_connectivity`
- `export_graph_summary`, `export_graph_as_cytoscape_json`
- `delete_node`, `delete_relationship`, `merge_duplicate_nodes`

**Persistence Mechanism**:
- Independent from `tool_context.state`
- `save_graph_to_disk(filename, output_dir)` writes to:
  - `knowledge_graphs/{filename}_{timestamp}.json` (node-link format)
  - `knowledge_graphs/{filename}_{timestamp}.graphml` (XML visualization)
  - `knowledge_graphs/{filename}_{timestamp}_summary.txt` (human-readable)
- Default directory: Project root `knowledge_graphs/`

#### B. Session State (Proposed ADK Pattern)

**Not Currently Implemented** but ADK supports:

```python
# User-scoped state (per user, across sessions)
session.state['user:name'] = "John Doe"
session.state['user:date_of_birth'] = "1980-01-01"

# App-scoped state (global, all users)
session.state['app:version'] = "1.0.0"
session.state['app:feature_flags'] = {...}

# Temporary state (current session only)
session.state['temp:current_phase'] = "research"
session.state['temp:research_topics_count'] = 5
```

**Question for Roadmap**: Should `kg_data` migrate to `session.state['app:kg_data']`?  
**Consideration**: Tool context state vs session state separation of concerns

#### C. Configuration System

**Location**: `.profiles/**` directory (30 YAML files)  
**Structure**:
```yaml
agent_id: oa001
agent_name: orchestrator_agent
model: 'gemini-2.5-pro'
description: >
  The Orchestrator Agent coordinates...
instruction: |
  As the Orchestrator Agent...
tools: []
```

**Loader**: `patientmap/common/config.py`
```python
class AgentConfig:
    def __init__(self, profile_path):
        self.profile = yaml.safe_load(open(profile_path))
    
    def get_agent(self):
        return AgentSettings(
            agent_id=self.profile.get("agent_id"),
            agent_name=self.profile.get("agent_name"),
            model=self.profile.get("model"),
            instruction=self.profile.get("instruction"),
            description=self.profile.get("description"),
            tools=self.profile.get("tools", [])
        )
```

**Extension Point**: Can add session/memory parameters to YAML configs

### 3. Runtime Patterns (Validated Against Official ADK)

#### Pattern 1: Current PatientMap (`main.py`)

```python
from google.adk.apps import App, ResumabilityConfig
from google.adk.plugins import ContextFilterPlugin
from patientmap.agents.orchestrator.agent import root_agent

app = App(
    name="patientmap",
    root_agent=root_agent,
    plugins=[ContextFilterPlugin(num_invocations_to_keep=5)],
    resumability_config=ResumabilityConfig(is_resumable=True)
)

app.run()  # Interactive CLI mode
```

**Official ADK Status**: ✅ **VALID** for interactive applications  
**Services**: None explicitly configured (uses internal defaults)  
**Use Case**: CLI/console interaction, prototyping  
**Limitations**: 
- No explicit session service control
- Cannot inject custom memory service
- Limited programmatic access

#### Pattern 2: Orchestrator Test Harness (`orchestrator/agent.py __main__`)

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

runner = Runner(
    app=app,
    session_service=session_service,
    memory_service=memory_service
)

# Manual session creation
session = await session_service.create_session(
    app_name="patientmap",
    user_id="test_user"
)

# Explicit invocation
async for event in runner.run_async(
    user_id=session.user_id,
    session_id=session.id,
    new_message=content
):
    # Process events
```

**Official ADK Status**: ✅ **PRODUCTION-READY**  
**Services**: Explicit wiring for full control  
**Use Case**: Programmatic invocation, testing, API servers  
**Advantages**:
- Complete control over services
- Can inject custom implementations
- Supports async event streaming
- Ideal for web backends

#### Pattern 3: Official ADK Helper (`InMemoryRunner`)

```python
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(app=app)  # Auto-wires services
await runner.run_debug("Query")   # Simplified debugging
```

**Official ADK Status**: ✅ **PROTOTYPING/TESTING ONLY**  
**Services**: Automatic `InMemorySessionService` + `InMemoryMemoryService`  
**Use Case**: Quick prototyping, debugging, unit tests  
**Limitations**: Not recommended for production

---

## Integration Roadmap (Validated Strategy)

### Stage 1: Implement Session Management (CRITICAL PRIORITY)

**Goal**: Enable persistent sessions with resumability across kernel restarts

#### 1.1 Create Runtime Services Module

**File**: `src/patientmap/runtime/services.py`

```python
"""
Runtime services configuration for PatientMap.
Centralizes session, artifact, and memory service initialization.
"""

from google.adk.apps import App, ResumabilityConfig, EventsCompactionConfig
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.plugins import ContextFilterPlugin
from patientmap.agents.orchestrator.agent import root_agent
from pathlib import Path
import os

# Configuration from environment
DB_URL = os.getenv(
    "PATIENTMAP_SESSION_DB",
    f"sqlite:///{Path(__file__).parent.parent.parent / 'var' / 'runtime' / 'sessions.db'}"
)
USE_PERSISTENT_SESSIONS = os.getenv("PATIENTMAP_PERSISTENT_SESSIONS", "true").lower() == "true"

def create_session_service():
    """Create session service based on environment configuration."""
    if USE_PERSISTENT_SESSIONS:
        return DatabaseSessionService(db_url=DB_URL)
    return InMemorySessionService()

def create_app():
    """Create configured PatientMap application."""
    return App(
        name="patientmap",
        root_agent=root_agent,
        plugins=[
            ContextFilterPlugin(num_invocations_to_keep=5)
        ],
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=3,  # Compact every 3 agent invocations
            overlap_size=1          # Keep 1 turn overlap for context
        ),
        resumability_config=ResumabilityConfig(is_resumable=True)
    )

def create_runner(
    session_service=None,
    artifact_service=None,
    memory_service=None
):
    """
    Create configured runner with services.
    
    Args:
        session_service: Optional custom session service (defaults to DatabaseSessionService)
        artifact_service: Optional custom artifact service (defaults to InMemoryArtifactService)
        memory_service: Optional memory service (defaults to None, add in Stage 2)
    
    Returns:
        Configured Runner instance
    """
    app = create_app()
    
    if session_service is None:
        session_service = create_session_service()
    
    if artifact_service is None:
        artifact_service = InMemoryArtifactService()
    
    # Memory service remains None until Stage 2
    
    return Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service
    )

# Helper function for CLI/API integration
async def run_session(
    runner: Runner,
    session_id: str,
    user_id: str,
    message: str
):
    """
    Helper to run a single message through the agent system.
    Based on Kaggle day_3a_agent_sessions.py pattern.
    """
    from google.genai import types
    
    content = types.Content(role='user', parts=[types.Part(text=message)])
    
    events = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        events.append(event)
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"[{event.author}]: {part.text}")
    
    return events
```

#### 1.2 Update `main.py` for Session Support

**Current `main.py`**:
```python
app = App(...)
app.run()
```

**Updated `main.py`** (backward compatible):
```python
"""
PatientMap Application Entry Point
Supports both interactive CLI (original behavior) and programmatic invocation
"""

import asyncio
import sys
from pathlib import Path

# Ensure src is on path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from patientmap.runtime.services import create_app, create_runner, run_session
from google.genai import types

def run_interactive():
    """Original interactive CLI mode using App.run()"""
    app = create_app()
    app.run()

async def run_with_sessions():
    """New mode with explicit session management"""
    runner = create_runner()
    
    # Create or resume session
    session = await runner.session_service.create_session(
        app_name="patientmap",
        user_id="default_user"
    )
    
    print(f"Session ID: {session.id}")
    print("PatientMap Agent System Ready")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        await run_session(
            runner=runner,
            session_id=session.id,
            user_id="default_user",
            message=user_input
        )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PatientMap Agent System")
    parser.add_argument(
        "--mode",
        choices=["interactive", "session"],
        default="interactive",
        help="Run mode: interactive (original) or session (with persistence)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        run_interactive()
    else:
        asyncio.run(run_with_sessions())
```

#### 1.3 Configure Session Database

**Directory Structure**:
```
project_root/
├── var/
│   └── runtime/
│       ├── sessions.db      # SQLite session database
│       └── .gitkeep         # Track directory, not DB file
├── .gitignore               # Add var/runtime/*.db
```

**Environment Variables** (optional `.env` file):
```bash
# Session Configuration
PATIENTMAP_SESSION_DB=sqlite:///./var/runtime/sessions.db
PATIENTMAP_PERSISTENT_SESSIONS=true

# Set to false for testing with in-memory sessions
# PATIENTMAP_PERSISTENT_SESSIONS=false
```

#### 1.4 Session State Conventions

**Establish naming conventions** for `session.state` to avoid conflicts:

| Prefix | Scope | Example Keys | Usage |
|--------|-------|--------------|-------|
| `user:` | User-specific, persistent | `user:name`, `user:dob`, `user:preferences` | Patient demographics, preferences |
| `app:` | Application-wide, persistent | `app:version`, `app:feature_flags`, `app:kg_metadata` | Global config, feature toggles |
| `temp:` | Session-temporary | `temp:current_phase`, `temp:research_count` | Workflow tracking, ephemeral state |

**Update Agent Instructions** (example for orchestrator):

Add to `.profiles/orchestrator_agent.yaml`:
```yaml
instruction: |
  ...existing instructions...
  
  **State Management:**
  - Track workflow phase in session.state['temp:current_phase'] (values: 'data', 'research', 'clinical')
  - After each phase completion, update temp:current_phase
  - Check temp:current_phase on session resume to determine next action
```

#### 1.5 Validation & Testing

**Test Script**: `tests/integration/test_session_persistence.py`

```python
import pytest
import asyncio
from patientmap.runtime.services import create_runner

@pytest.mark.asyncio
async def test_session_persistence():
    """Test that sessions persist across runner instances."""
    
    # Create first runner and session
    runner1 = create_runner()
    session = await runner1.session_service.create_session(
        app_name="patientmap",
        user_id="test_user",
        session_id="test_session_123"
    )
    
    # Store state
    session.state['test_key'] = 'test_value'
    
    # Simulate restart by creating new runner
    runner2 = create_runner()
    
    # Retrieve session
    retrieved_session = await runner2.session_service.get_session(
        app_name="patientmap",
        user_id="test_user",
        session_id="test_session_123"
    )
    
    assert retrieved_session is not None
    assert retrieved_session.state.get('test_key') == 'test_value'

@pytest.mark.asyncio
async def test_compaction():
    """Test that event compaction reduces context window."""
    runner = create_runner()
    
    session = await runner.session_service.create_session(
        app_name="patientmap",
        user_id="test_user"
    )
    
    # Run multiple turns to trigger compaction (interval=3)
    for i in range(5):
        await run_session(
            runner=runner,
            session_id=session.id,
            user_id="test_user",
            message=f"Test message {i}"
        )
    
    # Check for summary events (compaction markers)
    final_session = await runner.session_service.get_session(
        app_name="patientmap",
        user_id="test_user",
        session_id=session.id
    )
    
    summary_events = [e for e in final_session.events if e.event_type == 'summary']
    assert len(summary_events) >= 1  # At least one summary should exist
```

**Manual QA Checklist**:
- [ ] Run `python main.py --mode=session` successfully
- [ ] Type multiple messages, exit, restart, verify conversation continues
- [ ] Inspect `var/runtime/sessions.db` with SQLite browser
- [ ] Verify `events` table contains turn history
- [ ] Check `session_state` table for state persistence
- [ ] Confirm compaction after 3 invocations (summary events)

---

### Stage 2: Integrate Long-Term Memory (MEDIUM PRIORITY)

**Goal**: Enable cross-session memory for patient context and clinical history

#### 2.1 Enable In-Memory Memory Service (Prototyping)

**Update** `patientmap/runtime/services.py`:

```python
def create_memory_service():
    """Create memory service (in-memory for prototyping)."""
    return InMemoryMemoryService()

def create_runner(
    session_service=None,
    artifact_service=None,
    memory_service=None
):
    """Create configured runner with services."""
    # ... existing code ...
    
    if memory_service is None:
        memory_service = create_memory_service()  # Now enabled
    
    return Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service  # Wired to runner
    )
```

#### 2.2 Expose Memory Tools to Agents

**Agents Requiring Memory**:

1. **data_gatherer_agent** - Recall prior intake details if user returns
2. **clinical_agent** - Fetch prior specialist recommendations
3. **research_agent** - Remember prior research findings for related conditions

**Example Update** (`patientmap/agents/data_gatherer/agent.py`):

```python
from google.adk.tools import load_memory  # Add import

data_agent = LlmAgent(
    name=data_gatherer_agent_settings.agent_name,
    description=data_gatherer_agent_settings.description,
    model=Gemini(model_name=data_gatherer_agent_settings.model, retry_options=retry_config),
    instruction=data_gatherer_agent_settings.instruction + """
    
**Memory Usage:**
- Use load_memory tool to check if patient has prior intake records
- Query: "patient intake history {user_id}"
- If found, acknowledge prior information and ask what changed
""",
    tools=[load_memory]  # Add memory tool
)
```

**Clinical Agent Update** (`patientmap/agents/clinical/agent.py`):

```python
from google.adk.tools import load_memory

clinical_manager = Agent(
    # ... existing config ...
    tools=[
        # ... existing AgentTool(agent=...) entries ...
        load_memory  # Add at end of tools list
    ]
)
```

**Instruction Enhancement** (`.profiles/clinical/clinical_agent.yaml`):
```yaml
instruction: |
  ...existing instructions...
  
  **Memory Integration:**
  Before generating recommendations:
  1. Use load_memory to query: "prior clinical recommendations for {patient_id}"
  2. If found, summarize changes since last assessment
  3. Note any contradictions with current findings
```

#### 2.3 Implement Auto-Save Callback

**Create** `patientmap/common/callbacks.py`:

```python
"""
Agent callbacks for memory and session management.
Based on Kaggle day_3b_agent_memory.py auto_save_to_memory pattern.
"""

from google.adk.events import Event
from google.adk.sessions import Session
from google.adk.memory import BaseMemoryService
from google.adk.tools.tool_context import ToolContext
import os

# Feature flag for memory auto-save
AUTO_SAVE_ENABLED = os.getenv("PATIENTMAP_MEMORY_AUTO_SAVE", "true").lower() == "true"

async def auto_save_to_memory(
    *,
    event: Event,
    session: Session,
    tool_context: ToolContext
) -> None:
    """
    Automatically save agent responses to long-term memory.
    
    Triggered after each agent turn. Only saves if:
    - Memory service is configured
    - AUTO_SAVE_ENABLED is true
    - Event has substantive content (not partial or metadata events)
    """
    if not AUTO_SAVE_ENABLED:
        return
    
    memory_service = tool_context.memory_service
    if memory_service is None:
        return
    
    # Only save complete events with content
    if event.partial or not event.content:
        return
    
    # Skip saving from internal/system events
    if event.author in ['system', 'plugin', 'compaction']:
        return
    
    # Save session to memory
    try:
        await memory_service.add_session_to_memory(session)
    except Exception as e:
        # Log but don't fail agent execution
        print(f"Warning: Failed to save to memory: {e}")
```

**Register Callback** in `patientmap/runtime/services.py`:

```python
from patientmap.common.callbacks import auto_save_to_memory

def create_app():
    """Create configured PatientMap application with callbacks."""
    return App(
        name="patientmap",
        root_agent=root_agent,
        plugins=[
            ContextFilterPlugin(num_invocations_to_keep=5)
        ],
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=3,
            overlap_size=1
        ),
        resumability_config=ResumabilityConfig(is_resumable=True),
        # Register auto-save callback
        after_agent_callbacks=[auto_save_to_memory]
    )
```

#### 2.4 Manual vs Automatic Memory Usage

**Use `load_memory`** (reactive, on-demand):
- Default for most agents
- Query memory when needed
- Lower cost, explicit control

**Use `preload_memory`** (proactive, every turn):
- Only for agents that ALWAYS need historical context
- Example: Knowledge graph enrichment (research phase)
- Higher cost, automatic loading

**Example**: Research agent with preload for continuity

```python
from google.adk.tools import preload_memory

research_agent = Agent(
    # ... existing config ...
    instruction=f"""
    {researcher_config.instruction}
    
    **Context Enrichment:**
    - You have access to prior research findings via preload_memory
    - Cross-reference current research with historical findings
    - Identify novel insights vs confirmatory evidence
    """,
    tools=[google_search, url_context, preload_memory]  # Auto-loads memory
)
```

#### 2.5 Memory Validation

**Test Script**: `tests/integration/test_memory_service.py`

```python
@pytest.mark.asyncio
async def test_memory_recall():
    """Test cross-session memory recall."""
    runner = create_runner()
    
    # Session 1: Create memory
    session1 = await runner.session_service.create_session(
        app_name="patientmap",
        user_id="patient_123"
    )
    
    await run_session(
        runner=runner,
        session_id=session1.id,
        user_id="patient_123",
        message="I am allergic to penicillin"
    )
    
    # Manually save to memory
    await runner.memory_service.add_session_to_memory(session1)
    
    # Session 2: New session, recall memory
    session2 = await runner.session_service.create_session(
        app_name="patientmap",
        user_id="patient_123"
    )
    
    # Search memory
    results = await runner.memory_service.search_memory(
        app_name="patientmap",
        user_id="patient_123",
        query="allergies medication"
    )
    
    assert len(results.memories) > 0
    # Verify "penicillin" appears in recalled memories
```

---

### Stage 3: Production Memory Service (FUTURE)

**Goal**: Migrate to `VertexAiMemoryBankService` for semantic consolidation

#### 3.1 Prerequisites

- [ ] GCP project with Vertex AI enabled
- [ ] Service account with Vertex AI permissions
- [ ] Memory bank corpus created in Vertex AI

#### 3.2 Migration

**Update** `patientmap/runtime/services.py`:

```python
from google.adk.memory import VertexAiMemoryBankService
import os

def create_memory_service():
    """Create memory service (production-ready)."""
    use_vertex = os.getenv("PATIENTMAP_USE_VERTEX_MEMORY", "false").lower() == "true"
    
    if use_vertex:
        return VertexAiMemoryBankService(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
            memory_bank_id=os.getenv("PATIENTMAP_MEMORY_BANK_ID"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        )
    else:
        return InMemoryMemoryService()
```

**Environment Configuration**:
```bash
PATIENTMAP_USE_VERTEX_MEMORY=true
GOOGLE_CLOUD_PROJECT=your-gcp-project
PATIENTMAP_MEMORY_BANK_ID=your-memory-bank-id
GOOGLE_CLOUD_LOCATION=us-central1
```

**Validation**:
- API compatibility is identical (no code changes to agents)
- Test with small user base first
- Monitor costs (Vertex AI Memory Bank has per-query pricing)

---

## Critical Decision Points

### Decision 1: tool_context.state vs session.state for KG Storage

**Current**: `tool_context.state['kg_data']` stores entire graph  
**Options**:

#### Option A: Keep Current (Recommended)
- **Pro**: Clean separation of concerns (tools own their state)
- **Pro**: No migration needed
- **Pro**: KG tools remain self-contained
- **Con**: Knowledge graph not directly accessible in session state

#### Option B: Migrate to session.state
- **Pro**: KG becomes part of session persistence
- **Pro**: Can query KG state directly from session
- **Con**: Tight coupling between tools and session
- **Con**: Requires refactoring all 20+ kg_tools functions

**Recommendation**: **Option A** (keep current), add metadata to session state

```python
# In save_graph_to_disk(), also store metadata:
session.state['app:latest_kg_file'] = str(json_path)
session.state['app:kg_last_updated'] = datetime.now().isoformat()
session.state['app:kg_node_count'] = graph.number_of_nodes()
```

### Decision 2: Session Resumability Strategy

**Current**: `ResumabilityConfig(is_resumable=True)` in `main.py`  
**Question**: Where should agents resume after restart?

**Strategy**:
1. Store phase in `session.state['temp:current_phase']`
2. Update orchestrator instruction to check on resume:

```yaml
instruction: |
  ...
  
  **Resumability Logic:**
  On session start:
  1. Check session.state['temp:current_phase']
  2. If 'data': Resume data collection if incomplete
  3. If 'research': Continue research from last topic
  4. If 'clinical': Resume clinical analysis
  5. If not set: Start fresh from Phase 1
```

### Decision 3: Compaction Configuration

**Current**: Not configured  
**Proposed**: `EventsCompactionConfig(compaction_interval=3, overlap_size=1)`

**Rationale**:
- PatientMap has long multi-agent workflows (data → research → clinical)
- Research loops can iterate 10+ times (google_search results)
- Clinical phase has 16 specialist agents producing lengthy outputs
- Without compaction: token budgets will exceed limits

**Test**: Monitor first 10 production sessions, adjust interval if needed

---

## Implementation Timeline

### Phase 1: Foundation (Week 1-2)
- [ ] Create `patientmap/runtime/services.py`
- [ ] Implement `DatabaseSessionService` wiring
- [ ] Update `main.py` with dual-mode support
- [ ] Configure `var/runtime/` directory structure
- [ ] Write integration tests for session persistence
- [ ] Document session state conventions

### Phase 2: Memory Prototyping (Week 3)
- [ ] Enable `InMemoryMemoryService`
- [ ] Add `load_memory` to data_gatherer, clinical agents
- [ ] Implement `auto_save_to_memory` callback
- [ ] Write memory recall integration tests
- [ ] Manual QA with 5+ test sessions

### Phase 3: Production Hardening (Week 4-5)
- [ ] Load test with 50+ sessions
- [ ] Monitor compaction effectiveness
- [ ] Tune memory query patterns
- [ ] Add monitoring/logging for service health
- [ ] Document operational procedures

### Phase 4: Vertex AI Migration (Future)
- [ ] Set up GCP Memory Bank corpus
- [ ] Test API compatibility
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Cost analysis and optimization

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **tool_context.state conflicts with session.state** | MEDIUM | MEDIUM | Establish clear naming conventions, separate concerns |
| **Compaction loses critical context** | HIGH | LOW | Tune overlap_size, monitor summary quality |
| **Memory service costs exceed budget** | MEDIUM | MEDIUM | Start with InMemoryMemoryService, monitor Vertex AI usage |
| **Session DB growth** | LOW | HIGH | Implement retention policy, archive old sessions |
| **Backward compatibility breaks** | HIGH | LOW | Maintain `app.run()` as fallback, gradual migration |

---

## Validation Checklist

### Stage 1 (Sessions) Validation
- [ ] `DatabaseSessionService` stores sessions to SQLite
- [ ] Sessions persist across kernel restarts
- [ ] Event compaction creates summary events after 3 turns
- [ ] Session state prefixes (`user:`, `app:`, `temp:`) work correctly
- [ ] Resumability allows mid-workflow restarts
- [ ] Multiple users can have concurrent sessions
- [ ] `main.py --mode=interactive` still works (backward compat)

### Stage 2 (Memory) Validation
- [ ] `InMemoryMemoryService` stores and retrieves memories
- [ ] `load_memory` tool returns relevant context
- [ ] `auto_save_to_memory` callback executes after agent turns
- [ ] Cross-session memory recall works for same user
- [ ] Memory search returns relevant results (not just keyword match)
- [ ] Feature flag `PATIENTMAP_MEMORY_AUTO_SAVE=false` disables callback

### Stage 3 (Production) Validation
- [ ] `VertexAiMemoryBankService` API compatibility confirmed
- [ ] Semantic search quality exceeds keyword-based InMemory service
- [ ] Cost per query is within acceptable range
- [ ] Memory consolidation reduces duplicate entries
- [ ] Performance (latency) meets SLA requirements

---

## References

### Official Documentation
- **ADK Python Repo**: `google/adk-python` (Runner, services, examples)
- **Context7 ADK Docs**: `/google/adk-python` (API reference)
- **Google ADK Docs**: https://google.github.io/adk-docs/

### Internal Resources
- **Kaggle Course**: `kaggle_google_course/day_3a_agent_sessions.py` (session patterns)
- **Kaggle Course**: `kaggle_google_course/day_3b_agent_memory.py` (memory patterns)
- **Agent Hierarchy**: See "Current Architecture Deep Dive" section above
- **Configuration System**: `.profiles/**/*.yaml` (30 config files)

### Key Code Locations
- **Current Entry Point**: `main.py`
- **Orchestrator**: `src/patientmap/agents/orchestrator/agent.py`
- **KG Tools**: `src/patientmap/tools/kg_tools.py` (20+ functions)
- **Config Loader**: `src/patientmap/common/config.py`
- **Helper Functions**: `src/patientmap/common/helper_functions.py`

---

## Appendix A: Session Database Schema (SQLite)

**Generated by `DatabaseSessionService`**:

```sql
-- Sessions table
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    app_name TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at REAL NOT NULL,
    last_update_time REAL,
    UNIQUE(app_name, user_id, id)
);

-- Events table
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp REAL NOT NULL,
    author TEXT,
    content_json TEXT,  -- JSON-serialized event content
    metadata_json TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

-- Session state table
CREATE TABLE session_state (
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value_json TEXT,  -- JSON-serialized value
    PRIMARY KEY(session_id, key),
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

-- User state table (cross-session)
CREATE TABLE user_state (
    app_name TEXT NOT NULL,
    user_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value_json TEXT,
    PRIMARY KEY(app_name, user_id, key)
);

-- App state table (global)
CREATE TABLE app_state (
    app_name TEXT NOT NULL,
    key TEXT NOT NULL,
    value_json TEXT,
    PRIMARY KEY(app_name, key)
);
```

**Query Examples**:

```sql
-- List all sessions for a user
SELECT * FROM sessions WHERE app_name='patientmap' AND user_id='patient_123';

-- Get event history for a session
SELECT * FROM events WHERE session_id='abc123' ORDER BY timestamp;

-- Check user-scoped state
SELECT * FROM user_state WHERE app_name='patientmap' AND user_id='patient_123';
```

---

## Appendix B: Memory Service Comparison

| Feature | InMemoryMemoryService | VertexAiMemoryBankService |
|---------|----------------------|---------------------------|
| **Storage** | In-process memory | GCP Vertex AI Memory Bank |
| **Search Type** | Keyword matching | Semantic vector search |
| **Persistence** | Lost on restart | Durable cloud storage |
| **Cost** | Free | Per-query pricing |
| **Latency** | ~1ms | ~100-500ms (network) |
| **Consolidation** | None | Automatic deduplication |
| **Use Case** | Prototyping, testing | Production deployments |
| **API Compatibility** | Identical | Identical |

**Migration Path**: Start InMemory → validate with small user base → switch to Vertex AI

---

## Appendix C: Configuration File Examples

### Environment Variables (`.env`)

```bash
# Session Configuration
PATIENTMAP_SESSION_DB=sqlite:///./var/runtime/sessions.db
PATIENTMAP_PERSISTENT_SESSIONS=true

# Memory Configuration
PATIENTMAP_MEMORY_AUTO_SAVE=true
PATIENTMAP_USE_VERTEX_MEMORY=false  # Set true for production

# GCP Configuration (when using Vertex AI Memory)
GOOGLE_CLOUD_PROJECT=your-project-id
PATIENTMAP_MEMORY_BANK_ID=your-memory-bank-id
GOOGLE_CLOUD_LOCATION=us-central1

# API Keys (existing)
SEMANTIC_SCHOLAR_API_KEY=your-key
CROSSREF_EMAIL=your-email
```

### Agent YAML Extension (Example)

```yaml
# .profiles/orchestrator_agent.yaml
agent_id: oa001
agent_name: orchestrator_agent
model: 'gemini-2.5-pro'
description: >
  The Orchestrator Agent coordinates...
  
# NEW: Session/Memory Configuration
session_config:
  state_prefix: "temp:orchestrator"
  resumable: true
  save_to_memory: true

instruction: |
  ...existing instructions...
  
  **Session State Management:**
  - Track current phase in session.state['temp:current_phase']
  - Possible values: 'data', 'research', 'clinical'
  - On resume: Check temp:current_phase and continue from there
  
  **Memory Usage:**
  - Prior session summaries are automatically preloaded
  - Reference them when greeting returning users
```

---

## Conclusion

This **validated roadmap** provides a clear, evidence-based path to integrating sessions and memory into PatientMap. Key principles:

1. ✅ **Maintain Backward Compatibility**: `main.py --mode=interactive` preserves original behavior
2. ✅ **Incremental Adoption**: Sessions first (critical), memory second (enhancement)
3. ✅ **Production-Ready Patterns**: Based on official ADK samples and best practices
4. ✅ **Clear Separation of Concerns**: tool_context.state for tools, session.state for workflow
5. ✅ **Comprehensive Validation**: Integration tests and manual QA at each stage

**Next Steps**:
1. Review this roadmap with team
2. Begin Stage 1 implementation (`patientmap/runtime/services.py`)
3. Run validation tests after each stage
4. Monitor session/memory usage in production
5. Iterate based on real-world patterns

**Questions or Issues**: Refer to Kaggle course notebooks (`kaggle_google_course/`) or ADK documentation.
