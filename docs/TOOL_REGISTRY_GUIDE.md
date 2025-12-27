# Tool Registry Integration Guide

## Overview

The PatientMap Tool Registry provides a centralized system for managing all tools available to agents. This helps prevent LLM hallucination of non-existent tools by providing:

1. **Single Source of Truth**: All tools registered in `tool_registry.py`
2. **Runtime Validation**: Tools loaded from YAML configs are validated against registry
3. **Agent Self-Documentation**: Agents can query what tools they have access to
4. **Clear Documentation**: Each tool has metadata (category, description, usage)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   tool_registry.py                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │ TOOL_REGISTRY: Dict[str, Tool]                     │ │
│  │  - Maps tool names → actual Python objects        │ │
│  │  - Contains ALL available tools                   │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │ TOOL_DESCRIPTIONS: Dict[str, Metadata]             │ │
│  │  - Maps tool names → documentation                │ │
│  │  - Category, description, usage signature         │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Helper Functions:                                  │ │
│  │  - get_tools_from_config(names) → [Tool objects]  │ │
│  │  - get_available_tools(names) → JSON docs         │ │
│  │  - validate_agent_tools() → Validation result     │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Agent YAML Configuration                    │
│  agent_id: research_agent                               │
│  tools:                                                 │
│    - google_search      ← String name                   │
│    - url_context        ← Looked up in registry         │
│    - exit_loop          ← Converted to Python object    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Agent Python Module (agent.py)              │
│                                                          │
│  from patientmap.tools import get_tools_from_config     │
│  from patientmap.common.config import AgentConfig       │
│                                                          │
│  config = AgentConfig("agent.yaml").get_agent()         │
│  tools = get_tools_from_config(config.tools)            │
│                                                          │
│  agent = LlmAgent(                                      │
│      name=config.agent_name,                            │
│      tools=tools  ← Actual Python objects               │
│  )                                                       │
└─────────────────────────────────────────────────────────┘
```

## Tool Categories

### 1. ADK Built-in Tools
Tools provided by Google Agent Development Kit:
- `google_search`: Search Google for current information
- `url_context`: Fetch and extract content from URLs
- `exit_loop`: Exit loop agent iterations (only in checker agents)

### 2. Research Tools
Literature search tools (LangChain-based):
- `google_scholar_tool`: Search Google Scholar for academic papers
- `pubmed_tool`: Search PubMed for medical literature
- `semantic_scholar_tool`: Search Semantic Scholar with citation data
- `wikipedia_tool`: Search Wikipedia for general information

### 3. Neo4j Knowledge Graph Tools
**Connection Management:**
- `verify_neo4j_connection`: Test database connection
- `initialize_neo4j_schema`: Set up constraints and indexes

**Graph Initialization:**
- `neo4j_initialize_patient_graph`: Create Patient node anchor

**Node Operations (Individual):**
- `neo4j_add_condition`: Add single condition
- `neo4j_add_medication`: Add single medication
- `neo4j_add_research_article`: Add research article
- `neo4j_add_clinical_trial`: Add clinical trial

**Node Operations (Bulk - PREFERRED):**
- `neo4j_bulk_add_conditions`: Add multiple conditions efficiently
- `neo4j_bulk_add_medications`: Add multiple medications efficiently

**Relationship Operations:**
- `neo4j_link_article_to_condition`: Link one article to condition
- `neo4j_bulk_link_articles_to_conditions`: Link multiple (PREFERRED)
- `neo4j_bulk_link_articles_to_medications`: Link articles to medications

**Query Operations:**
- `neo4j_get_patient_overview`: Get comprehensive patient summary
- `neo4j_find_related_research`: Find articles for a condition
- `neo4j_export_graph_summary`: Get graph statistics
- `neo4j_analyze_graph_connectivity`: Analyze graph completeness

**Persistence:**
- `neo4j_clear_patient_graph`: Delete patient data (WARNING: destructive)
- `neo4j_list_all_patients`: List all patients in database

**Generic Tools (Advanced):**
- `neo4j_create_custom_node`: Create node with any label
- `neo4j_create_custom_relationship`: Create custom relationships
- `neo4j_delete_node`: Delete specific node
- `neo4j_bulk_create_custom_nodes`: Bulk create custom nodes
- `neo4j_bulk_create_custom_relationships`: Bulk create relationships

### 4. Admin Tools (Meta-Tools)
Tools that help agents understand their capabilities:
- `show_my_available_tools`: Show agent what tools it has
- `check_tool_exists`: Verify a tool exists before calling
- `list_tools_by_category`: Browse tools by category

## How to Use the Tool Registry

### Pattern 1: Simple Agent with Hardcoded Tools

**When to use:** Agent has a small, fixed set of tools that never changes.

```python
# agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import google_search, url_context
from patientmap.tools import get_tools_from_config

