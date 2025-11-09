# Clinical Researcher Agent - Tool Library Reference

## Overview
This directory contains comprehensive guides for five essential Python libraries that power the **Clinical Researcher Agent** - an AI system for researching medical conditions, analyzing peer-reviewed literature, and synthesizing clinical evidence. These guides document each library's role as a research tool integrated into the agent's toolkit.

## Agent Tool Stack Overview

The Clinical Researcher Agent uses a **two-tier tool architecture**:

### Primary Tools (Literature Research)
1. **Semantic Scholar** - Paper discovery and retrieval
2. **Habanero** - DOI metadata and enrichment
3. **PyTrials** - Clinical trials discovery

### Secondary Tools (Data Analysis)  
4. **Biopython** - Biological data processing
5. **pyOpenMS** - Mass spectrometry analysis

---

## Libraries Included

### 1. **Biopython** - Biological Sequence Analysis ⚙️ *Secondary Tool*
- **File**: `01_biopython_guide.md`
- **Purpose**: Provides tools for sequence analysis, alignment, and phylogenetic analysis
- **Key Features**:
  - Sequence manipulation (Seq objects)
  - Reading/writing biological file formats (FASTA, GenBank, FASTQ)
  - BLAST analysis
  - Sequence alignment
  - Phylogenetic tree analysis
  - BioSQL database integration
- **Installation**: `pip install biopython`
- **Best For**: Genomic and proteomic data analysis

### 2. **pyOpenMS** - Mass Spectrometry Data Analysis ⚙️ *Secondary Tool*
- **File**: `02_pyopenms_guide.md`
- **Purpose**: Comprehensive wrapper for OpenMS C++ library for MS data processing
- **Key Features**:
  - Raw MS data handling (mzML, mzXML formats)
  - Peak detection and feature finding
  - Data alignment and normalization
  - Quantification methods (isobaric, absolute quantitation)
  - Quality control reporting (mzQC)
  - Efficient data structures for large datasets
- **Installation**: `pip install pyopenms`
- **Best For**: Proteomics and metabolomics data analysis

### 3. **Semantic Scholar** - Academic Literature Search 🔍 *PRIMARY TOOL*
- **File**: `03_semanticscholar_guide.md`
- **Purpose**: Python client for querying academic paper metadata and citations
- **Key Features**:
  - Search scholarly articles
  - Retrieve paper metadata (title, authors, abstract, citations)
  - Author information lookup
  - Paper recommendations
  - Bulk search capabilities
  - Pagination support
  - Async/await support
- **Installation**: `pip install semanticscholar`
- **Best For**: Literature mining and research discovery

### 4. **Habanero** - CrossRef Bibliographic Data 📚 *PRIMARY TOOL*
- **File**: `04_habanero_guide.md`
- **Purpose**: Python client for CrossRef API to access DOI and citation metadata
- **Key Features**:
  - Search scholarly works by DOI
  - Query journal information
  - Find funder data
  - Advanced field-based searching
  - Boolean operators support
  - Citation data retrieval
  - Filtering by publication type, license, and more
- **Installation**: `pip install habanero`
- **Best For**: Citation tracking and DOI metadata retrieval

### 5. **PyTrials** - Clinical Trials Data 🏥 *PRIMARY TOOL*
- **File**: `05_pytrials_guide.md`
- **Purpose**: Access clinical trials data from ClinicalTrials.gov and other registries
- **Key Features**:
  - Search trials by condition, intervention, or location
  - Filter by phase, status, and sponsor
  - Extract trial eligibility criteria
  - Access outcomes and endpoints
  - Analyze trial metadata
  - Support for multiple registries
- **Installation**: `pip install pytrials`
- **Best For**: Clinical trials research and patient recruitment

## Quick Reference

### Installation of All Libraries
```bash
pip install biopython pyopenms semanticscholar habanero pytrials
```

### Common Usage Patterns

#### Biological Data Analysis (Biopython)
```python
from Bio import SeqIO
records = SeqIO.parse("sequences.fasta", "fasta")
```

