# Agent Restructuring Migration Plan

**Date**: 2025-01-XX  
**Project**: PatientMap  
**Goal**: Restructure flat agent directory into hierarchical structure reflecting actual agent relationships

---

## Latest Findings (2025-11-13)

Latest repo audit (branch `update/agents`, commit head as of 2025-11-13) surfaces a few critical deltas versus the original January plan:

- **Hierarchy migration complete** – The agent directory structure **has been reorganized**: `src/patientmap/agents/` now contains only `orchestrator/` with hierarchical subdirs (`data/`, `research/`, `clinical/`, `report/`). Sub-agents live under their respective phases (e.g., `data/gatherer/`, `clinical/manager/specialists/`), so the directory structure matches the proposed design. Legacy flat folders no longer exist at the top level.
- **Config files remain remote** – Despite the hierarchy migration, all YAML configs still live under `.profiles/**`. Agents continue walking the filesystem (e.g., `Path(__file__).parent.parent.parent.parent.parent / ".profiles"`) to load them. Co-located `config.yaml` files have not been created, meaning config management still suffers from the path complexity issues.
- **Observability plan pending** – `patientmap/common/logging.py` defines a helper to instantiate ADK's `LoggingPlugin`, but no agent or runner imports it. This diverges from Kaggle Day 4A guidance where the plugin is registered directly on the `Runner`.
- **FastMCP unused** – `fastmcp>=2.13.0.2` ships in `pyproject.toml`, and the Google ADK guide (`guides/09_Google_ADK_Framework.md`) documents how to expose agents via MCP, yet no MCP server exists under `src/` and no FastMCP entry point has been wired.
- **Evaluation assets missing** – A repo-wide search shows no `*.evalset.json`, `*.test.json`, or `test_config.json` files outside of the Kaggle notebooks. Day 4B's evaluation workflow has not been applied to PatientMap.
- **Long-running + approvals absent** – There are no references to `LongRunningTool`, `ApprovalTool`, or any custom waiting states. All KG mutations and clinical recommendations run synchronously without human-in-the-loop checkpoints.

These findings keep the original migration plan relevant, but the scope now explicitly includes observability, MCP exposure, and evaluation scaffolding so that the hierarchy change unlocks downstream tooling (tracing, MCP, CI evals) instead of existing as an isolated refactor.

---

## Visual Diagram: Current vs Proposed Structure

### Current Structure (Flat)

```
src/patientmap/agents/
├── orchestrator/          ← root_agent, coordinates 3 phases
├── data_manager/          ← Phase 1 coordinator
├── data_gatherer/         ← Used by data_manager
├── data_extraction/       ← (unused?)
├── kg_initialiser/        ← Used by data_manager
├── knowledge_graph/       ← Used by research
├── research/              ← Phase 2 coordinator
├── research_manager/      ← (unused?)
├── clinical/              ← Phase 3 coordinator
│   └── cardiology/        ← 16 specialist subdirs
│   └── neurology/
│   └── ...
├── communication/         ← (unused?)
├── format_agent/          ← (unused?)
└── reviewer/              ← (unused?)

Problems:
❌ Unclear parent-child relationships
❌ Complex import paths (sys.path manipulation)
❌ Config files separated in .profiles/
❌ No visual indication of hierarchy
❌ Hard to identify which agents are actually used
```

### Proposed Structure (Hierarchical)