# Option A: Direct import (if tools are fixed)
agent = LlmAgent(
    name="simple_agent",
    tools=[google_search, url_context]
)

# Option B: Load from YAML (better - single source of truth)
from patientmap.common.config import AgentConfig

config = AgentConfig("agent.yaml").get_agent()
tools = get_tools_from_config(config.tools)

agent = LlmAgent(
    name=config.agent_name,
    tools=tools
)
```

**agent.yaml:**
```yaml
agent_id: simple_agent
agent_name: Simple Research Agent
tools:
  - google_search
  - url_context
```

### Pattern 2: Agent with Tool Registry Validation

**When to use:** You want to validate tools at startup and fail fast if misconfigured.

```python
# agent.py
from pathlib import Path
from google.adk.agents import LlmAgent
from patientmap.common.config import AgentConfig
from patientmap.tools import get_tools_from_config, validate_agent_tools

current_dir = Path(__file__).parent
config_path = current_dir / "agent.yaml"

# Load config
config = AgentConfig(str(config_path)).get_agent()

# Validate tools before loading
validation = validate_agent_tools(config.agent_name, config.tools)
if not validation["valid"]:
    raise RuntimeError(
        f"Agent {config.agent_name} has invalid tools: "
        f"{validation['missing_tools']}"
    )

# Load validated tools
tools = get_tools_from_config(config.tools)

agent = LlmAgent(
    name=config.agent_name,
    tools=tools,
    instruction=config.instruction
)
```

### Pattern 3: Agent with Self-Documentation (RECOMMENDED)

**When to use:** You want to help LLM avoid hallucinating tools by showing what's available.

**agent.yaml:**
```yaml
agent_id: kg_builder
agent_name: Knowledge Graph Builder
model: gemini-2.0-flash-exp
tools:
  - neo4j_initialize_patient_graph
  - neo4j_bulk_add_conditions
  - neo4j_bulk_add_medications
  - neo4j_bulk_link_articles_to_conditions
  - show_my_available_tools  # ← Meta-tool
  
instruction: |
  You are a knowledge graph builder agent.
  
  **CRITICAL TOOL ACCESS RESTRICTION:**
  Before attempting to use ANY tool, you can call show_my_available_tools()
  to see exactly what tools you have access to. This will prevent errors
  from calling tools that don't exist.
  
  **YOUR AVAILABLE TOOLS:**
  You have access to EXACTLY the following tools (and NO others):
  1. neo4j_initialize_patient_graph - Create Patient node
  2. neo4j_bulk_add_conditions - Add multiple conditions efficiently
  3. neo4j_bulk_add_medications - Add multiple medications efficiently
  4. neo4j_bulk_link_articles_to_conditions - Link research to conditions
  5. show_my_available_tools - See your tool list with full documentation
  
  **TOOLS YOU DO NOT HAVE (do not attempt to call):**
  - You DO NOT have transfer_to_agent
  - You DO NOT have exit_loop
  - You DO NOT have google_search
  - You DO NOT have individual add functions (use bulk_ versions)
  
  If you're unsure about a tool, call show_my_available_tools() first.
```

**agent.py:**
```python
from pathlib import Path
from google.adk.agents import LlmAgent
from patientmap.common.config import AgentConfig
from patientmap.tools import get_tools_from_config

current_dir = Path(__file__).parent
config = AgentConfig(str(current_dir / "agent.yaml")).get_agent()

# Load tools including meta-tool
tools = get_tools_from_config(config.tools)

agent = LlmAgent(
    name=config.agent_name,
    model=Gemini(model_name=config.model),
    instruction=config.instruction,
    tools=tools  # Includes show_my_available_tools
)
```

### Pattern 4: Dynamic Tool Loading with Constants

**When to use:** Agent needs all tools of a specific category.

```python
# agent.py
from google.adk.agents import LlmAgent
from patientmap.tools import (
    get_tools_from_config,
    ALL_NEO4J_TOOLS,  # Pre-defined list
    NEO4J_NODE_TOOLS,
    RESEARCH_TOOLS
)

# Option A: Load all Neo4j tools
tools = get_tools_from_config(ALL_NEO4J_TOOLS)

# Option B: Load just node creation tools
tools = get_tools_from_config(NEO4J_NODE_TOOLS)

# Option C: Load research tools
tools = get_tools_from_config(RESEARCH_TOOLS)

# Option D: Mix categories
tools = get_tools_from_config(
    RESEARCH_TOOLS + NEO4J_NODE_TOOLS + ["exit_loop"]
)