#### Mass Spectrometry Analysis (pyOpenMS)
```python
import pyopenms as oms
exp = oms.MSExperiment()
oms.MzMLFile().load("data.mzML", exp)
```

### Semantic Scholar - Clinical Use
```python
# Agent searches for evidence on a medical condition
from semanticscholar import SemanticScholar

sch = SemanticScholar()
papers = sch.search_paper(
    query="Type 2 Diabetes management metformin GLP-1",
    fields=["title", "year", "citationCount", "abstract", "doi"],
    year_start=2021,           # Recent evidence
    citation_limit=100,        # High-impact papers
    publication_type="JournalArticle"
)

for paper in papers[:5]:
    print(f"{paper.title} ({paper.year}) - {paper.citationCount} citations")
```

### Habanero - Metadata Enrichment
```python
# Agent enriches papers with DOI metadata
from habanero import Crossref

cr = Crossref()
paper_metadata = cr.works(doi="10.1016/S0140-6736(23)01234-5")

message = paper_metadata['message']
print(f"Journal: {message['container-title']}")
print(f"Authors: {', '.join([a['family'] for a in message['author']])}")
print(f"Published: {message['published-online']['date-time']}")
```

### PyTrials - Active Trials Research
```python
# Agent searches for clinical trials
from pytrials import ClinicalTrials

ct = ClinicalTrials()
trials = ct.get_full_studies(
    search_expr="Type 2 Diabetes AND metformin",
    status="RECRUITING",
    phase="Phase 3|Phase 4"  # Confirmatory research
)

for trial in trials[:3]:
    print(f"NCT: {trial['StudyFirstPostDate']}")
    print(f"Status: {trial['OverallStatus']}")
```

## Clinical Researcher Agent Workflow

### Research Pipeline
The agent follows this process when given a clinical research query:

```
1. USER QUERY
   "What is the latest evidence for Type 2 Diabetes treatment?"
   
   ↓
   
2. SEMANTIC SCHOLAR SEARCH
   - Search for papers on diabetes treatment
   - Filter by year (recent evidence), citations (impact)
   - Get abstracts and metadata
   
   ↓
   
3. HABANERO ENRICHMENT
   - Look up DOI metadata for each paper
   - Retrieve full citation, journal info, authors
   - Add publication date and citation count
   
   ↓
   
4. PYTRIALS SEARCH (PARALLEL)
   - Search for active clinical trials on diabetes
   - Filter by phase, recruitment status
   - Extract eligibility criteria and outcomes
   
   ↓
   
5. DATA ANALYSIS (OPTIONAL)
   - If sequence/MS data needed, use Biopython/pyOpenMS
   - Process genomic or protein data from studies
   
   ↓
   
6. SYNTHESIS
   - Combine findings into evidence summary
   - Rank by citation count and trial phase
   - Provide researcher with actionable insights
```

### Agent Tool Invocation
```python
from agents.clinical.agent import ClinicalResearcherAgent

agent = ClinicalResearcherAgent()

# Agent automatically uses appropriate tools
response = agent.run(
    "What is the current evidence for metformin vs GLP-1 agonists for Type 2 Diabetes?"
)

# Response includes:
# - Recent papers with links
# - Active clinical trials
# - Evidence summary
# - Cited research
```

## Clinical Research Feature Comparison

| Feature | Semantic Scholar | Habanero | PyTrials | Biopython | pyOpenMS |
|---------|------------------|----------|----------|-----------|----------|
| **Paper Discovery** | ✅ Full-text search | ✅ DOI search | N/A | N/A | N/A |
| **Metadata Retrieval** | ✅ Abstract, citations | ✅ Complete metadata | ✅ Trial details | N/A | N/A |
| **Year Filtering** | ✅ | ✅ | N/A | N/A | N/A |
| **Citation Ranking** | ✅ High-impact papers | ✅ Citation count | N/A | N/A | N/A |
| **Clinical Trials** | N/A | N/A | ✅ Active trials | N/A | N/A |
| **Phase Filtering** | N/A | N/A | ✅ Phase 1-4 | N/A | N/A |
| **Biological Data** | N/A | N/A | N/A | ✅ FASTA, GenBank | ✅ mzML, mzXML |
| **Batch Queries** | ✅ Up to 1000 | ✅ Multiple queries | ✅ Parallel search | ✅ FASTA files | ✅ Batch processing |
| **API Rate Limiting** | ⚠️ Manual handling | ⚠️ 0.5-1s delays | ✅ Generous | N/A | N/A |
| **Best For Agent** | 🌟 PRIMARY | 🌟 PRIMARY | 🌟 PRIMARY | ⚙️ Secondary | ⚙️ Secondary |

