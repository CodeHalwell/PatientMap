# Session & Memory Integration Roadmap

This note distills the most relevant patterns from Google's Kaggle ADK course (`kaggle_google_course/day_3a_agent_sessions.py`, `day_3b_agent_memory.py`) and the latest ADK Python docs for upgrading PatientMap's runtime. The goal is to make the orchestrated workflow resilient across user conversations while capturing durable clinical context.

## 1. Current State & Architecture (2025-11-14 Assessment)

### Runtime Environment
- **Entry point**: `uv run adk web agents` from `src/patientmap/` auto-discovers the `orchestrator` agent via `__init__.py` export
- **Agent discovery**: ADK CLI loads `patientmap.agents.orchestrator` and finds `root_agent` export
- **Service defaults**: ADK web server creates its own `Runner` with in-memory services (`InMemorySessionService`, `InMemoryMemoryService`, `InMemoryArtifactService`)
- **No custom services**: Zero configuration for persistent sessions, memory, or observability plugins

### Agent Hierarchy ✅ COMPLETED
The hierarchical agent structure has been **successfully implemented**:
```
orchestrator/
├── orchestrator_agent.yaml (co-located!)
├── data/
│   ├── data_manager_agent.yaml
│   ├── gatherer/
│   │   └── data_gatherer_agent.yaml
│   └── kg_initialiser/
│       └── build_loop/ (builder + checker)
├── research/
│   ├── research_manager_agent.yaml
│   ├── topics/ (research_topics.yaml)
│   ├── search_loop/ (research + reviewer)
│   └── kg_enrichment/ (enricher + checker)
├── clinical/
│   ├── manager/ (clinical_agent.yaml + 16 specialists)
│   ├── checker/
│   └── kg_enrichment/
└── report/
    ├── report_manager_agent.yaml
    ├── roundtable/ (3 review agents)
    └── final_report/
```
**Key improvements**: All configs are now **co-located** with agent code (no more `.profiles/` remote paths), relative imports throughout, clean `./config.yaml` loading pattern.

### State Management Architecture
**Tool Context State (`tool_context.state`)**:
- Used exclusively for knowledge graph storage via `kg_data` key
- NetworkX graph serialized as node-link JSON
- 20+ KG tools (`kg_tools.py`) read/write to this single state key
- Persists only within a single ADK session (lost on server restart)

**Session State (ADK `session.state`)**: **NOT USED**
- No agents read or write to `session.state`
- Zero session-scoped persistence (e.g., user demographics, workflow phase tracking)
- Cannot resume interrupted workflows across sessions

**Memory Service**: **NOT USED**
- No calls to `load_memory` or `preload_memory` tools
- No `auto_save_to_memory` callback registered
- No cross-session context (e.g., prior visit history, recurring conditions)

### Critical Gaps
1. **Session resumability impossible**: KG data in `tool_context.state['kg_data']` vanishes when web server restarts—patients must start over
2. **No workflow phase tracking**: Orchestrator cannot detect "we're in research phase" after session break
3. **Zero cross-session learning**: Clinical specialists can't recall "this patient had adverse reaction to X drug last visit"
4. **Observability blind spots**: `LoggingPlugin` exists but isn't wired to Runner; no trace/debug capabilities in ADK web UI
5. **Config loading fragility**: Hardcoded `./config.yaml` paths fail if working directory changes during `adk web` discovery

## 2. Strategic Session & Memory Integration

### High-Value Integration Points (Prioritized)

#### **Priority 1: KG Persistence via Session State**
**Problem**: `tool_context.state['kg_data']` evaporates on server restart → patients lose all intake/research data  
**Solution**: Migrate KG storage to `session.state` for durable persistence

