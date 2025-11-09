# Habanero - Clinical Research Agent Guide

## Overview
Habanero is the **PRIMARY enrichment tool** for the Clinical Researcher Agent to retrieve DOI metadata and bibliographic information.

The library provides access to **CrossRef's database of 150+ million scholarly publications** with:
- Complete citation metadata (authors, journal, publication date)
- DOI-based paper lookup and enrichment
- Journal information and impact metrics
- Funding and acknowledgment tracking
- Publication history and availability

For clinical research, Habanero enriches papers found via Semantic Scholar with complete bibliographic information.

## Installation

### Using pip
```bash
pip install habanero
```

### From Source
```bash
git clone https://github.com/sckott/habanero.git
cd habanero
pip install .
```

## Clinical Use Cases

### 1. DOI Metadata Enrichment
```python
# After finding papers with Semantic Scholar, enrich with Habanero
from habanero import Crossref
from semanticscholar import SemanticScholar

sch = SemanticScholar()
cr = Crossref()

# Find papers on diabetes
papers = sch.search_paper("Type 2 Diabetes management", limit=5)

# Enrich each paper with DOI metadata
for paper in papers:
    try:
        doi_result = cr.works(doi=paper.doi)
        msg = doi_result['message']
        
        print(f"Title: {msg['title']}")
        print(f"Journal: {', '.join(msg.get('container-title', ['Unknown']))}")
        print(f"Authors: {len(msg.get('author', []))} authors")
        print(f"Published: {msg.get('published-online', {}).get('date-time', 'N/A')}")
        print(f"Citations: {msg.get('is-referenced-by-count', 'N/A')}")
    except:
        continue
```

### 2. Citation Metrics & Impact
```python
# Get citation count and impact metrics
result = cr.works(doi="10.1016/S0140-6736(23)01234-5")
msg = result['message']

citation_count = msg.get('is-referenced-by-count', 0)
published_date = msg.get('published', {}).get('date-parts', [[]])[0]
print(f"Citations: {citation_count}")
print(f"Published: {published_date}")
```

### 3. Funding & Author Information
```python
# Extract funding sources and author details
result = cr.works(doi="10.1371/journal.pmed.1003904")
msg = result['message']

# Funding information
funders = msg.get('funder', [])
print("Funding sources:")
for funder in funders:
    print(f"  - {funder.get('name', 'Unknown')}")

# Author information
authors = msg.get('author', [])
print(f"Authors ({len(authors)}):")
for author in authors[:3]:
    name = f"{author.get('given', '')} {author.get('family', '')}"
    print(f"  - {name}")
```

### 4. Journal & Publication Information
```python
# Get journal metrics and publication details
result = cr.works(doi="10.1001/jama.2023.1234")
msg = result['message']

journal_info = {
    'name': ', '.join(msg.get('container-title', ['Unknown'])),
    'issn': msg.get('issn-type', []),
    'issue': msg.get('issue', 'N/A'),
    'volume': msg.get('volume', 'N/A'),
    'pages': msg.get('page', 'N/A'),
    'license': msg.get('license', [{}])[0].get('URL', 'N/A')
}

for key, value in journal_info.items():
    print(f"{key}: {value}")
```

## Core Concepts

### CrossRef API Access
Habanero acts as a bridge between Python and the CrossRef API, allowing you to:
- Search for articles and publications
- Retrieve metadata by DOI (Digital Object Identifier)
- Query journals and authors
- Access citation data
- Get funding information

### CrossRef Data Model
CrossRef maintains a comprehensive database of scholarly works with the following key data:
- **DOI**: Digital Object Identifier (unique identifier)
- **Bibliographic Metadata**: Title, authors, publication date
- **Citation Information**: References, citations counts
- **Funding Information**: Grant agencies and award numbers
- **License Information**: Open access status

## Basic Usage

### Initialization
```python
import habanero

# Create a Crossref client
cr = habanero.Crossref()

# Optionally set email (recommended for API use)
cr = habanero.Crossref(mailto="your_email@example.com")
```

## Searching by DOI

