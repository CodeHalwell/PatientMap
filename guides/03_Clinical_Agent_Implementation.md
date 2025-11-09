# Clinical Researcher Agent - Implementation Reference

## Overview
This document provides implementation guidance for building a Clinical Researcher Agent using the five library tools documented in this repository. The agent automatically selects and chains tools to research medical conditions, analyze clinical evidence, and synthesize findings.

## Agent Architecture

### Tool Stack
```
Clinical Researcher Agent
├── Primary Tools (Literature Research)
│   ├── Semantic Scholar → Paper discovery & search
│   ├── Habanero → DOI enrichment & metadata
│   └── PyTrials → Clinical trials discovery
└── Secondary Tools (Data Analysis)
    ├── Biopython → Genomic/sequence analysis
    └── pyOpenMS → Mass spectrometry analysis
```

### Execution Flow
```
USER QUERY
    ↓
[Query Parsing & Classification]
    ↓
[Primary Tool Selection]
    ├─→ Semantic Scholar (paper search)
    ├─→ Habanero (DOI enrichment)
    └─→ PyTrials (trials search)
    ↓
[Optional Secondary Tools]
    ├─→ Biopython (if sequence data mentioned)
    └─→ pyOpenMS (if proteomics data mentioned)
    ↓
[Result Synthesis & Formatting]
    ↓
CLINICAL SUMMARY (with sources)
```

---

## Implementation Pattern 1: Multi-Source Literature Discovery

### Purpose
Research a medical condition by combining literature and trials data

### Implementation
```python
from semanticscholar import SemanticScholar
from habanero import Crossref
from pytrials import ClinicalTrials
import time

class ClinicalResearcherAgent:
    def __init__(self):
        self.scholar = SemanticScholar()
        self.crossref = Crossref()
        self.trials = ClinicalTrials()
        self.results_cache = {}
    
    def research_condition(self, condition: str, years_back: int = 5):
        """Research a medical condition with multi-source discovery"""
        
        research_data = {
            'condition': condition,
            'papers': [],
            'trials': [],
            'summary': {}
        }
        
        # 1. Search literature
        print(f"Searching literature for {condition}...")
        papers = self.scholar.search_paper(
            query=condition,
            fields=["title", "year", "citationCount", "abstract", "doi"],
            year_start=2024 - years_back,
            citation_limit=100,
            limit=20
        )
        
        # 2. Enrich papers with DOI metadata
        print("Enriching papers with metadata...")
        for paper in papers:
            try:
                doi_result = self.crossref.works(doi=paper.doi)
                msg = doi_result.get('message', {})
                
                enriched_paper = {
                    'title': paper.title,
                    'year': paper.year,
                    'citations': paper.citationCount,
                    'doi': paper.doi,
                    'journal': ', '.join(msg.get('container-title', ['Unknown'])[:1]),
                    'authors': len(msg.get('author', [])),
                    'abstract': paper.abstract[:300] if paper.abstract else 'N/A'
                }
                research_data['papers'].append(enriched_paper)
                
                # Respectful rate limiting
                time.sleep(0.5)
            except Exception as e:
                print(f"Error enriching {paper.title}: {e}")
                continue
        
        # 3. Search clinical trials
        print("Searching clinical trials...")
        try:
            trials = self.trials.get_full_studies(
                search_expr=condition,
                status="RECRUITING"
            )
            
            for trial in trials[:10]:
                trial_info = {
                    'nct_id': trial.get('NCTId', 'N/A'),
                    'title': trial.get('StudyTitle', 'N/A'),
                    'status': trial.get('OverallStatus', 'N/A'),
                    'phase': trial.get('Phase', 'N/A')
                }
                research_data['trials'].append(trial_info)
        except Exception as e:
            print(f"Error searching trials: {e}")
        
        # 4. Generate summary statistics
        research_data['summary'] = {
            'total_papers': len(research_data['papers']),
            'avg_citations': sum(p['citations'] for p in research_data['papers']) / max(1, len(research_data['papers'])),
            'recent_papers': sum(1 for p in research_data['papers'] if p['year'] >= 2023),
            'active_trials': len(research_data['trials']),
            'top_journals': self._get_top_journals(research_data['papers'])
        }
        
        return research_data
    
    def _get_top_journals(self, papers):
        """Extract top journals from papers"""
        journals = {}
        for paper in papers:
            journal = paper.get('journal', 'Unknown')
            journals[journal] = journals.get(journal, 0) + 1
        
        return sorted(journals.items(), key=lambda x: x[1], reverse=True)[:5]

# Usage
agent = ClinicalResearcherAgent()
results = agent.research_condition("Type 2 Diabetes")

print(f"\n=== RESEARCH SUMMARY: Type 2 Diabetes ===")
print(f"Papers Found: {results['summary']['total_papers']}")
print(f"Recent Papers (2023+): {results['summary']['recent_papers']}")
print(f"Average Citations: {results['summary']['avg_citations']:.1f}")
print(f"Active Trials: {results['summary']['active_trials']}")
print(f"\nTop Journals:")
for journal, count in results['summary']['top_journals']:
    print(f"  - {journal}: {count} papers")
```