**Implementation**:
```python
# In kg_tools.py, replace _get_graph() and _save_graph()
def _get_graph(tool_context: ToolContext) -> nx.DiGraph:
    # Try session state first (persistent), fallback to tool context (ephemeral)
    if hasattr(tool_context, 'session') and tool_context.session:
        if 'app:kg_data' in tool_context.session.state:
            data = tool_context.session.state['app:kg_data']
            return nx.node_link_graph(data, directed=True, edges="links")
    # Fallback for non-session contexts (tests)
    if 'kg_data' in tool_context.state:
        data = tool_context.state['kg_data']
        return nx.node_link_graph(data, directed=True, edges="links")
    return nx.DiGraph()

def _save_graph(graph: nx.DiGraph, tool_context: ToolContext) -> None:
    data = nx.node_link_data(graph, edges="links")
    if hasattr(tool_context, 'session') and tool_context.session:
        tool_context.session.state['app:kg_data'] = data  # Persistent
        tool_context.session.state['app:kg_last_updated'] = datetime.now().isoformat()
        tool_context.session.state['app:kg_node_count'] = graph.number_of_nodes()
    else:
        tool_context.state['kg_data'] = data  # Fallback
```
**Impact**: Patients can close browser, server can restart, work resumes from exact KG state.

#### **Priority 2: Workflow Phase Tracking**
**Problem**: Orchestrator has no memory of "we completed data phase, now in research"  
**Solution**: Track phase progression in `session.state['temp:current_phase']`

**Implementation**:
```python
# In orchestrator/agent.py instruction (YAML):
instruction: |
  **Phase Tracking**:
  - Check session.state['temp:current_phase'] on each turn
  - Valid phases: 'data', 'research', 'clinical', 'report'
  - After sub-agent completes, update: session.state['temp:current_phase'] = 'next_phase'
  - If phase is set and sub-agent confirms completion, proceed to next
  - If session resumes mid-phase, acknowledge and continue from checkpoint
```
**Impact**: Users can pause/resume 2-hour research workflows without starting over.

#### **Priority 3: Patient Demographics in User State**
**Problem**: Data gatherer re-asks name, DOB, conditions every session  
**Solution**: Store persistent demographics in `session.state['user:*']` keys

**Implementation** (data gatherer instruction):
```yaml
instruction: |
  **Memory-Aware Intake**:
  1. Check session.state['user:name'], ['user:dob'], ['user:conditions']
  2. If found, greet by name: "Welcome back, {name}. Last visit: {date}."
  3. Ask: "Has anything changed since last time?" (vs full intake)
  4. Save/update: session.state['user:name'], ['user:dob'], ['user:primary_conditions']
```
**Impact**: Returning patients feel recognized, intake time cut by 70%.

### Infrastructure Layer

#### **App Wrapper for Custom Services**
Since `adk web agents` auto-discovers agents via `__init__.py` exports, we create an `App` wrapper:

**Update `src/patientmap/agents/orchestrator/__init__.py`**:
     ```python
     from google.adk.apps import App, EventsCompactionConfig, ResumabilityConfig
     from google.adk.plugins import ContextFilterPlugin
     from google.adk.sessions import DatabaseSessionService
     from google.adk.artifacts import InMemoryArtifactService
     from google.adk.memory import InMemoryMemoryService
     from .agent import root_agent
     
     # Create app with custom services
     app = App(
         name="orchestrator",
         root_agent=root_agent,
         plugins=[ContextFilterPlugin(num_invocations_to_keep=5)],
         events_compaction_config=EventsCompactionConfig(compaction_interval=3, overlap_size=1),
         resumability_config=ResumabilityConfig(is_resumable=True),
     )
     
     # Export both for flexibility
     __all__ = ["root_agent", "app"]
     ```
   - **Alternative**: Create a separate `patientmap/runtime/app.py` module that ADK can discover as a standalone app if the CLI supports custom app locations.

2. **Persist sessions with SQLite first, then cloud**
   - `DatabaseSessionService` (mirroring the Kaggle example) gives durable transcripts without extra infra. Once stable, migrate to `VertexAiSessionService` to align with GCP managed storage.
   - Store the DB file beneath `var/runtime/` (git-ignored) so webinars and tests can inspect sessions via SQL, as shown in the course `check_data_in_db()` helper.