### Get Single Article by DOI
```python
# Search by DOI
result = cr.works(ids="10.1371/journal.pone.0033693")

# Result contains full metadata
print(result['message']['title'])
print(result['message']['author'])
print(result['message']['published-online'])
```

### Search Multiple DOIs
```python
# Search multiple DOIs at once
ids = [
    "10.1371/journal.pone.0033693",
    "10.1038/nature12373"
]
results = cr.works(ids=ids)
```

## General Searching

### Search Works/Articles
```python
# Basic search
result = cr.works(query="ecology")

# Search with pagination
result = cr.works(query="climate change", limit=50, offset=0)

# Search within date range
result = cr.works(query="biodiversity", from_pub_date="2015-01-01", until_pub_date="2020-12-31")

# Filter by publication type
result = cr.works(query="machine learning", type="journal-article")

# Filter by license
result = cr.works(query="open science", license="CC-BY")

# Sort results
result = cr.works(query="genetics", sort="published", order="desc")
```

### Access Search Results
```python
# Get metadata from search results
items = result['message']['items']

for item in items:
    doi = item.get('DOI')
    title = item.get('title', [''])[0]
    authors = item.get('author', [])
    publication_date = item.get('published-online')
    
    print(f"DOI: {doi}")
    print(f"Title: {title}")
    print(f"Authors: {[f['given'} {f['family']}" for f in authors]}")
    print(f"Published: {publication_date}")
```

## Searching by Author

### Search by Author
```python
# Search articles by author name
result = cr.works(query="Albert Einstein")

# Get author information
for item in result['message']['items']:
    authors = item.get('author', [])
    for author in authors:
        if 'Einstein' in author.get('family', ''):
            print(f"{author['given']} {author['family']}")
```

## Searching Journals

### Get Journal Information
```python
# Search journals by ISSN (International Standard Serial Number)
result = cr.journals(ids="2047-8689")

# Search journals by name
result = cr.journals(query="Nature")

# Get journal metadata
journal = result['message']
print(journal['title'])
print(journal['ISSN'])
print(journal['publisher'])
```

## Searching Funders

### Get Funder Information
```python
# Search funders
result = cr.funders(query="National Science Foundation")

# Get funder metadata
for funder in result['message']['items']:
    print(funder['name'])
    print(funder['id'])
```

## Advanced Querying

### Field Queries
```python
# Search specific fields
# Using the query syntax supported by CrossRef

# Author field
result = cr.works(query="author:Albert Einstein")

# Title field
result = cr.works(query="title:quantum mechanics")

# Combined searches
result = cr.works(query="author:Einstein AND title:relativity")

# Boolean operators
result = cr.works(query="climate OR weather")
result = cr.works(query="NOT politics")
```

### Filtering Options
```python
# Filter by work type
result = cr.works(filter={
    "type": "journal-article",
    "has-abstract": True,
    "has-full-text": True
})

# Filter by publication status
result = cr.works(filter={"is-published": True})

# Filter by license
result = cr.works(filter={"license": "CC-BY"})

# Filter by open access
result = cr.works(filter={"is-oa": True})

# Combine multiple filters
result = cr.works(
    query="machine learning",
    filter={
        "type": "journal-article",
        "has-abstract": True,
        "from-pub-date": "2015-01-01",
        "until-pub-date": "2020-12-31"
    }
)
```

### Sorting and Pagination
```python
# Sort by relevance (default)
result = cr.works(query="biology", sort="relevance")

# Sort by publication date
result = cr.works(query="biology", sort="published", order="desc")

# Sort by update date
result = cr.works(query="biology", sort="updated", order="asc")

# Pagination - get first 100 results
result = cr.works(query="biology", limit=100)

# Get next 100 results (offset)
result = cr.works(query="biology", limit=100, offset=100)
```

## Data Extraction

