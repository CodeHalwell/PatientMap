# Agent Tool Access Standards

**Last Updated:** 2025-01-XX  
**Purpose:** Ensure all agents have crystal-clear documentation of their tool access to prevent runtime errors

## Overview

This document establishes standards for documenting tool access in agent YAML configuration files. Following these patterns prevents agents from attempting to call tools they don't have access to.

## Audit Summary

- **Total Agents:** 35
- **Fixed Issues:** 16 clinical specialists had instructions referencing unavailable tools
- **Standardized:** All agents now have explicit tool access documentation

---

## Standard Templates

### Template A: NO_TOOLS Pattern (Coordinators/Reviewers)

**Use for:** orchestrator, data_manager, data_gatherer, research_manager, reviewer_agent, roundtable agents, final_report_agent, clinical_agent (director)

```yaml
agent_id: example_id
agent_name: example_agent
model: 'gemini-2.5-pro' # or gemini-2.5-flash
description: >
  Brief description of agent role
instruction: |
  Clear instructions WITHOUT any tool references.
  
  Focus on agent's coordination, review, or discussion role.
  
  Do NOT mention specific tools by name.
  
  Detect completion of each step and proceed to the next automatically, notifying
  the user briefly at each transition.
tools: []
```

---

### Template B: HAS_TOOLS Pattern (Working Agents)

**Use for:** research_agent, clinical_checker_agent, knowledge graph agents

```yaml
agent_id: example_id
agent_name: example_agent
model: 'gemini-2.5-flash'
description: >
  Brief description of agent role
instruction: |
  **CRITICAL TOOL ACCESS - YOU HAVE EXACTLY X TOOLS:**
  Your available tools are ONLY:
  1. tool_name_one
  2. tool_name_two
  3. tool_name_three
  
  **DO NOT call any other tools** including:
  - NO tool_x (explain who has it)
  - NO tool_y (explain restriction)
  - NO file operations, search tools, etc.
  - If you need something outside your toolset, [specify alternative action]
  
  [Rest of instructions that reference ONLY the listed tools]
  
  Detect completion of each step and proceed to the next automatically, notifying
  the user briefly at each transition.
tools: [tool_name_one, tool_name_two, tool_name_three]  # Must match instruction list
```

---

### Template C: CLINICAL SPECIALIST Pattern

**Use for:** All 16 clinical specialist agents

```yaml
agent_id: ca01
agent_name: cardiology_specialist_agent
model: 'gemini-2.5-flash'
description: |
  A board-certified [specialty] agent specializing in [domain].
instruction: |
  You are a board-certified [specialist] reviewing this patient case.
  
  **CRITICAL TOOL ACCESS RESTRICTION:**
  - **YOU HAVE NO TOOLS AVAILABLE** - Your tools list is empty: []
  - **DO NOT attempt to call ANY tools** including:
    * NO search_pubmed, google_scholar_tool, semantic_scholar_tool, wikipedia_tool
    * NO checker_agent or any other agents
    * NO database queries, file operations, or external API calls
  - **Rely on your expert knowledge** as a board-certified [specialist]
  - Base recommendations on established clinical guidelines ([relevant guidelines])
  - **IF you need external data, state it clearly** in your recommendations rather than attempting tool calls
  - **ALWAYS include references/citations** but these should be from your training knowledge, not tool-retrieved

  **Your Clinical Focus:**
  - [List of specialties]
  
  [Rest of clinical workflow instructions]
tools: []
```

---

## Critical Rules

### 1. Tools List Must Match Instructions

❌ **WRONG:** Instructions mention `search_pubmed` but `tools: []`  
✅ **CORRECT:** Either add tool to list OR remove reference from instructions

### 2. Explicit Tool Access Section Required

All agents with `tools: [...]` (non-empty) MUST have:
```yaml
instruction: |
  **CRITICAL TOOL ACCESS - YOU HAVE EXACTLY X TOOLS:**
  Your available tools are ONLY:
  1. [list each tool]
  
  **DO NOT call any other tools** including:
  - [list common tools this agent should NOT use]
```

### 3. No Tools = Explicit Statement

All agents with `tools: []` MUST have:
```yaml
instruction: |
  **CRITICAL TOOL ACCESS RESTRICTION:**
  - **YOU HAVE NO TOOLS AVAILABLE** - Your tools list is empty: []
  - **DO NOT attempt to call ANY tools**
```

### 4. Domain Boundaries Documented

