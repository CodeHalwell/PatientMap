# PatientMap - Clinical Researcher Agent

A sophisticated AI agent for researching medical conditions, analyzing peer-reviewed clinical literature, and synthesizing evidence-based insights using multiple APIs and data sources.

## Overview

PatientMap uses a multi-tool approach to provide comprehensive clinical research capabilities:

**Research Tools**:
- **Semantic Scholar**: Search 200M+ academic papers on medical topics
- **Habanero (CrossRef)**: Retrieve DOI metadata and bibliographic information
- **PyTrials**: Discover active clinical trials from ClinicalTrials.gov
- **Biopython**: Analyze biological sequences and genomic data
- **pyOpenMS**: Process mass spectrometry data from proteomics studies

**Knowledge Graph Storage**:
- **Neo4j Aura**: **PRIMARY** persistent cloud-based graph database
  - ONE unified graph per patient across all workflow phases
  - No file operations needed - automatic cloud persistence
  - Multi-patient support with shared research articles
  - Production-grade graph database with ACID guarantees

## Project Structure

```
WellInformed/
├── guides/                          # Comprehensive library documentation
│   ├── 01_biopython_guide.md       # Sequence analysis reference
│   ├── 02_pyopenms_guide.md        # Mass spectrometry guide
│   ├── 03_semanticscholar_guide.md # Primary literature search tool
│   ├── 04_habanero_guide.md        # DOI metadata enrichment tool
│   ├── 05_pytrials_guide.md        # Clinical trials discovery tool
│   ├── CLINICAL_AGENT_REFERENCE.md # Agent implementation patterns
│   └── README.md                   # Library index & workflows
│
├── agents/                          # Agent implementations
│   ├── orchestrator/                # Coordinates multiple agents
│   ├── research/                    # Research agent
│   ├── clinical/                    # Clinical researcher agent
│   ├── reviewer/                    # Evidence reviewer
│   ├── knowledge_graph/             # Knowledge synthesis
│   ├── data_extraction/             # Data parsing
│   └── communication/               # Results formatting
│
├── main.py                          # Application entry point
├── pyproject.toml                  # Python dependencies (uv)
└── README.md                        # This file
```

## Getting Started

### Installation

```bash
# Clone repository
git clone <repo-url>
cd WellInformed

# Install dependencies using uv
uv sync

# Or with pip
pip install -e .
```

### Configuration

Create a `.env` file with your API credentials:

```env
# Required: Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# Required: Neo4j Aura (for persistent knowledge graphs)
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# Optional: Research APIs
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key  # Optional but recommended
CROSSREF_EMAIL=your@email.com                       # Required for Habanero
CLINICAL_TRIALS_API_KEY=your_clinical_trials_key    # Optional
```

### Quick Start

```bash
# Test Neo4j integration
python test_neo4j_integration.py

# Run unified workflow test (recommended first)
python test_unified_neo4j_workflow.py

# Run the agent system
cd src/patientmap
uv run adk web agents
```

Then interact with the agent system through the web interface to create patient knowledge graphs and conduct research.

### Unified Neo4j Workflow

**NEW**: PatientMap now uses **ONE persistent Neo4j graph per patient** across all workflow phases:

```
┌─────────────────────────────────┐
│   Neo4j Aura Cloud Database     │
│   (Single Persistent Graph)     │
└────────┬────────────────────────┘
         │
    ┌────┴─────┬──────────┐
    │          │          │
┌───▼───┐  ┌──▼───┐  ┌───▼────┐
│ Data  │  │Research│  │Clinical│
│ Phase │  │ Phase │  │ Phase  │
└───────┘  └────────┘  └────────┘
CREATE      UPDATE      UPDATE
Patient     + Research  + Clinical
```

**Key Benefits**:
- ✅ **Single Source of Truth**: ONE graph across data → research → clinical phases
- ✅ **No File Operations**: Automatic cloud persistence (no save/load)
- ✅ **Multi-Patient Support**: Unique constraints enable multiple patients
- ✅ **Production-Ready**: Enterprise Neo4j Aura with ACID guarantees

See [`docs/neo4j_unified_workflow.md`](docs/neo4j_unified_workflow.md) for complete guide.

## Core Features

### 1. Literature Discovery
Automatically searches peer-reviewed journals for evidence on:
- Medical conditions (diabetes, cancer, heart disease, etc.)
- Treatments and medications
- Diagnostic procedures
- Clinical outcomes

**Tools Used**: Semantic Scholar, Habanero

### 2. Clinical Trials Research
Find active and completed clinical trials:
- Filter by trial phase (Phase 1-4)
- Check recruitment status
- Review eligibility criteria
- Examine outcomes and endpoints

**Tools Used**: PyTrials

### 3. Evidence Synthesis
Combine multiple sources to create comprehensive summaries:
- Literature review with citation metrics
- Active trials and recruitment information
- Evidence hierarchy (strongest to weakest)
- Treatment comparisons

**Tools Used**: All primary tools

### 4. Biological Data Analysis
Process and analyze biological data:
- DNA/protein sequence analysis
- Mass spectrometry data processing
- Genomic alignment
- Phylogenetic analysis

**Tools Used**: Biopython, pyOpenMS (optional)

## Documentation

Comprehensive guides for each library are in the `/guides` directory:

- **[Semantic Scholar Guide](guides/03_semanticscholar_guide.md)** - Paper search & discovery
- **[Habanero Guide](guides/04_habanero_guide.md)** - DOI metadata & enrichment  
- **[PyTrials Guide](guides/05_pytrials_guide.md)** - Clinical trials research
- **[Biopython Guide](guides/01_biopython_guide.md)** - Sequence analysis
- **[pyOpenMS Guide](guides/02_pyopenms_guide.md)** - Mass spectrometry analysis
- **[Clinical Agent Reference](guides/CLINICAL_AGENT_REFERENCE.md)** - Agent implementation patterns

### Key Workflows

#### Research a Medical Condition
```python
# Agent automatically:
# 1. Searches Semantic Scholar for recent papers
# 2. Enriches results with Habanero DOI metadata
# 3. Finds active clinical trials
# 4. Synthesizes findings into evidence summary

response = agent.run("Research evidence for Type 2 Diabetes management")
```

#### Compare Treatment Options
```python
# Agent provides:
# - Papers per treatment
# - Average citation counts (impact)
# - Active clinical trials
# - Evidence hierarchy ranking

response = agent.run(
    "Compare evidence for metformin vs GLP-1 agonists for diabetes"
)
```

#### Find Active Clinical Trials
```python
# Agent searches for:
# - Recruiting trials
# - Trial phases and status
# - Eligibility criteria
# - Primary outcomes

response = agent.run("Find recruiting trials for Type 2 Diabetes in the US")
```

## API Usage & Rate Limits

| API | Rate Limit | Strategy |
|-----|-----------|----------|
| Semantic Scholar | 100 req/5min | Batch queries, add delays |
| Habanero/CrossRef | Respectful use | 0.5-1s between requests |
| PyTrials | Generous | Can query freely |
| Biopython | None | Local processing |
| pyOpenMS | None | Local processing |

## Configuration

Environment variables (`.env`):
```
SEMANTIC_SCHOLAR_API_KEY=your_key_here
CROSSREF_EMAIL=your_email@example.com
CLINICAL_TRIALS_API_KEY=optional
```

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Tools
1. Implement tool wrapper in `agents/`
2. Register with agent framework
3. Add documentation to `/guides`
4. Update this README

### Contributing
See CONTRIBUTING.md for guidelines.

## Architecture

### Agent Framework
Built on [Google ADK](guides/GOOGLE_ADK_REFERENCE.md) for:
- Multi-agent orchestration
- Tool integration
- State management
- Result synthesis

### Tool Pipeline
```
User Query
    ↓
Query Parser (classify research type)
    ↓
Primary Tools (literature, trials)
    ├─→ Semantic Scholar
    ├─→ Habanero
    └─→ PyTrials
    ↓
Optional Secondary Tools (data analysis)
    ├─→ Biopython
    └─→ pyOpenMS
    ↓
Results Aggregator
    ↓
Evidence Synthesizer
    ↓
Formatted Response (with citations)
```

## Performance & Optimization

- **Caching**: DOI lookups cached to reduce CrossRef calls
- **Batch Queries**: Up to 1000 papers per Semantic Scholar query
- **Rate Limiting**: Automatic backoff for API throttling
- **Parallelization**: Concurrent tool invocation when possible
- **Memory Efficient**: Streaming for large datasets

## Examples

### Example 1: Research Type 2 Diabetes
```python
agent = ClinicalResearcherAgent()
response = agent.run("""
    What is the latest evidence for Type 2 Diabetes management?
    Focus on the role of metformin and newer agents like GLP-1 agonists.
""")
```

### Example 2: Compare Treatments
```python
response = agent.run("""
    Compare clinical evidence for treating hypertension with:
    - ACE inhibitors
    - Beta blockers  
    - Calcium channel blockers
""")
```

### Example 3: Find Active Trials
```python
response = agent.run("""
    Find recruiting clinical trials for triple negative breast cancer
    with immunotherapy in the United States
""")
```

## Troubleshooting

### "Rate Limit Exceeded"
- Semantic Scholar: Provides API key for higher limits
- Habanero: Implement 0.5-1s delays between requests

### "No Results"
- Verify condition/disease name spelling
- Try broader search terms
- Check trial status (recruiting, active, etc.)

### "API Connection Error"
- Check internet connection
- Verify API endpoints are accessible
- Check API key credentials in environment

## Resources

- **Semantic Scholar**: https://www.semanticscholar.org
- **CrossRef**: https://www.crossref.org
- **ClinicalTrials.gov**: https://clinicaltrials.gov
- **Biopython**: http://biopython.org
- **OpenMS**: https://openms.de

## License

This project is licensed under [LICENSE FILE]. 

Clinical research data sourced from:
- Semantic Scholar (AI2)
- CrossRef (scholarly publishing)
- ClinicalTrials.gov (NIH)

## Citation

If you use WellInformed in your research, please cite:
```
@software{wellinformed2024,
  title={WellInformed: Clinical Researcher Agent},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/wellinformed}
}
```

## Support

For issues, questions, or contributions:
- GitHub Issues: [Link to issues]
- Email: [contact email]
- Documentation: [Link to docs]

---

**Last Updated**: November 9, 2024
**Status**: Active Development