---

## Implementation Pattern 2: Evidence Hierarchy Builder

### Purpose
Structure clinical evidence from strongest (RCTs) to weakest (observational)

### Implementation
```python
class EvidenceHierarchyBuilder:
    """Build evidence pyramid for clinical recommendations"""
    
    EVIDENCE_HIERARCHY = {
        'meta-analysis': 1,
        'randomized controlled trial': 2,
        'rct': 2,
        'cohort study': 3,
        'case control': 4,
        'case series': 5,
        'case report': 6,
        'expert opinion': 7
    }
    
    def __init__(self):
        self.scholar = SemanticScholar()
        self.trials = ClinicalTrials()
    
    def build_evidence_pyramid(self, condition: str, treatment: str):
        """Build evidence pyramid showing study types"""
        
        pyramid = {level: [] for level in range(1, 8)}
        
        # Search for different study types
        study_types = [
            ('meta-analysis', 'meta-analysis systematic review'),
            ('randomized controlled trial', 'randomized controlled trial RCT'),
            ('cohort study', 'cohort study'),
            ('case control', 'case control study'),
            ('case series', 'case series'),
        ]
        
        for study_type, query in study_types:
            print(f"Searching for {study_type}...")
            papers = self.scholar.search_paper(
                query=f"{condition} {treatment} {query}",
                fields=["title", "year", "citationCount"],
                limit=5
            )
            
            level = self.EVIDENCE_HIERARCHY.get(study_type, 7)
            pyramid[level] = [
                {
                    'title': p.title,
                    'year': p.year,
                    'citations': p.citationCount
                } for p in papers
            ]
        
        # Add active clinical trials at level 2
        try:
            trials = self.trials.get_full_studies(
                search_expr=f"{condition} AND {treatment}",
                phase="Phase 3|Phase 4"
            )
            pyramid[2].extend([
                {
                    'title': t.get('StudyTitle', 'Unknown'),
                    'nct': t.get('NCTId', 'N/A'),
                    'status': t.get('OverallStatus', 'N/A')
                } for t in trials[:3]
            ])
        except:
            pass
        
        return self._format_pyramid(pyramid)
    
    def _format_pyramid(self, pyramid):
        """Format pyramid for display"""
        levels_text = {
            1: "Systematic Reviews & Meta-analyses",
            2: "Randomized Controlled Trials & Active Trials",
            3: "Cohort Studies",
            4: "Case-Control Studies",
            5: "Case Series",
            6: "Case Reports",
            7: "Expert Opinion"
        }
        
        output = "\n=== EVIDENCE HIERARCHY ===\n"
        for level in range(1, 8):
            if pyramid[level]:
                output += f"\nLevel {level}: {levels_text[level]}\n"
                output += f"  ({len(pyramid[level])} studies)\n"
                for study in pyramid[level][:2]:
                    title = study.get('title', 'Unknown')[:60]
                    output += f"  - {title}...\n"
        
        return output

# Usage
builder = EvidenceHierarchyBuilder()
pyramid = builder.build_evidence_pyramid("Type 2 Diabetes", "metformin")
print(pyramid)
```