agent = LlmAgent(name="dynamic_agent", tools=tools)
```

## Best Practices

### ✅ DO: Use Tool Registry as Single Source of Truth

**Bad (hardcoded mismatch):**
```python
# agent.py - WRONG!
tools = [google_search, url_context, exit_loop]  # Hardcoded

# agent.yaml
tools:
  - google_search
  - url_context
# ← Missing exit_loop! Runtime mismatch error
```

**Good (YAML is source of truth):**
```python
# agent.py - RIGHT!
config = AgentConfig("agent.yaml").get_agent()
tools = get_tools_from_config(config.tools)  # Load from YAML

# agent.yaml
tools:
  - google_search
  - url_context
  - exit_loop
# ← Clear, validated, single source of truth
```

### ✅ DO: Document Available Tools in Agent Instructions

**Bad (agent doesn't know what it has):**
```yaml
instruction: |
  You are a research agent. Use tools to gather information.
  # ← Agent will hallucinate tools it doesn't have!
```

**Good (explicit tool list):**
```yaml
instruction: |
  You are a research agent.
  
  **YOUR AVAILABLE TOOLS:**
  - google_search: Search Google for current information
  - url_context: Fetch content from URLs
  - exit_loop: Signal completion (only call when research is done)
  
  **TOOLS YOU DO NOT HAVE:**
  - You DO NOT have transfer_to_agent
  - You DO NOT have save_file or write_file
  
  Use ONLY the tools listed above.
```

### ✅ DO: Add Meta-Tool for Self-Documentation

**Add to agent YAML:**
```yaml
tools:
  - google_search
  - url_context
  - show_my_available_tools  # ← Meta-tool

instruction: |
  If you're unsure what tools you have access to, call:
  show_my_available_tools()
  
  This will return a complete list with descriptions.
```

### ✅ DO: Validate Tools at Startup

```python
from patientmap.tools import validate_agent_tools

config = AgentConfig("agent.yaml").get_agent()
validation = validate_agent_tools(config.agent_name, config.tools)

if not validation["valid"]:
    print(f"❌ Agent {config.agent_name} has invalid configuration!")
    print(f"Missing tools: {validation['missing_tools']}")
    raise RuntimeError("Fix agent.yaml before proceeding")

print(f"✅ Agent {config.agent_name} validated successfully")
print(f"   {validation['total_valid']} tools loaded")
```

### ✅ DO: Use Bulk Operations

**Bad (inefficient individual calls):**
```python
tools = [
    "neo4j_add_condition",  # Individual
    "neo4j_add_medication",  # Individual
    "neo4j_link_article_to_condition"  # Individual
]
```

**Good (efficient bulk operations):**
```python
tools = [
    "neo4j_bulk_add_conditions",  # Batch process
    "neo4j_bulk_add_medications",  # Batch process
    "neo4j_bulk_link_articles_to_conditions"  # Batch process
]
```

### ❌ DON'T: Reference Non-Existent Tools in Instructions

**Bad:**
```yaml
instruction: |
  Use transfer_to_agent() to hand control back to orchestrator.
  # ← Tool doesn't exist! Will cause runtime error
  
tools: []  # ← Empty tools list but instructions mention transfer_to_agent
```

**Good:**
```yaml
instruction: |
  When you complete your work, simply provide your final response.
  Sub-agents automatically return control when they finish - no transfer needed.
  
  **YOU DO NOT HAVE transfer_to_agent** - any attempt to call it will fail.
  
tools: []  # ← Consistent with instruction
```

### ❌ DON'T: Mix Registry and Hardcoded Tools

**Bad (inconsistent):**
```python
# Don't do this - mixing patterns causes confusion
from google.adk.tools import google_search
from patientmap.tools import get_tools_from_config

config = AgentConfig("agent.yaml").get_agent()
yaml_tools = get_tools_from_config(config.tools)

# Mixing YAML-loaded and hardcoded tools
tools = [google_search] + yaml_tools  # ← Confusing!
```

**Good (consistent):**
```python
# Use registry consistently
config = AgentConfig("agent.yaml").get_agent()
tools = get_tools_from_config(config.tools)  # All from YAML
```

## Adding New Tools

### Step 1: Create the Tool Function

```python
# patientmap/tools/my_new_tools.py

def my_custom_tool(parameter: str, tool_context: ToolContext) -> str:
    """
    Do something custom.
    
    Args:
        parameter: Input parameter
        tool_context: ADK tool context
        
    Returns:
        Result string
    """
    # Implementation
    return f"Processed: {parameter}"
```

### Step 2: Register in tool_registry.py

```python
# Import your new tool
from patientmap.tools.my_new_tools import my_custom_tool