```
src/patientmap/agents/
└── orchestrator/                           ← Entry point (root_agent)
    ├── __init__.py
    ├── agent.py                            ← Coordinates 3 sequential phases
    ├── config.yaml                         ← Co-located configuration
    │
    ├── data/                               ← Phase 1: Data Collection & KG Init
    │   ├── __init__.py
    │   ├── agent.py                        ← data_manager_agent
    │   ├── config.yaml
    │   │
    │   ├── gatherer/                       ← Triage/intake agent
    │   │   ├── __init__.py
    │   │   ├── agent.py                    ← data_gatherer_agent
    │   │   └── config.yaml
    │   │
    │   └── kg_initialiser/                 ← Knowledge graph initialization
    │       ├── __init__.py
    │       ├── agent.py                    ← kg_initialiser_agent (coordinator)
    │       ├── config.yaml
    │       │
    │       ├── planning/                   ← Plans KG structure from patient data
    │       │   ├── __init__.py
    │       │   ├── agent.py                ← planning_agent
    │       │   └── config.yaml
    │       │
    │       └── build_loop/                 ← LoopAgent: build → check → iterate
    │           ├── __init__.py
    │           │
    │           ├── builder/                ← Creates/updates graph
    │           │   ├── __init__.py
    │           │   ├── agent.py            ← build_agent
    │           │   └── config.yaml
    │           │
    │           └── checker/                ← Validates and calls exit_loop
    │               ├── __init__.py
    │               ├── agent.py            ← logic_checker_agent
    │               └── config.yaml
    │
    ├── research/                           ← Phase 2: Literature Research
    │   ├── __init__.py
    │   ├── agent.py                        ← research_root_agent (coordinator)
    │   ├── config.yaml
    │   │
    │   ├── topics/                         ← Generates research topics
    │   │   ├── __init__.py
    │   │   ├── agent.py                    ← research_topics agent
    │   │   └── config.yaml
    │   │
    │   ├── search_loop/                    ← LoopAgent: iterative literature search
    │   │   ├── __init__.py
    │   │   │
    │   │   └── researcher/                 ← Conducts searches (google_search, url_context)
    │   │       ├── __init__.py
    │   │       ├── agent.py                ← research_agent
    │   │       └── config.yaml
    │   │
    │   └── kg_enrichment/                  ← Enriches KG with findings
    │       ├── __init__.py
    │       │
    │       ├── enricher/                   ← Adds research to graph
    │       │   ├── __init__.py
    │       │   ├── agent.py                ← knowledge_graph_agent
    │       │   └── config.yaml
    │       │
    │       └── checker/                    ← Validates enrichment
    │           ├── __init__.py
    │           ├── agent.py                ← enrichment_checker
    │           └── config.yaml
    │
    └── clinical/                           ← Phase 3: Clinical Analysis
        ├── __init__.py
        ├── agent.py                        ← clinical_loop_agent (coordinator)
        ├── config.yaml
        │
        ├── manager/                        ← Routes to specialists
        │   ├── __init__.py
        │   ├── agent.py                    ← clinical_manager
        │   ├── config.yaml
        │   │
        │   └── specialists/                ← 16 specialist agents
        │       ├── __init__.py
        │       ├── cardiology/
        │       │   ├── __init__.py
        │       │   ├── agent.py
        │       │   └── config.yaml
        │       ├── neurology/
        │       │   ├── __init__.py
        │       │   ├── agent.py
        │       │   └── config.yaml
        │       ├── psychiatry/
        │       │   ├── __init__.py
        │       │   ├── agent.py
        │       │   └── config.yaml
        │       ├── endocrinology/
        │       ├── clinical_pharmacy/
        │       ├── gastroenterology/
        │       ├── geriatrics/
        │       ├── hematology/
        │       ├── nephrology/
        │       ├── pulmonology/
        │       ├── physical_medicine_rehabilitation/
        │       ├── infectious_disease/
        │       ├── nutrition_dietetics/
        │       ├── pain_medicine/
        │       ├── rheumatology/
        │       └── palliative_care/
        │
        └── checker/                        ← Validates clinical outputs
            ├── __init__.py
            ├── agent.py                    ← checker_agent
            └── config.yaml

Benefits:
✅ Visual hierarchy matches code hierarchy
✅ Clean relative imports (no sys.path manipulation)
✅ Co-located configs (easier maintenance)
✅ Clear parent-child relationships
✅ Easier testing (test each subtree independently)
✅ Better modularity and encapsulation
```

---

## Migration Strategy

