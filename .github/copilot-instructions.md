# PatientMap Copilot Instructions
## System Overview
- Core app runs via `main.py` using Google ADK `App` with `root_agent` orchestrating sequential data → research → clinical phases.
- Runtime depends on `src` being on `sys.path`; new modules should follow existing prepend pattern before local imports.
- Agents use Gemini models with shared retry policy from `patientmap/common/helper_functions.py`; reuse `retry_config` when adding API calls.
## Config-Driven Agents
- Agent prompts, model choices, and workflow scripts live in `.profiles/**`; update YAML alongside code so LLM behavior stays in sync.
- Each agent module loads a specific YAML; missing files raise runtime errors (e.g., orchestrator expects `.profiles/orchestrator_agent.yaml`).
- When adding agents, expose a `root_agent` for imports and register them in orchestrator or clinical tool lists as needed.
## Knowledge Graph Pipeline
- Knowledge graph tools in `src/patientmap/tools/kg_tools.py` store graphs inside `tool_context.state`; never bypass helpers when mutating the graph.
- Builder agents must batch mutations with `bulk_add_nodes` and `bulk_add_relationships`; the checker only reads/validates and exits loops via `exit_loop`.
- Final artifacts are timestamped into `knowledge_graphs/`; builders defer saving until the checker signals completion.
## Research Workflow
- Research loop (`patientmap/agents/research/agent.py`) first generates topics, then iterates searches using ADK tools `google_search` and `url_context`.
- Maintain the "COMPLETED:" progress markers and terminal "RESEARCH COMPLETE" string—other agents rely on them to advance phases.
## Clinical Specialists
- `patientmap/agents/clinical/agent.py` exposes specialists as ADK `AgentTool` instances; call only the relevant tools and justify selections in outputs.
- Specialist configs live under `.profiles/clinical/*_agent.yaml`; consistent naming (e.g., `cardiology_agent.yaml`) keeps loader paths working.
## Data Intake
- Data manager coordinates `data_gatherer` → `kg_initialiser` in one turn; respect its mandatory sequencing when extending prompts or tooling.
- Triage agent instructions enforce an empathetic script; changes should stay aligned with `.profiles/data/data_gatherer_agent.yaml`.
## Utilities & Error Handling
- Use `patientmap/common/helper_functions.handle_tool_error` for ADK tool callbacks so failures degrade gracefully without breaking loops.
- Logging is suppressed via `patientmap/common/logging.configure_logging`; import it before LangChain tools to avoid aiohttp shutdown noise.
## Developer Workflow
- Python 3.13 project managed by `uv`; install with `uv sync` (or `pip install -e .`) and run the app via `python main.py`.
- Set required environment variables (`SEMANTIC_SCHOLAR_API_KEY`, `CROSSREF_EMAIL`, optional `CLINICAL_TRIALS_API_KEY`) before invoking agents.
- No automated tests ship today; exercise modules through ADK runners (see orchestrator `__main__` blocks) when validating changes.
## External Integrations
- Literature tools wrap LangChain community clients (Google Scholar, PubMed, Semantic Scholar, Wikipedia) in `patientmap/tools/research_tools.py`; ensure API keys in `.env` are loaded via `load_dotenv()`.
- Knowledge graph tooling depends on NetworkX node-link JSON; keep properties JSON-serializable for persistence.
## Troubleshooting
- If agents stall, check that completion signals from sub-agents match the YAML instructions—phase transitions rely on exact phrases.
- Missing YAML or graph files trigger RuntimeErrors; create profiles under `.profiles` before running loops to avoid early termination.
