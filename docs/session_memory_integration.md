# Session & Memory Integration Roadmap

This note distills the most relevant patterns from Google's Kaggle ADK course (`kaggle_google_course/day_3a_agent_sessions.py`, `day_3b_agent_memory.py`) and the latest ADK Python docs for upgrading PatientMap's runtime. The goal is to make the orchestrated workflow resilient across user conversations while capturing durable clinical context.

## 1. Current Gaps
- The application runs via **`uv run adk web agents`** from `src/patientmap/`, which uses ADK's auto-discovery to find and load the `orchestrator` agent. There is no explicit `main.py` entry point being used in the actual workflow.
- ADK's `adk web` command automatically creates an in-memory web server with default services (`InMemorySessionService`, `InMemoryMemoryService`). No custom `Runner`, session persistence, or memory configuration is applied.
- The `orchestrator` agent is discovered via its `__init__.py` export (`from .agent import root_agent`), and the ADK CLI handles all runtime wiring internally.
- No persistent session store is configured, so user turns disappear between server restarts; knowledge graph phases cannot be resumed mid-way.
- Long-term memory is unused; agents rely solely on single-session state (`tool_context.state`) and YAML prompts. Cross-session personalization is impossible.

### Field Audit Notes (2025-11-13)
- **Actual runtime**: `uv run adk web agents` from `src/patientmap/` auto-discovers `agents/orchestrator/` via `__init__.py` export. The root `main.py` is **not used** in production workflow.
- ADK's web server provides its own `Runner` with default in-memory services. No `EventsCompactionConfig` or custom service wiring is configured.
- `patientmap/agents/orchestrator/agent.py` contains a `__main__` block with `Runner` setup, but this is only for standalone testing and never executed in the ADK web workflow.
- There is no `patientmap/runtime/` package yet. To customize sessions/memory, we need to either:
  1. Create a custom ADK app wrapper that the CLI can discover, or
  2. Use ADK's configuration mechanisms (if available) to inject custom services
- No references to `DatabaseSessionService`, `VertexAiSessionService`, or custom `MemoryService` appear anywhere outside of the Kaggle notebooks, confirming that Stage 1 (sessions) has not begun.

## 2. Session Management Plan
1. **Centralize runtime wiring for ADK auto-discovery**
   - Since `adk web agents` auto-discovers agents via `__init__.py` exports, we need to create an `App` wrapper that the CLI can discover.
   - Create `src/patientmap/agents/orchestrator/__init__.py` that exports an `App` instead of just `root_agent`:
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
