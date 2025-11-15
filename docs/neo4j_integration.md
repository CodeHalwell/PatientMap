# Neo4j Integration for PatientMap

## Overview

PatientMap now supports **dual knowledge graph storage**:
- **NetworkX**: In-memory graphs for prototyping and temporary analysis
- **Neo4j Aura**: Cloud-hosted graph database for persistent, production-grade storage

## Setup

### 1. Neo4j Aura Account
Your free Neo4j Aura instance is already configured with credentials in `.env`:

```env
NEO4J_URI=neo4j+s://514cd0db.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=XBtUdln2W72IWTxAKckeeyrTaTYYY8n5OxZpPRzljKo
NEO4J_DATABASE=neo4j
AURA_INSTANCEID=514cd0db
AURA_INSTANCENAME=Free instance
```

### 2. Install Dependencies
```bash
uv sync  # Installs neo4j>=5.27.0
```

### 3. Verify Connection
```python
from patientmap.common.neo4j_client import Neo4jClient
from google.adk.tools.tool_context import ToolContext

tool_context = ToolContext()
info = Neo4j Client.verify_connection(tool_context)
print(info)
# {'status': 'connected', 'database': 'neo4j', 'name': 'Neo4j Kernel', ...}
```

## Architecture

### Neo4j Client (`patientmap/common/neo4j_client.py`)
- **Connection Pooling**: Driver stored in `ToolContext.state['neo4j_driver']` (singleton pattern)
- **Automatic Credential Loading**: Reads from `.env` file
- **Session Management**: `get_session()` returns managed sessions
- **Schema Initialization**: Creates constraints/indexes for Patient, Condition, Medication, ResearchArticle, ClinicalTrial

### Neo4j Tools (`patientmap/tools/neo4j_kg_tools.py`)
All Neo4j tools use the `neo4j_` prefix to distinguish from NetworkX tools:

**Connection**:
- `verify_neo4j_connection(tool_context)` - Check database access
- `initialize_neo4j_schema(tool_context)` - Set up constraints (idempotent)

**Graph Initialization**:
- `neo4j_initialize_patient_graph(patient_id, patient_name, tool_context)` - Create Patient node

**Node Operations**:
- `neo4j_add_condition(patient_id, condition_id, condition_name, icd_code, symptoms, tool_context)`
- `neo4j_add_medication(patient_id, medication_id, medication_name, dosage, frequency, side_effects, tool_context)`
- `neo4j_add_research_article(article_id, article_title, authors, ..., tool_context)`

**Relationship Operations**:
- `neo4j_link_article_to_condition(article_id, condition_id, relevance, confidence, tool_context)`
- `neo4j_bulk_link_articles_to_conditions(links, tool_context)` - **Efficient batch linking**

**Query Operations**:
- `neo4j_get_patient_overview(patient_id, tool_context)` - Patient summary
- `neo4j_find_related_research(condition_id, max_results, tool_context)` - Related articles
- `neo4j_export_graph_summary(tool_context)` - Database statistics
- `neo4j_analyze_graph_connectivity(patient_id, tool_context)` - Connectivity metrics

**Management**:
- `neo4j_clear_patient_graph(patient_id, tool_context)` - Delete patient data
- `neo4j_list_all_patients(tool_context)` - List all patients in database

## Agent Integration

### Builder Agent
The `knowledge_graph_building_agent` now has access to both NetworkX and Neo4j tools:

**Workflow**:
1. Call `verify_neo4j_connection()` to check accessibility
2. Call `initialize_neo4j_schema()` once per session
3. Create patient: `neo4j_initialize_patient_graph(patient_id, patient_name)`
4. Add conditions: `neo4j_add_condition(patient_id, condition_id, ...)`
5. Add medications: `neo4j_add_medication(patient_id, medication_id, ...)`
6. Add research: `neo4j_add_research_article(article_id, ...)`
7. Batch link: `neo4j_bulk_link_articles_to_conditions(links)`
8. Review: `neo4j_get_patient_overview(patient_id)`

### Tool Selection Strategy
The builder agent's instruction now recommends:
- **Primary**: Use Neo4j tools for persistent storage
- **Fallback**: Use NetworkX tools if Neo4j connection fails
- **Batch Operations**: Prefer `neo4j_bulk_link_articles_to_conditions` for research articles

## Neo4j Schema

### Node Labels
- **Patient**: `{patient_id, name, created_at, updated_at}`
- **Condition**: `{condition_id, name, label, icd_code, symptoms, created_at, updated_at}`
- **Medication**: `{medication_id, name, label, dosage, frequency, side_effects, created_at, updated_at}`
- **ResearchArticle**: `{article_id, title, label, authors, publication_date, journal, url, abstract, keywords, created_at, updated_at}`
- **ClinicalTrial**: `{trial_id, title, label, phase, status, conditions, interventions, url, created_at, updated_at}`

### Relationship Types
- **HAS_CONDITION**: `(Patient)-[{created_at}]->(Condition)`
- **TAKES_MEDICATION**: `(Patient)-[{created_at}]->(Medication)`
- **STUDIES**: `(ResearchArticle)-[{relevance, confidence, created_at}]->(Condition)`