### Phase 0: Preparation (Pre-Migration)

**Duration**: 1-2 hours  
**Risk**: Low

#### 0.1 Backup Current State

```powershell
# Create backup branch
git checkout -b backup/pre-restructure
git add .
git commit -m "Backup before agent restructuring"
git push origin backup/pre-restructure

# Return to working branch
git checkout update/agents
```

#### 0.2 Identify Unused Agents

Based on analysis, these appear unused:
- `communication/` - No imports found
- `format_agent/` - No imports found
- `reviewer/` - No imports found
- `research_manager/` - No imports found
- `data_extraction/` - No imports found

**Action**: Move to `src/patientmap/agents/_deprecated/` directory

```powershell
# Create deprecated directory
New-Item -ItemType Directory -Path "src/patientmap/agents/_deprecated" -Force

# Move unused agents
Move-Item "src/patientmap/agents/communication" "src/patientmap/agents/_deprecated/"
Move-Item "src/patientmap/agents/format_agent" "src/patientmap/agents/_deprecated/"
Move-Item "src/patientmap/agents/reviewer" "src/patientmap/agents/_deprecated/"
Move-Item "src/patientmap/agents/research_manager" "src/patientmap/agents/_deprecated/"
Move-Item "src/patientmap/agents/data_extraction" "src/patientmap/agents/_deprecated/"
```

#### 0.3 Run Current Tests

```powershell
# Ensure all tests pass before migration
python -m pytest tests/ -v

# Or if using unittest
python -m unittest discover tests/
```

---

### Phase 1: Data Phase Restructuring

**Duration**: 2-3 hours  
**Risk**: Medium  
**Target**: `data_manager`, `data_gatherer`, `kg_initialiser`

#### 1.1 Create New Directory Structure

```powershell
# Create data phase structure
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/data" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/data/gatherer" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/data/kg_initialiser" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/data/kg_initialiser/planning" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/data/kg_initialiser/build_loop" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/data/kg_initialiser/build_loop/builder" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/data/kg_initialiser/build_loop/checker" -Force
```

#### 1.2 Copy Config Files

```powershell
# Copy YAML configs to new locations
Copy-Item ".profiles/data/data_manager_agent.yaml" "src/patientmap/agents/orchestrator/data/config.yaml"
Copy-Item ".profiles/data/data_gatherer_agent.yaml" "src/patientmap/agents/orchestrator/data/gatherer/config.yaml"
Copy-Item ".profiles/knowledge/kg_initialiser.yaml" "src/patientmap/agents/orchestrator/data/kg_initialiser/config.yaml"
Copy-Item ".profiles/knowledge/kg_checker_agent.yaml" "src/patientmap/agents/orchestrator/data/kg_initialiser/build_loop/checker/config.yaml"
```

#### 1.3 Migrate Agent Files

See **Example Refactored Code** section below for detailed code changes.

**Files to migrate**:
1. `data_manager/agent.py` → `orchestrator/data/agent.py`
2. `data_gatherer/agent.py` → `orchestrator/data/gatherer/agent.py`
3. `kg_initialiser/agent.py` → `orchestrator/data/kg_initialiser/agent.py`

#### 1.4 Update Imports

**Old import pattern** (in `orchestrator/agent.py`):
```python
from patientmap.agents.data_manager.agent import root_agent as data_manager_agent
```

**New import pattern**:
```python
from .data.agent import root_agent as data_manager_agent
```

#### 1.5 Test Data Phase

```powershell
# Test data phase independently
python -c "from patientmap.agents.orchestrator.data.agent import root_agent; print(root_agent)"
```

---

### Phase 2: Research Phase Restructuring

**Duration**: 2-3 hours  
**Risk**: Medium  
**Target**: `research`, `knowledge_graph`

#### 2.1 Create Directory Structure

```powershell
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/research" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/research/topics" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/research/search_loop" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/research/search_loop/researcher" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/research/kg_enrichment" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/research/kg_enrichment/enricher" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/research/kg_enrichment/checker" -Force
```