# Add to TOOL_REGISTRY
TOOL_REGISTRY: Dict[str, Any] = {
    # ... existing tools ...
    
    # Your new tool
    "my_custom_tool": my_custom_tool,
}

# Add to TOOL_DESCRIPTIONS
TOOL_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    # ... existing descriptions ...
    
    "my_custom_tool": {
        "category": "Custom",
        "description": "Do something custom with parameters",
        "usage": "my_custom_tool(parameter: str, tool_context: ToolContext) -> str"
    },
}
```

### Step 3: Use in Agent YAML

```yaml
agent_id: my_agent
tools:
  - my_custom_tool  # ← Now available!
```

### Step 4: Load in Agent Code

```python
# agent.py - No changes needed!
# Tool registry automatically picks up new tools
config = AgentConfig("agent.yaml").get_agent()
tools = get_tools_from_config(config.tools)  # Includes my_custom_tool
```

## Debugging Tool Issues

### Issue: "Tool 'X' not found in TOOL_REGISTRY"

**Cause:** Tool name in YAML doesn't match registry.

**Solution:**
```python
# Check what's available
from patientmap.tools import ALL_TOOL_NAMES
print("Available tools:", ALL_TOOL_NAMES)

# Validate specific agent
from patientmap.tools import validate_agent_tools
result = validate_agent_tools("my_agent", ["tool1", "tool2", "fake_tool"])
print(result)
# Output: {'valid': False, 'missing_tools': ['fake_tool'], ...}
```

### Issue: LLM Keeps Hallucinating Non-Existent Tools

**Cause:** Agent instructions don't explicitly list available tools.

**Solution:** Add explicit tool documentation to YAML:
```yaml
instruction: |
  **YOUR AVAILABLE TOOLS (use ONLY these):**
  1. google_search - Search Google
  2. url_context - Fetch URL content
  
  **TOOLS YOU DO NOT HAVE (do not call these):**
  - transfer_to_agent (does not exist)
  - save_file (does not exist)
  - execute_code (does not exist)
  
  Call show_my_available_tools() if you need to verify.
```

### Issue: Tools Not Loading from YAML

**Cause:** YAML format error or import issue.

**Solution:**
```python
# Test YAML loading
from patientmap.common.config import AgentConfig
config = AgentConfig("agent.yaml").get_agent()
print("Tools in YAML:", config.tools)

# Test tool conversion
from patientmap.tools import get_tools_from_config
tools = get_tools_from_config(config.tools)
print(f"Loaded {len(tools)} tools successfully")
```

## Testing the Registry

```python
# Run the registry module directly to see summary
python -m patientmap.tools.tool_registry

# Output:
# ================================================================================
# PATIENTMAP TOOL REGISTRY SUMMARY
# ================================================================================
# 
# Total tools registered: 35
# 
# ADK Built-in Tools: 3
# Research Tools: 4
# Neo4j Tools: 28
# ...
```

## Migration Guide for Existing Agents

If you have agents with hardcoded tools, follow this migration path:

### Before (Hardcoded):
```python
# agent.py
from google.adk.tools import google_search, url_context, exit_loop

research_agent = LlmAgent(
    name="research_agent",
    tools=[google_search, url_context, exit_loop]  # ← Hardcoded
)
```

### After (Registry-Based):

**Step 1: Create YAML config**
```yaml
# agent.yaml
agent_id: research_agent
agent_name: Research Agent
tools:
  - google_search
  - url_context
  - exit_loop
```

**Step 2: Update Python code**
```python
# agent.py
from pathlib import Path
from patientmap.common.config import AgentConfig
from patientmap.tools import get_tools_from_config

current_dir = Path(__file__).parent
config = AgentConfig(str(current_dir / "agent.yaml")).get_agent()
tools = get_tools_from_config(config.tools)

research_agent = LlmAgent(
    name=config.agent_name,
    tools=tools  # ← Loaded from registry
)
```

**Step 3: Test**
```python
# Validate configuration
from patientmap.tools import validate_agent_tools
result = validate_agent_tools(config.agent_name, config.tools)
assert result["valid"], f"Invalid tools: {result['missing_tools']}"
```

## Summary

The Tool Registry provides:

1. ✅ **Single Source of Truth**: All tools in one place
2. ✅ **Runtime Validation**: Catch errors at startup
3. ✅ **Self-Documentation**: Agents can query their capabilities
4. ✅ **Consistent Loading**: YAML → Registry → Agent
5. ✅ **Clear Metadata**: Category, description, usage for each tool
6. ✅ **Easy Extension**: Add new tools in three steps

By using the Tool Registry consistently, you'll:
- Reduce LLM hallucination of non-existent tools
- Catch configuration errors early
- Make agent capabilities explicit and documented
- Simplify agent development and maintenance