### Constraints (Auto-created)
```cypher
CREATE CONSTRAINT patient_id_unique FOR (p:Patient) REQUIRE p.patient_id IS UNIQUE
CREATE CONSTRAINT condition_id_unique FOR (c:Condition) REQUIRE c.condition_id IS UNIQUE
CREATE CONSTRAINT medication_id_unique FOR (m:Medication) REQUIRE m.medication_id IS UNIQUE
CREATE CONSTRAINT article_id_unique FOR (a:ResearchArticle) REQUIRE a.article_id IS UNIQUE
CREATE CONSTRAINT trial_id_unique FOR (t:ClinicalTrial) REQUIRE t.trial_id IS UNIQUE
```

### Indexes (Auto-created)
```cypher
CREATE INDEX patient_name_index FOR (p:Patient) ON (p.name)
CREATE INDEX condition_label_index FOR (c:Condition) ON (c.label)
```

## Cypher Query Examples

### Get Patient with All Related Data
```cypher
MATCH (p:Patient {patient_id: 'patient_123'})
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
OPTIONAL MATCH (a:ResearchArticle)-[:STUDIES]->(c)
RETURN p, collect(DISTINCT c) AS conditions, 
       collect(DISTINCT m) AS medications,
       collect(DISTINCT a) AS research
```

### Find High-Confidence Research for Condition
```cypher
MATCH (a:ResearchArticle)-[r:STUDIES]->(c:Condition {condition_id: 'condition_diabetes'})
WHERE r.confidence > 0.8
RETURN a.title, r.confidence, r.relevance
ORDER BY r.confidence DESC
```

### Calculate Knowledge Graph Depth
```cypher
MATCH (p:Patient {patient_id: 'patient_123'})
MATCH path = (p)-[*1..3]->()
RETURN avg(length(path)) AS avg_depth, max(length(path)) AS max_depth
```

## Comparison: NetworkX vs Neo4j

| Feature | NetworkX | Neo4j Aura |
|---------|----------|------------|
| **Storage** | In-memory (ephemeral) | Persistent cloud database |
| **Performance** | Fast for small graphs | Optimized for complex queries |
| **Scalability** | Limited by RAM | Scales to millions of nodes |
| **Querying** | Python algorithms | Cypher query language |
| **Backup** | Manual JSON export | Automatic cloud backup |
| **Cost** | Free (bundled) | Free tier (50k nodes) |
| **Setup** | Zero config | Requires credentials |
| **Use Case** | Prototyping, temporary analysis | Production, persistent storage |

## Best Practices

1. **Always verify connection first**: Call `verify_neo4j_connection()` at session start
2. **Initialize schema once**: Call `initialize_neo4j_schema()` early in workflow
3. **Use batch operations**: Prefer `neo4j_bulk_link_articles_to_conditions` over individual links
4. **Unique IDs**: Ensure patient_id, condition_id, medication_id are unique
5. **MERGE semantics**: Re-calling create functions with same ID updates existing nodes
6. **Error handling**: If Neo4j fails, fallback to NetworkX tools gracefully
7. **Connection cleanup**: Driver auto-closes when ToolContext state is cleared

## Troubleshooting

### Connection Errors
```python
# Check connection
from patientmap.tools.neo4j_kg_tools import verify_neo4j_connection
result = verify_neo4j_connection(tool_context)
# If status='error', check .env credentials
```

### Authentication Failed
- Verify `NEO4J_PASSWORD` in `.env` matches Aura console
- Check `NEO4J_URI` scheme is `neo4j+s://` (secure)

### Constraint Violations
```
Neo4j.ClientError.Schema.ConstraintValidationFailed: Node already exists
```
Solution: Use MERGE semantics (built into all neo4j_add_* functions)

### Missing Properties
- All neo4j_add_* functions use MERGE with SET, so re-calling updates nodes
- Example: Add missing ICD code by calling `neo4j_add_condition` again with same condition_id

## Migration from NetworkX

To migrate existing NetworkX graphs to Neo4j:

1. **Export NetworkX**: `save_graph_to_disk(filename)`
2. **Load JSON**: Read node-link JSON format
3. **Bulk Import to Neo4j**:
```python
# Parse NetworkX export
with open('patient_kg.json') as f:
    data = json.load(f)

# Initialize Neo4j graph
neo4j_initialize_patient_graph(patient_id, patient_name, tool_context)

# Batch add nodes by type
conditions = [n for n in data['nodes'] if n['node_type'] == 'condition']
for c in conditions:
    neo4j_add_condition(patient_id, c['id'], c['label'], c.get('icd_code'), ...)

# Batch link research
links = []
for link in data['links']:
    if link['relationship_type'] == 'STUDIES':
        links.append({
            'article_id': link['source'],
            'condition_id': link['target'],
            'relevance': link.get('relevance'),
            'confidence': link.get('confidence')
        })
neo4j_bulk_link_articles_to_conditions(links, tool_context)
```

## Next Steps

### Session/Memory Integration
- Neo4j driver stored in `ToolContext.state` already supports ADK session lifecycle
- Future: Integrate with `DatabaseSessionService` for cross-session persistence
- Future: Wire `EventsCompactionConfig` for memory optimization

### MCP Server
- Consider exposing Neo4j tools via FastMCP server
- Enable external agents to query PatientMap knowledge graphs
- Ref: ADK docs on `ToolboxToolset` and MCP integration

### Advanced Queries
- Implement graph algorithms (shortest path, centrality, community detection)
- Add full-text search on research abstracts
- Create specialized views for clinical decision support
