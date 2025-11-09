# Semantic Scholar - Clinical Research Agent Guide

## Overview
Semantic Scholar is the **PRIMARY tool** for the Clinical Researcher Agent to search and retrieve peer-reviewed academic papers on medical conditions, treatments, and clinical evidence.

The library provides access to **200+ million academic papers** with AI-powered search, citation analysis, and metadata retrieval. For clinical research, it enables:
- Evidence-based literature discovery
- High-impact paper identification (by citation count)
- Recent evidence filtering (by publication year)
- Condition-specific searches (diabetes, cancer, etc.)
- Treatment comparison research

## Clinical Use Cases

### 1. Literature Review on Medical Condition
```python
# Search for evidence on Type 2 Diabetes
from semanticscholar import SemanticScholar

sch = SemanticScholar()
papers = sch.search_paper(
    query="Type 2 Diabetes management treatment",
    fields=["title", "year", "citationCount", "abstract", "doi"],
    year_start=2020,  # Recent evidence
    limit=10
)
```

### 2. Evidence Synthesis by Citation Count
```python
# Find high-impact papers on a treatment
papers = sch.search_paper(
    query="metformin efficacy Type 2 Diabetes RCT",
    citation_limit=100,  # High-impact research
    fields=["title", "authors", "citationCount", "year"]
)

# Sort by impact
sorted_papers = sorted(papers, 
    key=lambda p: p.citationCount, reverse=True)
```

### 3. Recent Evidence Discovery
```python
# Get latest research on new treatments
papers = sch.search_paper(
    query="GLP-1 agonist cardiovascular outcomes",
    year_start=2023,  # Last 1-2 years
    fields=["title", "abstract", "venue", "year"]
)
```

### 4. Treatment Comparison Research
```python
# Compare evidence for different treatments
treatments = ["metformin", "GLP-1 agonist", "SGLT2 inhibitor"]
comparison_results = {}

for treatment in treatments:
    papers = sch.search_paper(
        query=f"{treatment} Type 2 Diabetes efficacy",
        year_start=2020,
        limit=5
    )
    comparison_results[treatment] = len(papers)
    print(f"{treatment}: {len(papers)} recent papers")
```

### Using pip
```bash
pip install semanticscholar
```

### From GitHub (Latest Development Version)
```bash
# Using VCS support
pip install git+https://github.com/danielnsilva/semanticscholar@master

# Or clone and install
git clone git@github.com:danielnsilva/semanticscholar.git
cd semanticscholar
pip install .
```

## Basic Usage

### Initializing the Client

#### Synchronous Client
```python
from semanticscholar import SemanticScholar

# Basic initialization
sch = SemanticScholar()

# With API key for authenticated requests
sch = SemanticScholar(api_key='your_api_key_here')

# With custom timeout
sch = SemanticScholar(timeout=5)

# Disable automatic retries for rate limiting
sch = SemanticScholar(retry=False)

# Update timeout after initialization
sch.timeout = 5
```

#### Asynchronous Client
```python
import asyncio
from semanticscholar import AsyncSemanticScholar

async def fetch_paper():
    sch = AsyncSemanticScholar()
    paper = await sch.get_paper('10.1093/mind/lix.236.433')
    return paper

paper = asyncio.run(fetch_paper())
```

## Fetching Paper Data

### Get Single Paper
```python
from semanticscholar import SemanticScholar

sch = SemanticScholar()

# Fetch paper by DOI
paper = sch.get_paper('10.1093/mind/lix.236.433')
print(paper.title)

# Access available fields
print(paper.keys())

# Access raw JSON data
print(paper.raw_data)
```

### Get Multiple Papers (Batch)
```python
# Fetch up to 1000 papers in a single call
list_of_paper_ids = [
    'CorpusId:470667',
    '10.2139/ssrn.2250500',
    '0f40b1f08821e22e859c6050916cec3667778613'
]
results = sch.get_papers(list_of_paper_ids)
```

## Searching Papers

### Basic Paper Search
```python
# Search by keyword
results = sch.search_paper('Computing Machinery and Intelligence')

# Get first page of results
first_page = results.items

# Fetch next page
results.next_page()
first_two_pages = results.items

# Iterate through all results
all_results = [item for item in results]
```

### Search with Query Parameters

#### Publication Year Filter
```python
# Restrict to specific year
results = sch.search_paper('turing test', year=2000)

# Date range (YYYY-MM-DD, YYYY-MM, or YYYY)
results = sch.search_paper('turing test', publication_date_or_year='2020-01-01:2021-12-31')
```

#### Publication Type Filter
```python
results = sch.search_paper('turing test', publication_type=['Journal', 'Conference'])
```

#### Open Access Filter
```python
results = sch.search_paper('turing test', open_access_pdf=True)
```

#### Venue Filter
```python
results = sch.search_paper('turing test', venue=['ESEM', 'ICSE', 'ICSME'])
```

#### Fields of Study Filter
```python
results = sch.search_paper('turing test', fields_of_study=['Computer Science', 'Education'])
```

#### Citation Count Filter
```python
results = sch.search_paper('turing test', min_citation_count=100)
```

#### Custom Field Selection
```python
results = sch.search_paper('software engineering', fields=['title', 'year'])
```

#### Custom Result Limit
```python
results = sch.search_paper('software engineering', limit=5)
```

### Advanced Search with Title Matching
```python
# Match title field specifically
paper = sch.search_paper(query='deep learning', match_title=True)
```