### Common Data Fields
```python
def extract_article_info(item):
    """Extract commonly used fields from a CrossRef work"""
    return {
        'doi': item.get('DOI'),
        'title': item.get('title', [None])[0],
        'authors': [f"{a['given']} {a['family']}" for a in item.get('author', [])],
        'published_date': item.get('published-online') or item.get('published-print'),
        'journal': item.get('container-title', [None])[0],
        'volume': item.get('volume'),
        'issue': item.get('issue'),
        'pages': item.get('page'),
        'issn': item.get('ISSN'),
        'type': item.get('type'),
        'abstract': item.get('abstract'),
        'is_oa': item.get('is-oa'),
        'license': item.get('license', [{}])[0].get('URL'),
        'citations': item.get('is-referenced-by-count'),
    }

# Usage
result = cr.works(query="quantum computing", limit=10)
articles = [extract_article_info(item) for item in result['message']['items']]
```

### Handling Pagination
```python
def search_all_results(query, limit_per_page=100):
    """Fetch all results for a query with pagination"""
    all_results = []
    offset = 0
    
    while True:
        result = cr.works(
            query=query,
            limit=limit_per_page,
            offset=offset
        )
        
        items = result['message']['items']
        if not items:
            break
            
        all_results.extend(items)
        offset += limit_per_page
        
        # Optional: add delay to avoid rate limiting
        # import time
        # time.sleep(0.5)
    
    return all_results

# Usage
all_papers = search_all_results("climate change")
print(f"Found {len(all_papers)} papers")
```

## Error Handling

### Common Error Scenarios
```python
try:
    result = cr.works(ids="invalid-doi")
except Exception as e:
    print(f"Error fetching DOI: {e}")

try:
    result = cr.works(query="test", limit=10000)  # Limit exceeded
except Exception as e:
    print(f"Query error: {e}")
```

### Rate Limiting
```python
import time
import habanero

cr = habanero.Crossref()

# Implement delay between requests to avoid rate limiting
for query in ["machine learning", "deep learning", "AI"]:
    result = cr.works(query=query, limit=10)
    print(f"Found {len(result['message']['items'])} results for {query}")
    time.sleep(0.5)  # 500ms delay between requests
```

## Best Practices

1. **Email Address**: Always provide an email address to CrossRef
   ```python
   cr = habanero.Crossref(mailto="your_email@example.com")
   ```

2. **Rate Limiting**: Implement delays between requests
   ```python
   import time
   time.sleep(0.5)
   ```

3. **Result Validation**: Check for required fields before accessing
   ```python
   doi = item.get('DOI')
   if doi:
       # Process DOI
   ```

4. **Error Handling**: Always wrap API calls in try-except blocks

5. **Pagination**: Use offset and limit for large result sets

6. **Filtering**: Use CrossRef filters for more precise queries

## Example Workflows

### Workflow 1: Find Recent Papers by Author
```python
import habanero
import time

cr = habanero.Crossref(mailto="user@example.com")

# Search for recent papers
result = cr.works(
    query="author:Langmuir",
    from_pub_date="2020-01-01",
    sort="published",
    order="desc",
    limit=50
)

# Process results
for item in result['message']['items']:
    print(f"Title: {item['title'][0]}")
    print(f"DOI: {item['DOI']}")
    print(f"Date: {item.get('published-online')}")
    time.sleep(0.3)
```

### Workflow 2: Collect Citation Metadata
```python
# Search papers and collect metadata
result = cr.works(
    query="climate change",
    filter={"type": "journal-article", "has-abstract": True},
    limit=100
)

papers = []
for item in result['message']['items']:
    papers.append({
        'doi': item['DOI'],
        'title': item['title'][0],
        'journal': item.get('container-title', [''])[0],
        'year': item['published-online']['date-parts'][0][0],
        'citations': item.get('is-referenced-by-count', 0)
    })

# Analyze collected data
print(f"Total papers: {len(papers)}")
avg_citations = sum(p['citations'] for p in papers) / len(papers)
print(f"Average citations: {avg_citations}")
```

## Documentation and Resources
- **Official GitHub**: https://github.com/sckott/habanero
- **CrossRef API Docs**: https://github.com/CrossRef/rest-api-doc
- **PyPI**: https://pypi.org/project/habanero/
- **CrossRef Homepage**: https://www.crossref.org/
