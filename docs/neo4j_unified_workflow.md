# Neo4j Unified Workflow - Single Persistent Graph

## Overview

PatientMap now uses **ONE persistent Neo4j graph per patient** that is progressively updated across all workflow phases. This eliminates the previous multi-graph approach (base → enriched → final) and provides a unified, production-grade graph database.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│            Neo4j Aura Cloud Database                    │
│  (Persistent storage - no file saving/loading needed)  │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
   ┌────▼────┐ ┌──▼───┐ ┌────▼────┐
   │  Data   │ │Research│ Clinical │
   │  Phase  │ │ Phase │ │  Phase  │
   └─────────┘ └────────┘ └─────────┘
   
   CREATE      UPDATE     UPDATE
   Patient     Add        Add more
   + Initial   Research   Clinical
   Conditions  Articles   Insights
```

## Key Changes from Old Approach

### Before (NetworkX Multi-Graph)
```python
# Data Phase
builder → create NetworkX graph → save to patient_kg.json

# Research Phase
enricher → load patient_kg.json → add research → save to patient_kg_enriched.json

# Clinical Phase  
clinical → load patient_kg_enriched.json → add insights → save to patient_final_kg.json
```

### After (Neo4j Single Graph)
```python
# Data Phase
builder → neo4j_initialize_patient_graph(patient_id)
       → neo4j_add_condition(patient_id, ...)
       → neo4j_add_medication(patient_id, ...)
       # Graph persists in Neo4j

# Research Phase
enricher → neo4j_get_patient_overview(patient_id)  # Query existing graph
        → neo4j_add_research_article(...)
        → neo4j_bulk_link_articles_to_conditions(...)
        # Updates persist automatically

# Clinical Phase
clinical → neo4j_get_patient_overview(patient_id)  # Query existing graph
        → neo4j_add_condition(...)  # Add new diagnoses
        → neo4j_add_medication(...)  # Add new treatments
        # Updates persist automatically
```

## Workflow Phases

### Phase 1: Data Initialization (Builder Agent)

**Goal**: Create patient node with initial conditions and medications

**Tools**:
- `verify_neo4j_connection()` - Check database connection
- `initialize_neo4j_schema()` - Set up constraints (once per session)
- `neo4j_initialize_patient_graph(patient_id, patient_name)` - Create Patient node
- `neo4j_add_condition(patient_id, condition_id, name, icd_code, symptoms)` - Add condition + link
- `neo4j_add_medication(patient_id, medication_id, name, dosage, frequency)` - Add medication + link

**Output**: Patient node with conditions and medications in Neo4j

**No File Operations**: Everything persists in database

---

### Phase 2: Research Enrichment (Research Agent)

**Goal**: Add research articles and link to patient's conditions

**Tools**:
- `neo4j_get_patient_overview(patient_id)` - Get current state
- `neo4j_find_related_research(condition_id)` - Check existing research
- `neo4j_add_research_article(article_id, title, authors, ...)` - Add article
- `neo4j_add_clinical_trial(trial_id, title, phase, ...)` - Add trial
- `neo4j_bulk_link_articles_to_conditions(links)` - Batch link articles

**Output**: Same patient graph + research articles linked to conditions

**No File Operations**: Updates persist automatically

---

### Phase 3: Clinical Enrichment (Clinical Agent)

**Goal**: Add clinical recommendations and new diagnoses/treatments

**Tools**:
- `neo4j_get_patient_overview(patient_id)` - Get current state
- `neo4j_add_condition(patient_id, condition_id, ...)` - Add new diagnoses
- `neo4j_add_medication(patient_id, medication_id, ...)` - Add new treatments
- `neo4j_link_article_to_condition(article_id, condition_id, ...)` - Link evidence

**Output**: Same patient graph + clinical insights

**No File Operations**: Updates persist automatically

---

## Benefits

### ✅ Single Source of Truth
- ONE graph per patient across all phases
- No synchronization issues
- No version conflicts (enriched vs final)

### ✅ Persistent Storage
- Cloud-hosted Neo4j Aura
- Automatic persistence (no save operations)
- Accessible across sessions

### ✅ Multi-Patient Support
- `patient_id` unique constraint enables multiple patients
- Shared research articles (one article can link to many patients' conditions)
- Free tier: ~430 dedicated patients or thousands with shared research

### ✅ Production-Ready
- ACID transactions
- Cypher query language
- Advanced graph algorithms (shortest path, centrality, community detection)
- Neo4j Browser for visualization

### ✅ Simplified Workflow
- No file loading/saving
- No graph import/export between phases
- Direct database queries

## Example Workflow

```python
# Phase 1: Data Initialization
builder_agent:
  1. verify_neo4j_connection()
  2. initialize_neo4j_schema()
  3. neo4j_initialize_patient_graph("patient_001", "John Doe")
  4. neo4j_add_condition("patient_001", "cond_diabetes", "Type 2 Diabetes", "E11.9", [...])
  5. neo4j_add_medication("patient_001", "med_metformin", "Metformin", "500mg", "BID")
  # Result: Patient node + 1 condition + 1 medication in Neo4j