#### 2.2 Copy Configs

```powershell
Copy-Item ".profiles/research/research_agent.yaml" "src/patientmap/agents/orchestrator/research/config.yaml"
Copy-Item ".profiles/research/research_topics.yaml" "src/patientmap/agents/orchestrator/research/topics/config.yaml"
Copy-Item ".profiles/knowledge/knowledge_graph_agent.yaml" "src/patientmap/agents/orchestrator/research/kg_enrichment/enricher/config.yaml"
```

#### 2.3 Migrate Files

**Files to migrate**:
1. `research/agent.py` → `orchestrator/research/agent.py`
2. Extract topics logic → `orchestrator/research/topics/agent.py`
3. `knowledge_graph/agent.py` → `orchestrator/research/kg_enrichment/enricher/agent.py`

#### 2.4 Test Research Phase

```powershell
python -c "from patientmap.agents.orchestrator.research.agent import root_agent; print(root_agent)"
```

---

### Phase 3: Clinical Phase Restructuring

**Duration**: 3-4 hours  
**Risk**: High (16 specialist agents to move)  
**Target**: `clinical/` with all specialists

#### 3.1 Create Directory Structure

```powershell
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/clinical" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/clinical/manager" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/clinical/manager/specialists" -Force
New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/clinical/checker" -Force

# Create all 16 specialist directories
$specialists = @(
    "cardiology", "neurology", "psychiatry", "endocrinology",
    "clinical_pharmacy", "gastroenterology", "geriatrics", "hematology",
    "nephrology", "pulmonology", "physical_medicine_rehabilitation",
    "infectious_disease", "nutrition_dietetics", "pain_medicine",
    "rheumatology", "palliative_care"
)

foreach ($specialist in $specialists) {
    New-Item -ItemType Directory -Path "src/patientmap/agents/orchestrator/clinical/manager/specialists/$specialist" -Force
}
```

#### 3.2 Migrate Specialists (Automated)

```powershell
# Migrate specialist configs
foreach ($specialist in $specialists) {
    $configFile = ".profiles/clinical/${specialist}_agent.yaml"
    $targetDir = "src/patientmap/agents/orchestrator/clinical/manager/specialists/$specialist"
    
    if (Test-Path $configFile) {
        Copy-Item $configFile "$targetDir/config.yaml"
    }
    
    # Copy agent files
    $agentFile = "src/patientmap/agents/clinical/$specialist/agent.py"
    if (Test-Path $agentFile) {
        Copy-Item $agentFile "$targetDir/agent.py"
    }
}
```

#### 3.3 Update Clinical Manager Imports

**Old pattern**:
```python
from patientmap.agents.clinical.cardiology import cardiology_agent
```

**New pattern**:
```python
from .manager.specialists.cardiology.agent import root_agent as cardiology_agent
```

#### 3.4 Test Clinical Phase

```powershell
python -c "from patientmap.agents.orchestrator.clinical.agent import root_agent; print(root_agent)"
```

---

### Phase 4: Update Orchestrator & Main Entry Point

**Duration**: 1 hour  
**Risk**: Medium-High (breaks everything if wrong)

#### 4.1 Update Orchestrator Imports

**File**: `src/patientmap/agents/orchestrator/agent.py`

```python
# OLD:
from patientmap.agents.data_manager.agent import root_agent as data_manager_agent
from patientmap.agents.research.agent import root_agent as research_agent
from patientmap.agents.clinical.agent import root_agent as clinical_agent

# NEW:
from .data.agent import root_agent as data_manager_agent
from .research.agent import root_agent as research_agent
from .clinical.agent import root_agent as clinical_agent
```

#### 4.2 Verify Main Entry Point

**File**: `main.py`

This import should **remain unchanged**:
```python
from patientmap.agents.orchestrator.agent import root_agent
```

This still works because `orchestrator/` is at the same level.

#### 4.3 Test Full System