Agents with overlapping capabilities must document:
- What they CAN do (their domain)
- What they CANNOT do (other agent's domain)
- Why the restriction exists

**Example:** Research enricher can add articles but NOT conditions (clinical agent's domain)

---

## Fixed Issues Log

### Issue 1: Clinical Specialists Tool Mismatch

**Problem:** All 16 clinical specialist agents had `tools: []` but instructions contained:
```yaml
**TOOL USAGE GUIDANCE:**
- Use search_pubmed for medical literature
- Use google_scholar_tool for guidelines
- ALWAYS use the checker_agent to validate
```

**Root Cause:** Copy-paste from template that assumed tools would be added later

**Resolution:** Replaced tool usage section with explicit "NO TOOLS AVAILABLE" statements

**Affected Agents:**
1. cardiology_agent
2. clinical_pharmacy_agent
3. endocrinology_agent
4. gastroenterology_agent
5. geriatrics_agent
6. hematology_agent
7. infectious_disease_agent
8. nephrology_agent
9. neurology_agent
10. nutrition_dietetics_agent
11. pain_medicine_agent
12. palliative_care_agent
13. physical_medicine_rehabilitation_agent
14. psychiatry_agent
15. pulmonology_agent
16. rheumatology_agent

---

## Agent Inventory by Pattern

### NO_TOOLS Agents (17 total)

**Coordinators:**
- orchestrator_agent.yaml
- data_manager_agent.yaml
- research_manager_agent.yaml
- clinical_agent.yaml (specialist coordinator)
- report_manager_agent.yaml

**Triage/Collection:**
- data_gatherer_agent.yaml

**Review/Discussion:**
- reviewer_agent.yaml
- moderator_agent.yaml
- evidence_synthesizer_agent.yaml
- insight_integrator_agent.yaml
- final_report_agent.yaml

**Clinical Specialists (16):**
- [All specialist agents listed above]

### HAS_TOOLS Agents (18 total)

**Data Initialization (11 tools):**
- kg_initialiser.yaml (builder) - 10 Neo4j tools
- kg_initialiser_checker.yaml - 6 Neo4j read tools + exit_loop

**Research Phase:**
- research_agent.yaml - 2 search tools (google_search, url_context)
- verification_agent.yaml - 2 search tools

**Research Enrichment (13 tools):**
- knowledge_graph_agent.yaml (enricher) - 11 Neo4j tools
- kg_enricher_checker.yaml - 6 Neo4j read tools + exit_loop

**Clinical Enrichment (9 tools):**
- clinical_kg_agent.yaml - 8 Neo4j tools
- clinical_checker_agent.yaml - 6 Neo4j read tools + exit_loop

**Report Phase:**
- report_manager_agent.yaml - 2 sub-agents as tools

---

## Maintenance Guidelines

### When Adding New Agents

1. **Choose appropriate template** (NO_TOOLS or HAS_TOOLS)
2. **If HAS_TOOLS:**
   - List all tools in `tools: []` array
   - Add "CRITICAL TOOL ACCESS" section listing exact same tools
   - Add "DO NOT call" section for common tool confusion
3. **If NO_TOOLS:**
   - Ensure `tools: []` is empty
   - Add "CRITICAL TOOL ACCESS RESTRICTION" section
   - Never mention specific tools by name in instructions

### When Modifying Existing Agents

1. **Before adding tool to instructions:**
   - Verify tool exists in `tools: []` list
   - Update tool count in "YOU HAVE EXACTLY X TOOLS" section
   - Add tool to numbered list

2. **Before removing tool:**
   - Remove from `tools: []` list
   - Remove from "available tools" numbered list
   - Update tool count
   - Consider adding to "DO NOT call" section if commonly confused

### Validation Checklist

Run this check after any agent YAML modification:

```bash
# Check for tool usage guidance mismatches
grep -r "TOOL USAGE GUIDANCE:" **/*_agent.yaml
# Should return 0 matches - this phrase was in buggy configs

# Check all agents have tool access documentation
grep -r "CRITICAL TOOL ACCESS" **/*_agent.yaml
# Should return 18 matches (all HAS_TOOLS + all NO_TOOLS agents)

# Verify tools list matches instructions
# Manual review: For each agent with tools, count:
# - Items in tools: []
# - Items in "YOU HAVE EXACTLY X TOOLS" list
# - These numbers must match exactly
```

---

## Design Rationale

### Why Explicit Tool Restrictions?

**Problem:** LLMs may hallucinate tool calls if instructions are ambiguous
- "Use search_pubmed" suggests the tool exists
- Agent attempts to call unavailable tool
- Runtime error: "Tool not found"

**Solution:** Make restrictions impossible to misunderstand
- "YOU HAVE NO TOOLS AVAILABLE"
- "DO NOT attempt to call ANY tools"
- List specific tools that might be confused as available

### Why Clinical Specialists Have No Tools?

**Architecture Decision:**
- Clinical director (`clinical_agent`) calls specialists as tools
- Specialists provide expert analysis from training data
- Research/database access handled by dedicated agents
- Prevents: Tool access sprawl, duplicate API calls, inconsistent data

**Benefits:**
- Faster specialist responses (no I/O)
- Clearer separation of concerns
- Specialists focus on clinical reasoning
- Research/data agents handle external queries

### Why Builder/Checker Split?

**Pattern:** Loop agents use builder/checker architecture

**Builder:**
- Has write tools (add, create, bulk operations)
- Does NOT have exit_loop tool
- Builds until checker signals completion

**Checker:**
- Has read-only tools (get, find, analyze)
- HAS exit_loop tool
- Validates builder's work
- Decides when loop terminates

**Why this split?**
- Prevents infinite loops (builder can't exit own loop)
- Enforces validation step (checker must review)
- Clear roles (one builds, one validates)

---

## Related Documentation

- [Agent Architecture Overview](./01_Index_And_Overview.md)
- [Clinical Agent Implementation](./03_Clinical_Agent_Implementation.md)
- [Google ADK Framework](./09_Google_ADK_Framework.md)
- [Main Copilot Instructions](../.github/copilot-instructions.md)

---

## Version History

- **v1.0** (2025-01-XX): Initial standards document
  - Fixed 16 clinical specialist tool mismatches
  - Standardized 3 template patterns
  - Documented all 35 agents