# Phase 2: Research Enrichment
research_agent:
  1. neo4j_get_patient_overview("patient_001")  # Returns 1 condition, 1 medication
  2. neo4j_add_research_article("art_001", "Metformin Efficacy Study", [...])
  3. neo4j_add_research_article("art_002", "Diabetes Management Guidelines", [...])
  4. neo4j_bulk_link_articles_to_conditions([
       {"article_id": "art_001", "condition_id": "cond_diabetes", "relevance": "treatment", "confidence": 0.9},
       {"article_id": "art_002", "condition_id": "cond_diabetes", "relevance": "guidelines", "confidence": 0.95}
     ])
  # Result: Same patient + 2 research articles linked

# Phase 3: Clinical Enrichment
clinical_agent:
  1. neo4j_get_patient_overview("patient_001")  # Returns 1 condition, 1 medication, 2 research articles
  2. neo4j_add_condition("patient_001", "cond_hypertension", "Hypertension", "I10", [...])
  3. neo4j_add_medication("patient_001", "med_lisinopril", "Lisinopril", "10mg", "QD")
  # Result: Same patient + 2 conditions + 2 medications + 2 research articles

# Final Query
neo4j_export_graph_summary()
{
  "total_nodes": 5,
  "total_edges": 6,
  "nodes_by_type": {
    "Patient": 1,
    "Condition": 2,
    "Medication": 2,
    "ResearchArticle": 2
  }
}
```

## Agent Configuration Updates

### ✅ Builder Agent (`kg_initialiser.yaml`)
- **Removed**: All NetworkX tools (`initialize_patient_graph`, `bulk_add_nodes`, `save_graph_to_disk`, etc.)
- **Added**: All Neo4j tools (`neo4j_initialize_patient_graph`, `neo4j_add_condition`, etc.)
- **Updated**: Instructions emphasize NO FILE OPERATIONS

### ✅ Research Enricher (`knowledge_graph_agent.yaml`)
- **Removed**: `list_knowledge_graphs`, `load_graph_from_disk`, `save_graph_to_disk`
- **Added**: `neo4j_get_patient_overview`, `neo4j_add_research_article`, `neo4j_bulk_link_articles_to_conditions`
- **Updated**: Instructions say "UPDATE existing Neo4j graph" instead of "load enriched file"

### ✅ Clinical Enricher (`clinical_kg_enrichment_agent.yaml`)
- **Removed**: All file-based NetworkX tools
- **Added**: Neo4j tools for adding conditions/medications and linking evidence
- **Updated**: Instructions say "UPDATE same Neo4j graph" instead of "load final file"

## Neo4j Schema

```cypher
// Unique Constraints
CREATE CONSTRAINT patient_id_unique IF NOT EXISTS FOR (p:Patient) REQUIRE p.patient_id IS UNIQUE;
CREATE CONSTRAINT condition_id_unique IF NOT EXISTS FOR (c:Condition) REQUIRE c.condition_id IS UNIQUE;
CREATE CONSTRAINT medication_id_unique IF NOT EXISTS FOR (m:Medication) REQUIRE m.medication_id IS UNIQUE;
CREATE CONSTRAINT article_id_unique IF NOT EXISTS FOR (a:ResearchArticle) REQUIRE a.article_id IS UNIQUE;
CREATE CONSTRAINT trial_id_unique IF NOT EXISTS FOR (t:ClinicalTrial) REQUIRE t.trial_id IS UNIQUE;

// Indexes for Performance
CREATE INDEX patient_name_idx IF NOT EXISTS FOR (p:Patient) ON (p.name);
CREATE INDEX condition_label_idx IF NOT EXISTS FOR (c:Condition) ON (c.label);

// Node Labels
:Patient (patient_id, name, created_at, updated_at)
:Condition (condition_id, label, icd_code, symptoms)
:Medication (medication_id, label, dosage, frequency, side_effects)
:ResearchArticle (article_id, title, authors, journal, url, abstract, keywords)
:ClinicalTrial (trial_id, title, phase, status, conditions, interventions, url)