```powershell
# Test import chain
python main.py --help

# Or run full app
python main.py
```

---

### Phase 5: Cleanup & Validation

**Duration**: 1-2 hours  
**Risk**: Low

#### 5.1 Remove Old Agent Directories

```powershell
# Only after CONFIRMING new structure works!
Remove-Item "src/patientmap/agents/data_manager" -Recurse -Force
Remove-Item "src/patientmap/agents/data_gatherer" -Recurse -Force
Remove-Item "src/patientmap/agents/kg_initialiser" -Recurse -Force
Remove-Item "src/patientmap/agents/knowledge_graph" -Recurse -Force
Remove-Item "src/patientmap/agents/research" -Recurse -Force
Remove-Item "src/patientmap/agents/clinical" -Recurse -Force  # After moving specialists
```

#### 5.2 Archive Old Config Directory

```powershell
# Keep .profiles for reference but mark as deprecated
Rename-Item ".profiles" ".profiles.deprecated"
```

#### 5.3 Run Full Test Suite

```powershell
# Run all tests
python -m pytest tests/ -v --tb=short

# Test each agent independently
python -c "from patientmap.agents.orchestrator.agent import root_agent; print('✓ Orchestrator OK')"
python -c "from patientmap.agents.orchestrator.data.agent import root_agent; print('✓ Data Manager OK')"
python -c "from patientmap.agents.orchestrator.research.agent import root_agent; print('✓ Research OK')"
python -c "from patientmap.agents.orchestrator.clinical.agent import root_agent; print('✓ Clinical OK')"
```

#### 5.4 Update Documentation

Files to update:
- `README.md` - Update project structure diagram
- `docs/session_memory_integration_VALIDATED.md` - Update agent hierarchy section
- `.github/copilot-instructions.md` - Update directory structure references

---

## Rollback Plan

If something breaks during migration:

### Option 1: Rollback Specific Phase

```powershell
# If Phase 2 breaks, revert just that phase
git checkout HEAD -- src/patientmap/agents/orchestrator/research/
git checkout HEAD -- src/patientmap/agents/research/
```

### Option 2: Full Rollback

```powershell
# Restore from backup branch
git stash
git checkout backup/pre-restructure
git checkout -b update/agents-restored
```

### Option 3: Manual Fix

Keep both old and new structures temporarily, debug imports, then remove old.

---

## Example Refactored Code

See next section for complete before/after examples.

---

## Post-Migration Checklist

- [ ] All tests pass (`pytest tests/`)
- [ ] Main entry point works (`python main.py`)
- [ ] Each agent can be imported independently
- [ ] No `sys.path` manipulation in agent files
- [ ] Configs co-located with agents
- [ ] Documentation updated
- [ ] Old directories removed
- [ ] Git commit with clear message
- [ ] Team notified of new structure

---

## Estimated Timeline

| Phase | Duration | Risk Level |
|-------|----------|------------|
| 0. Preparation | 1-2 hours | Low |
| 1. Data Phase | 2-3 hours | Medium |
| 2. Research Phase | 2-3 hours | Medium |
| 3. Clinical Phase | 3-4 hours | High |
| 4. Orchestrator Update | 1 hour | Medium-High |
| 5. Cleanup & Validation | 1-2 hours | Low |
| **Total** | **10-15 hours** | **Medium** |

**Recommendation**: Allocate 2 full work days for migration with buffer time.

---

## Risk Mitigation

1. **Backup everything** before starting
2. **Migrate one phase at a time** - don't do all at once
3. **Test after each phase** - catch issues early
4. **Keep old structure** until new one is fully validated
5. **Pair programming** - have someone review changes
6. **Use version control** - commit after each successful phase

---

## Success Criteria

✅ All agents importable via hierarchical paths  
✅ No `sys.path` manipulation needed  
✅ Configs co-located with code  
✅ All tests passing  
✅ Main application runs successfully  
✅ Clear visual hierarchy in file explorer  
✅ Improved code maintainability