### Bulk Search
```python
# Retrieve large batch of papers (up to 10,000,000 total)
response = sch.search_paper(query='deep | learning', bulk=True)

# Retrieve highly-cited papers first
response = sch.search_paper(query='deep learning', bulk=True, sort='citationCount:desc')
```

## Paper Recommendations

### Recommend from Single Paper
```python
results = sch.get_recommended_papers('10.2139/ssrn.2250500')
```

### Recommend from Multiple Papers (Positive and Negative)
```python
positive_paper_ids = ['10.1145/3544585.3544600']
negative_paper_ids = ['10.1145/301250.301271']
results = sch.get_recommended_papers_from_lists(positive_paper_ids, negative_paper_ids)
```

## Author Information

### Get Single Author
```python
author = sch.get_author(2262347)
```

### Get Multiple Authors
```python
author_ids = ['3234559', '1726629', '1726629']
results = sch.get_authors(author_ids)
```

### Search Authors
```python
results = sch.search_author('Alan M. Turing')
```

## Autocomplete

### Get Paper Suggestions
```python
suggestions = sch.get_autocomplete('softw')
# Returns Autocomplete objects for matching papers
```

## Working with Paginated Results

### PaginatedResults Class
The library handles pagination automatically:

```python
results = sch.search_paper('Computing Machinery and Intelligence')

# Access first page items
first_page = results.items

# Fetch next page
results.next_page()

# Get all results across all pages
all_results = results.get_all_results()

# Iterate through results
for item in results:
    print(item.title)

# Access by index
item = results[0]

# Get total length
total = len(results)
```

## Debugging and Logging

### Enable Global Debug Logging
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Enable Library-Specific Debug Logging
```python
import logging
logging.getLogger('semanticscholar').setLevel(logging.DEBUG)
```

### Debug Output Example
```python
# Debug output includes:
# - HTTP Request details (method, URL)
# - Headers (including API key)
# - JSON payload
# - Equivalent cURL command

DEBUG:semanticscholar:HTTP Request: POST https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year
DEBUG:semanticscholar:Headers: {'x-api-key': 'F@k3K3y'}
DEBUG:semanticscholar:Payload: {'ids': ['CorpusId:470667', '10.2139/ssrn.2250500']}
DEBUG:semanticscholar:cURL command: curl -X POST -H 'x-api-key: F@k3K3y' ...
```

## API Endpoints Reference

### Graph API - Paper Endpoints

#### Paper Relevance Search
- **Endpoint**: `/graph/v1/paper/relevance_search`
- **Description**: Search papers by relevance to a query
- **Query Syntax**: Supports `|` for OR operations, multiple filters
- **Supported Sorting**: `paperId`, `publicationDate`, `citationCount`
- **Note**: `total` field reflects partial phrase matches only

#### Bulk Paper Search
- **Endpoint**: `/graph/v1/paper/bulk_search`
- **Description**: Retrieve large batches (up to 10,000,000 papers)
- **Bulk Parameter**: Must be `True` for bulk queries
- **Constraints**: Cannot use `bulk=True` with `match_title=True`

#### Batch Paper Request
- **Method**: POST
- **Endpoint**: `/graph/v1/paper/batch`
- **Request Format**:
```bash
curl -X POST -H "x-api-key: YOUR_API_KEY" \
  -d '{"ids": ["CorpusId:12345", "10.1000/xyz123"]}' \
  "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,authors,citationCount"
```

## Exception Handling

### Custom Exceptions
```python
from semanticscholar import (
    SemanticScholarException,
    APIException,
    RateLimitExceeded,
    InvalidRequestException,
    ResourceNotFoundException
)

try:
    paper = sch.get_paper('invalid_id')
except ResourceNotFoundException as e:
    print(f"Paper not found: {e}")
except RateLimitExceeded as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
except APIException as e:
    print(f"API Error {e.status_code}: {e.message}")
except SemanticScholarException as e:
    print(f"Error: {e}")
```

## Best Practices

1. **API Keys**: Use an API key for authenticated requests to avoid rate limiting
2. **Timeouts**: Set appropriate timeouts for your use case
3. **Batch Operations**: Use batch endpoints when fetching multiple items
4. **Pagination**: Implement proper pagination handling for large result sets
5. **Error Handling**: Handle exceptions properly for production code
6. **Logging**: Enable debug logging only when needed to diagnose issues
7. **Rate Limiting**: Implement delays between requests if needed

## Complete Example Workflow

```python
from semanticscholar import SemanticScholar

# Initialize
sch = SemanticScholar(api_key='your_api_key', timeout=5)

# Search for papers
results = sch.search_paper(
    'machine learning interpretability',
    year=2020,
    fields=['title', 'authors', 'citationCount'],
    limit=10
)

# Process results
for item in results.items:
    print(f"Title: {item.title}")
    print(f"Authors: {item.authors}")
    print(f"Citations: {item.citationCount}")
    
    # Get detailed paper info
    paper = sch.get_paper(item.paperId)
    print(f"Abstract: {paper.abstract}")
    
    # Get recommendations
    recommendations = sch.get_recommended_papers(item.paperId)
    print(f"Related papers: {len(recommendations)}")
```

## Documentation and Resources
- **Official GitHub**: https://github.com/danielnsilva/semanticscholar
- **API Documentation**: https://www.semanticscholar.org/product/api
- **PyPI**: https://pypi.org/project/semanticscholar/
- **ReadTheDocs**: https://semanticscholar.readthedocs.io/
