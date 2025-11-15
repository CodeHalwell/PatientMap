# Tool Registry Quick Reference

## Summary
✅ **30 tools registered** across 9 categories
- 3 ADK Built-in tools
- 4 Research tools  
- 23 Neo4j tools (connection, nodes, relationships, queries, persistence, generic)

## How to Use

### In Agent YAML
```yaml
agent_id: my_agent
tools:
  - google_search
  - neo4j_bulk_add_conditions
  - show_my_available_tools  # Meta-tool to see what you have
```

### In Agent Python Code
```python
from patientmap.tools import get_tools_from_config
from patientmap.common.config import AgentConfig

config = AgentConfig("agent.yaml").get_agent()
tools = get_tools_from_config(config.tools)  # Converts strings → objects

agent = LlmAgent(name=config.agent_name, tools=tools)
```

## All Available Tools

### ADK Built-in (3)
| Tool | Usage |
|------|-------|
| `google_search` | `google_search(query: str) -> str` |
| `url_context` | `url_context(url: str) -> str` |
| `exit_loop` | `exit_loop() -> None` (only in checker agents) |

### Research (4)
| Tool | Usage |
|------|-------|
| `google_scholar_tool` | `google_scholar_tool(query: str) -> str` |
| `pubmed_tool` | `pubmed_tool(query: str) -> str` |
| `semantic_scholar_tool` | `semantic_scholar_tool(query: str) -> str` |
| `wikipedia_tool` | `wikipedia_tool(query: str) -> str` |

### Neo4j Connection (2)
| Tool | Usage |
|------|-------|
| `verify_neo4j_connection` | `verify_neo4j_connection(tool_context) -> str` |
| `initialize_neo4j_schema` | `initialize_neo4j_schema(tool_context) -> str` |

### Neo4j Initialization (1)
| Tool | Usage |
|------|-------|
| `neo4j_initialize_patient_graph` | `neo4j_initialize_patient_graph(patient_id, patient_name, tool_context) -> str` |

### Neo4j Nodes (6)
| Tool | Usage | Notes |
|------|-------|-------|
| `neo4j_add_condition` | Single condition | Use bulk version when possible |
| `neo4j_add_medication` | Single medication | Use bulk version when possible |
| `neo4j_bulk_add_conditions` | Multiple conditions | **PREFERRED** |
| `neo4j_bulk_add_medications` | Multiple medications | **PREFERRED** |
| `neo4j_add_research_article` | Single article | |
| `neo4j_add_clinical_trial` | Single trial | |

### Neo4j Relationships (3)
| Tool | Usage | Notes |
|------|-------|-------|
| `neo4j_link_article_to_condition` | Single link | Use bulk when possible |
| `neo4j_bulk_link_articles_to_conditions` | Multiple links | **PREFERRED** |
| `neo4j_bulk_link_articles_to_medications` | Multiple links | **PREFERRED** |

### Neo4j Queries (4)
| Tool | Usage |
|------|-------|
| `neo4j_get_patient_overview` | `neo4j_get_patient_overview(patient_id, tool_context) -> str` |
| `neo4j_find_related_research` | `neo4j_find_related_research(condition_id, max_results, tool_context) -> str` |
| `neo4j_export_graph_summary` | `neo4j_export_graph_summary(tool_context) -> str` |
| `neo4j_analyze_graph_connectivity` | `neo4j_analyze_graph_connectivity(patient_id, tool_context) -> str` |

### Neo4j Persistence (2)
| Tool | Usage | Notes |
|------|-------|-------|
| `neo4j_clear_patient_graph` | `neo4j_clear_patient_graph(patient_id, tool_context) -> str` | ⚠️ DESTRUCTIVE |
| `neo4j_list_all_patients` | `neo4j_list_all_patients(tool_context) -> str` | |

### Neo4j Generic (5)
| Tool | Usage | Notes |
|------|-------|-------|
| `neo4j_create_custom_node` | Create any node type | For custom entities |
| `neo4j_create_custom_relationship` | Create any relationship | For custom links |
| `neo4j_delete_node` | Delete specific node | ⚠️ DESTRUCTIVE |
| `neo4j_bulk_create_custom_nodes` | Bulk create custom nodes | **PREFERRED** |
| `neo4j_bulk_create_custom_relationships` | Bulk create custom rels | **PREFERRED** |

## Admin/Meta-Tools

These tools help agents understand their own capabilities:

```yaml
tools:
  - show_my_available_tools  # Shows what tools you have
  - check_tool_exists        # Verify a tool exists
  - list_tools_by_category   # Browse tools by category
```

## Tool Category Constants

Use these in Python code for convenience:

```python
from patientmap.tools import (
    ADK_BUILTIN_TOOLS,      # ['google_search', 'url_context', 'exit_loop']
    RESEARCH_TOOLS,         # All 4 research tools
    ALL_NEO4J_TOOLS,        # All 23 Neo4j tools
    NEO4J_NODE_TOOLS,       # Just node creation tools
    NEO4J_RELATIONSHIP_TOOLS, # Just relationship tools
    NEO4J_QUERY_TOOLS,      # Just query tools
    ALL_TOOL_NAMES          # All 30 tool names
)

# Load all research tools
tools = get_tools_from_config(RESEARCH_TOOLS)
```

## Validation

```python
from patientmap.tools import validate_agent_tools

# Check if agent config is valid
result = validate_agent_tools("my_agent", ["google_search", "fake_tool"])
print(result)
# {
#   "valid": False,
#   "missing_tools": ["fake_tool"],
#   "available_tools": ["google_search"]
# }
```

## Testing

```bash
# Run registry module to see summary
uv run python src/patientmap/tools/tool_registry.py

# Output shows:
# - Total tools registered: 30
# - Breakdown by category
# - Full JSON with all tool metadata
```

## Common Patterns

### Pattern 1: Research Agent
```yaml
tools:
  - google_search
  - url_context
  - exit_loop  # If used in loop
```

### Pattern 2: KG Builder
```yaml
tools:
  - neo4j_initialize_patient_graph
  - neo4j_bulk_add_conditions
  - neo4j_bulk_add_medications
  - neo4j_bulk_link_articles_to_conditions
```

### Pattern 3: KG Checker (Read-Only)
```yaml
tools:
  - neo4j_get_patient_overview
  - neo4j_analyze_graph_connectivity
  - exit_loop
```

### Pattern 4: Full Stack
```yaml
tools:
  # Research
  - google_search
  - pubmed_tool
  # Graph building
  - neo4j_bulk_add_conditions
  - neo4j_bulk_add_medications
  - neo4j_bulk_link_articles_to_conditions
  # Queries
  - neo4j_get_patient_overview
  # Meta
  - show_my_available_tools
```

## Preventing Tool Hallucination

Add to agent instructions:

```yaml
instruction: |
  **YOUR AVAILABLE TOOLS:**
  You have access to EXACTLY these tools:
  1. google_search - Search Google
  2. neo4j_bulk_add_conditions - Add conditions to graph
  
  **TOOLS YOU DO NOT HAVE:**
  - transfer_to_agent (does not exist)
  - save_file (does not exist)
  - execute_code (does not exist)
  
  If unsure, call show_my_available_tools() to see your tool list.
  NEVER attempt to call tools not listed above.
```

## See Also

- **Full Guide**: `docs/TOOL_REGISTRY_GUIDE.md` - Complete integration guide with examples
- **Agent Standards**: `docs/AGENT_TOOL_ACCESS_STANDARDS.md` - Agent configuration patterns
- **Source Code**: `src/patientmap/tools/tool_registry.py` - Registry implementation