// Relationship Types
(:Patient)-[:HAS_CONDITION]->(:Condition)
(:Patient)-[:TAKES_MEDICATION]->(:Medication)
(:ResearchArticle)-[:STUDIES {relevance, confidence}]->(:Condition)
(:ClinicalTrial)-[:INVESTIGATES]->(:Condition)
```

## Querying the Graph

### Get Patient Overview
```cypher
MATCH (p:Patient {patient_id: 'patient_001'})
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
OPTIONAL MATCH (a:ResearchArticle)-[:STUDIES]->(c)
RETURN p, collect(DISTINCT c) AS conditions, 
       collect(DISTINCT m) AS medications,
       count(DISTINCT a) AS research_count
```

### Find Research for Condition
```cypher
MATCH (a:ResearchArticle)-[r:STUDIES]->(c:Condition {condition_id: 'cond_diabetes'})
RETURN a.title, a.authors, r.relevance, r.confidence
ORDER BY r.confidence DESC
```

### Cross-Patient Analysis
```cypher
MATCH (p:Patient)-[:HAS_CONDITION]->(c:Condition {label: 'Type 2 Diabetes'})
RETURN p.name, count(c) AS diabetes_patients
```

## Testing

### Test Script: `test_unified_neo4j_workflow.py`

```python
# Test complete workflow: data → research → clinical phases
# All on ONE persistent Neo4j graph

from patientmap.tools.neo4j_kg_tools import *

patient_id = "test_unified_patient"
patient_name = "Test Unified Patient"

# Phase 1: Data
print("=== Phase 1: Data Initialization ===")
verify_neo4j_connection(mock_context)
initialize_neo4j_schema(mock_context)
neo4j_initialize_patient_graph(patient_id, patient_name, mock_context)
neo4j_add_condition(patient_id, "cond_test_diabetes", "Type 2 Diabetes", "E11.9", [...], mock_context)

# Phase 2: Research
print("=== Phase 2: Research Enrichment ===")
overview = neo4j_get_patient_overview(patient_id, mock_context)
neo4j_add_research_article("art_test_001", "Diabetes Study", [...], mock_context)
neo4j_link_article_to_condition("art_test_001", "cond_test_diabetes", "treatment", 0.9, mock_context)

# Phase 3: Clinical
print("=== Phase 3: Clinical Enrichment ===")
neo4j_add_medication(patient_id, "med_test_metformin", "Metformin", "500mg", "BID", [...], mock_context)

# Verify Final State
print("=== Final Graph Summary ===")
summary = neo4j_export_graph_summary(mock_context)
print(summary)

# Cleanup
neo4j_clear_patient_graph(patient_id, mock_context)
```

## Troubleshooting

### Connection Issues
```python
result = verify_neo4j_connection(tool_context)
# Returns: {"status": "connected", "version": "5.27-aura", ...}
```

### Schema Verification
```cypher
SHOW CONSTRAINTS;
SHOW INDEXES;
```

### Clear Patient for Testing
```python
neo4j_clear_patient_graph("test_patient_001", tool_context)
# Deletes patient + all related nodes and edges
```

## Migration Guide

### For Existing Agents

**Old NetworkX Pattern:**
```python
# Load graph
load_graph_from_disk("patient_kg_enriched.json")
# Modify graph
bulk_add_nodes([...])
# Save graph
save_graph_to_disk("patient_kg_final.json")
```

**New Neo4j Pattern:**
```python
# Query existing graph
neo4j_get_patient_overview(patient_id)
# Update graph
neo4j_add_condition(patient_id, ...)
# No save needed - auto-persists
```

### For New Agents

1. Import Neo4j tools from `patientmap.tools.neo4j_kg_tools`
2. Use `neo4j_get_patient_overview(patient_id)` to get current state
3. Use `neo4j_add_*` tools to update graph
4. Use `neo4j_export_graph_summary()` for statistics
5. **Never call save/load functions** - Neo4j handles persistence

## Next Steps

### Immediate
- [x] Remove all NetworkX tools from agents
- [x] Update agent YAML configurations
- [x] Test unified workflow end-to-end

### Future Enhancements
- [ ] Add DatabaseSessionService for cross-session persistence tracking
- [ ] Implement advanced Cypher queries (similarity, path finding)
- [ ] Add community detection for condition clustering
- [ ] Expose Neo4j tools via MCP server (FastMCP)
- [ ] Create Neo4j Browser visualization dashboards
- [ ] Add graph versioning with timestamps

## Resources

- **Neo4j Aura Console**: https://console.neo4j.io/
- **Neo4j Browser**: Access via Aura console for visual queries
- **Cypher Reference**: https://neo4j.com/docs/cypher-manual/current/
- **Python Driver Docs**: https://neo4j.com/docs/python-manual/current/