## API Rate Limits & Agent Resilience

### Semantic Scholar
- **Rate Limit**: 100 requests per 5 minutes
- **Agent Strategy**: Batch queries, implement exponential backoff
- **Timeout**: 30 seconds
- **Recommendation**: Use API key for higher limits

### Habanero (CrossRef)
- **Rate Limit**: Respectful use recommended (0.5-1s between requests)
- **Agent Strategy**: Add delays, cache DOI lookups
- **Timeout**: 15 seconds
- **Note**: Non-commercial use is encouraged

### PyTrials (ClinicalTrials.gov)
- **Rate Limit**: Generous for research use
- **Agent Strategy**: Can make multiple rapid queries
- **Timeout**: 30 seconds
- **Benefit**: No artificial rate limiting

### Biopython & pyOpenMS
- **Rate Limit**: None (local processing only)
- **Agent Strategy**: Memory-efficient for large datasets
- **Note**: Handle large files with streaming/chunking

### Agent Resilience Implementation
```python
import time
import random
from typing import List

class ClinicalResearchAgent:
    def search_papers_with_backoff(self, queries: List[str]):
        """Search with exponential backoff for rate limits"""
        for i, query in enumerate(queries):
            try:
                results = self.scholar.search_paper(query)
                return results
            except RateLimitExceeded:
                wait_time = 2 ** i + random.uniform(0, 1)
                print(f"Rate limited. Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
    
    def search_with_caching(self, doi: str):
        """Cache DOI lookups to avoid duplicate calls"""
        if doi in self.doi_cache:
            return self.doi_cache[doi]
        
        result = self.habanero.works(doi=doi)
        self.doi_cache[doi] = result
        time.sleep(0.5)  # Respectful rate limiting
        return result
```

## Troubleshooting

### Common Issues

**Biopython - ImportError**
```python
# Verify installation
import Bio
```

**pyOpenMS - Missing dependencies**
- Install NumPy: `pip install numpy`
- Check platform compatibility

**Semantic Scholar - Rate limiting**
- Use API key for higher limits
- Implement exponential backoff

**Habanero - Empty results**
- Verify query syntax
- Check filter parameters
- Use simpler search terms

**PyTrials - No results**
- Verify condition names
- Try broader location criteria
- Check recruitment status

## Performance Tips

1. **Batch Operations**: Use batch endpoints when available
2. **Caching**: Store results locally to avoid repeated API calls
3. **Pagination**: Implement proper pagination for large datasets
4. **Asynchronous Processing**: Use async clients (Semantic Scholar)
5. **Memory Management**: Use streaming/on-disk processing for large files

## Resources

### Documentation Links
- **Biopython**: http://biopython.org
- **pyOpenMS**: https://pyopenms.readthedocs.io
- **Semantic Scholar**: https://www.semanticscholar.org/product/api
- **CrossRef (Habanero)**: https://github.com/CrossRef/rest-api-doc
- **ClinicalTrials.gov**: https://clinicaltrials.gov/api/gui

### Key Publications
- Cock et al. (2009) - "Biopython: freely available Python tools for computational molecular biology"
- Röst et al. (2016) - "OpenMS: a flexible open-source software platform for mass spectrometry data analysis"

## Contributing
For improvements or corrections to these guides, please refer to the main project documentation.

## License
Documentation provided for educational and research purposes.

---

**Last Updated**: 2024
**Total Files**: 5 comprehensive guides + this index
**Total Content**: 10,000+ lines of documentation and examples