---

## Implementation Pattern 3: Treatment Comparison Engine

### Purpose
Compare evidence for different treatment options

### Implementation
```python
class TreatmentComparisonEngine:
    """Compare clinical evidence for treatment options"""
    
    def __init__(self):
        self.scholar = SemanticScholar()
        self.crossref = Crossref()
        self.trials = ClinicalTrials()
    
    def compare_treatments(self, condition: str, treatments: list):
        """Compare evidence across multiple treatments"""
        
        comparison = {}
        
        for treatment in treatments:
            print(f"\nAnalyzing {treatment}...")
            
            # Literature metrics
            papers = self.scholar.search_paper(
                query=f"{condition} {treatment}",
                year_start=2020,
                fields=["citationCount", "year"],
                limit=20
            )
            
            # Clinical trials
            try:
                trials = self.trials.get_full_studies(
                    search_expr=f"{condition} AND {treatment}"
                )
                active_trials = [t for t in trials 
                                if t.get('OverallStatus') == 'RECRUITING']
            except:
                active_trials = []
            
            # Calculate metrics
            comparison[treatment] = {
                'papers': len(papers),
                'avg_citations': sum(p.citationCount for p in papers) / max(1, len(papers)),
                'recent_papers': sum(1 for p in papers if p.year >= 2023),
                'active_trials': len(active_trials),
                'impact_score': self._calculate_impact(papers, len(active_trials))
            }
        
        return self._format_comparison(comparison)
    
    def _calculate_impact(self, papers, trials_count):
        """Calculate overall impact score"""
        avg_citations = sum(p.citationCount for p in papers) / max(1, len(papers))
        trials_weight = trials_count * 10
        paper_weight = avg_citations
        
        return (paper_weight + trials_weight) / 2 if (paper_weight + trials_weight) > 0 else 0
    
    def _format_comparison(self, comparison):
        """Format comparison for display"""
        output = "\n=== TREATMENT COMPARISON ===\n"
        output += f"{'Treatment':<20} {'Papers':<10} {'Avg Citations':<15} {'Trials':<10}\n"
        output += "-" * 55 + "\n"
        
        for treatment, metrics in sorted(
            comparison.items(),
            key=lambda x: x[1]['impact_score'],
            reverse=True
        ):
            output += f"{treatment:<20} {metrics['papers']:<10} "
            output += f"{metrics['avg_citations']:<15.1f} {metrics['active_trials']:<10}\n"
        
        return output

# Usage
engine = TreatmentComparisonEngine()
comparison = engine.compare_treatments(
    "Type 2 Diabetes",
    ["metformin", "GLP-1 agonist", "SGLT2 inhibitor", "insulin"]
)
print(comparison)
```

---

## Integration with Google ADK

### Setup in Google ADK Framework
```python
from google.adk import Agent, Runner
from google.adk.tools import tool

# Define clinical research tools
@tool
def search_papers(condition: str, years_back: int = 5) -> str:
    """Search for peer-reviewed papers on a medical condition"""
    agent = ClinicalResearcherAgent()
    results = agent.research_condition(condition, years_back)
    return format_results(results)

@tool
def find_clinical_trials(condition: str, status: str = "RECRUITING") -> str:
    """Find active clinical trials for a condition"""
    ct = ClinicalTrials()
    trials = ct.get_full_studies(search_expr=condition, status=status)
    return format_trials(trials)

@tool
def compare_treatments(condition: str, treatments: list) -> str:
    """Compare evidence across treatment options"""
    engine = TreatmentComparisonEngine()
    return engine.compare_treatments(condition, treatments)

# Create clinical researcher agent
clinical_agent = Agent(
    name="Clinical Researcher",
    description="Research medical conditions and clinical evidence",
    instruction="""You are a clinical research expert. When asked about medical conditions:
    1. Search for recent peer-reviewed literature
    2. Find active clinical trials
    3. Compare treatment options when requested
    4. Provide evidence-based summaries with citations""",
    tools=[search_papers, find_clinical_trials, compare_treatments]
)
```