3. **Adopt compaction defaults**
   - PatientMap conversations span data intake → research → clinical; compaction prevents multi-tool histories from blowing token budgets. Use the Kaggle pattern (interval=3, overlap=1) and adjust once we observe transcript length in logs.

4. **Session-state conventions**
   - Normalize key prefixes (`user:*`, `app:*`, `temp:*`) as in `day_3a_agent_sessions.py` to avoid collisions between triage, research, and clinical agents. Document these prefixes inside `.profiles` instructions so agents store flags consistently (e.g., `user:name`, `app:graph_id`).

## 3. Memory Enablement Roadmap
1. **Stage 1 – Prototype (local dev)**
   - Enable `InMemoryMemoryService` to validate APIs. Expose the built-in tools from ADK (`load_memory`, `preload_memory`) to high-value agents:
     - `patientmap/agents/data_manager/agent.py`: allow data gatherer to recall prior intake details if the user resumes mid-way.
     - `patientmap/agents/clinical/agent.py`: attach `load_memory` so the director can fetch prior specialist outputs when a session restarts.

2. **Stage 2 – Automatic persistence**
   - Copy the Kaggle callback (`auto_save_to_memory`) into `patientmap/common/callbacks.py` and register it through the `Runner` so every agent turn writes to memory when `memory_service` is present.
   - Guard the callback so it skips saving during dry-run/test sessions.

3. **Stage 3 – Production-grade memory**
   - Swap to `VertexAiMemoryBankService` for semantic consolidation. ADK docs emphasise identical APIs, so only the constructor and credentials change.
   - Define memory schemas aligned to PatientMap's domain (e.g., conditions, medications, social determinants) to improve retrieval quality.

4. **Tooling guidance**
   - Use `load_memory` (reactive) by default; upgrade to `preload_memory` for agents that depend on historical facts every turn (e.g., knowledge-graph enrichment loops). The Kaggle notebooks highlight that `preload_memory` increases cost, so reserve it for core flows.

## 4. Implementation Steps
- [ ] Research ADK CLI's auto-discovery mechanism to determine best approach for injecting custom `App` configuration (check if `adk web` can accept app exports vs agent exports).
- [ ] Update `src/patientmap/agents/orchestrator/__init__.py` to export a configured `App` instance with custom services, or create a separate app module that ADK can discover.
- [ ] Introduce configuration flags (env vars) for session DB URL, compaction thresholds, and memory backend, defaulting to the local-friendly settings above.
- [ ] Wire `auto_save_to_memory` as an `after_agent_callback` on top-level agents (or within the runner) and expose a feature flag to disable it during bulk backfills.
- [ ] Extend agent tool lists (`clinical`, `research`, `data_manager`) with `load_memory`/`preload_memory` once the runner supplies a memory service.
- [ ] Document state-key conventions in `.profiles` YAML so prompt instructions stay aligned with the new memory behaviors.

## 5. Verification Checklist
- Write integration tests that:
  1. Trigger two sequential turns and assert `DatabaseSessionService` stores events (query the SQLite `events` table, as demonstrated in `day_3a`).
  2. Save a fact into memory, start a new session, and assert an agent using `load_memory` recalls it (mirrors `day_3b` "birthday" example).
  3. Confirm compaction emits summary events after the configured interval.
- Add manual QA scripts leveraging the Kaggle `run_session` helper pattern to inspect sessions and memory entries during development.

## 6. Further Reading
- Kaggle 5-Day Agents Course notebooks (bundled under `kaggle_google_course/`) for runnable reference implementations.
- ADK Python reference: `/google/adk-python` (Context7) for `Runner`, `DatabaseSessionService`, `InMemoryMemoryService`, and `load_memory` APIs.
- ADK Docs on context compaction & memory: https://google.github.io/adk-docs/context/compaction/ and https://google.github.io/adk-docs/sessions/memory/.

Implementing the steps above will let PatientMap maintain patient context across long-running multi-agent workflows, resume interrupted research phases, and gradually build a reusable clinical memory base.