---

## Rate Limiting & Resilience

### Backoff Strategy
```python
import time
import random
from typing import Optional

class RateLimitHandler:
    """Handle rate limiting with exponential backoff"""
    
    MAX_RETRIES = 3
    INITIAL_WAIT = 1  # seconds
    
    def __init__(self):
        self.request_log = []
    
    def execute_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff"""
        
        for attempt in range(self.MAX_RETRIES):
            try:
                result = func(*args, **kwargs)
                self.request_log.append({
                    'timestamp': time.time(),
                    'success': True
                })
                return result
            
            except RateLimitExceeded:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.INITIAL_WAIT * (2 ** attempt)
                    wait_time += random.uniform(0, 1)
                    print(f"Rate limited. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    raise
    
    def log_request(self):
        """Track requests for rate limiting compliance"""
        self.request_log.append({'timestamp': time.time()})
    
    def check_rate_limit(self, limit: int, window: int = 300):
        """Check if we're within rate limits"""
        now = time.time()
        recent = [r for r in self.request_log 
                 if now - r['timestamp'] < window]
        
        return len(recent) < limit
```

---

## Testing & Validation

### Unit Test Example
```python
import unittest

class TestClinicalAgent(unittest.TestCase):
    
    def setUp(self):
        self.agent = ClinicalResearcherAgent()
    
    def test_research_condition(self):
        """Test research on a condition"""
        results = self.agent.research_condition("Type 2 Diabetes", years_back=2)
        
        self.assertIn('papers', results)
        self.assertIn('trials', results)
        self.assertTrue(len(results['papers']) > 0)
    
    def test_evidence_hierarchy(self):
        """Test evidence hierarchy building"""
        builder = EvidenceHierarchyBuilder()
        pyramid = builder.build_evidence_pyramid("Diabetes", "metformin")
        
        self.assertIsInstance(pyramid, str)
        self.assertIn('EVIDENCE HIERARCHY', pyramid)
    
    def test_treatment_comparison(self):
        """Test treatment comparison"""
        engine = TreatmentComparisonEngine()
        comparison = engine.compare_treatments(
            "Type 2 Diabetes",
            ["metformin", "insulin"]
        )
        
        self.assertIsInstance(comparison, str)
        self.assertIn('TREATMENT COMPARISON', comparison)
```

---

## Deployment Checklist

- [ ] Semantic Scholar API key configured
- [ ] Habanero rate limiting implemented (0.5-1s delays)
- [ ] PyTrials queries tested
- [ ] Biopython/pyOpenMS optional dependencies verified
- [ ] Caching system implemented for DOI lookups
- [ ] Error handling for API failures
- [ ] Logging configured for debugging
- [ ] Rate limit monitoring in place
- [ ] Results formatting consistent
- [ ] Documentation URLs embedded in responses
- [ ] Citation tracking for reproducibility

---

## Best Practices

1. **Evidence Hierarchy**: Always present evidence from strongest (meta-analyses) to weakest (expert opinion)
2. **Recent Evidence**: Prioritize papers from last 3-5 years for current practices
3. **Citation Impact**: Use citation count as proxy for paper quality/influence
4. **Active Trials**: Include recruiting trials as evidence of ongoing research
5. **Source Attribution**: Always include DOI, journal, and year
6. **Rate Limiting**: Respect API limits with delays between requests
7. **Caching**: Cache DOI lookups to avoid duplicate calls
8. **Error Handling**: Gracefully handle API failures and continue with available data

---

## Resources

- **Semantic Scholar API**: https://www.semanticscholar.org/product/api
- **CrossRef API (Habanero)**: https://github.com/CrossRef/rest-api-doc
- **ClinicalTrials.gov API**: https://clinicaltrials.gov/api/gui
- **Google ADK Documentation**: [Link to ADK docs]

