# Quick Start Guide - WellInformed Libraries

## 📦 One-Line Installation

```bash
pip install biopython pyopenms semanticscholar habanero pytrials
```

---

## 🚀 5-Minute Quick Start

### 1. Biopython - Load and Analyze Sequences
```python
from Bio import SeqIO
from Bio.Seq import Seq

# Load FASTA file
records = SeqIO.parse("sequences.fasta", "fasta")

# Access sequence
for record in records:
    seq = record.seq
    print(f"Reverse complement: {seq.reverse_complement()}")
    print(f"Protein translation: {seq.translate()}")
```

### 2. pyOpenMS - Analyze Mass Spectrometry Data
```python
import pyopenms as oms

# Load mzML file
exp = oms.MSExperiment()
oms.MzMLFile().load("data.mzML", exp)

# Get 2D peak data
rt, mz, intensity = exp.get2DPeakData(100, 2000, 200, 1400, 2)
print(f"Loaded {len(rt)} peaks")
```

### 3. Semantic Scholar - Search Academic Papers
```python
from semanticscholar import SemanticScholar

# Initialize client
sch = SemanticScholar(api_key='your_key')

# Search papers
results = sch.search_paper('machine learning', limit=5)

# Access results
for item in results.items:
    print(f"{item.title} by {item.authors}")
```

### 4. Habanero - Get DOI Metadata
```python
import habanero

# Initialize CrossRef client
cr = habanero.Crossref(mailto="your_email@example.com")

# Get paper by DOI
result = cr.works(ids="10.1371/journal.pone.0033693")
print(f"Title: {result['message']['title']}")
```

### 5. PyTrials - Search Clinical Trials
```python
import pytrials

# Initialize client
client = pytrials.ClinicalTrials()

# Search recruiting trials
results = client.search(
    condition='Diabetes',
    status='Recruiting',
    country='United States'
)

for trial in results[:3]:
    print(f"NCT ID: {trial.get('NCTId')}")
```

---

## 📋 Library Cheat Sheet

### Biopython
```python
# Import
from Bio import SeqIO, Blast, Phylo
from Bio.Seq import Seq

# Read sequences
for record in SeqIO.parse("file.fasta", "fasta"):
    print(record.seq)

# Convert format
SeqIO.convert("input.gb", "genbank", "output.fasta", "fasta")
```

### pyOpenMS
```python
# Import
import pyopenms as oms

# Load data
exp = oms.MSExperiment()
oms.MzMLFile().load("file.mzML", exp)

# Get data
spectra = exp.getNrSpectra()
```

### Semantic Scholar
```python
# Import
from semanticscholar import SemanticScholar

# Initialize
sch = SemanticScholar(api_key='key', timeout=5)

# Search and get
results = sch.search_paper('query', limit=10)
paper = sch.get_paper('DOI')
```

### Habanero
```python
# Import
import habanero

# Initialize
cr = habanero.Crossref(mailto="email@example.com")

# Search and get
works = cr.works(query="biology")
paper = cr.works(ids="10.1234/example")
```

### PyTrials
```python
# Import
import pytrials

# Initialize
client = pytrials.ClinicalTrials()

# Search
results = client.search(condition='disease', status='Recruiting')
```

---

## 🔗 Integration Examples

### Example 1: Find Papers and Related Trials
```python
from semanticscholar import SemanticScholar
import pytrials

sch = SemanticScholar()
client = pytrials.ClinicalTrials()

# Find papers
papers = sch.search_paper('cancer immunotherapy', limit=5)

# For each paper, find related trials
for paper in papers.items:
    # Extract keywords
    keywords = paper.title
    
    # Search trials
    trials = client.search(condition=keywords)
    print(f"Found {len(trials)} trials related to {paper.title}")
```

### Example 2: Collect and Analyze Citation Data
```python
import habanero
from collections import Counter

cr = habanero.Crossref(mailto="user@example.com")

# Search papers
results = cr.works(query="machine learning", limit=100)

# Collect publication years
years = [item['published-online']['date-parts'][0][0] 
         for item in results['message']['items'] 
         if 'published-online' in item]

# Analyze
year_counts = Counter(years)
print("Papers by year:", dict(year_counts.most_common(5)))
```

### Example 3: Analyze Sequence Data from Papers
```python
from Bio import SeqIO, Seq

# Simulate data from paper
fasta_content = """>seq1
ATGCGATCGATCGAT
>seq2
ATGCGATCGATCGAT"""

# Write to file
with open("temp.fasta", "w") as f:
    f.write(fasta_content)

# Analyze sequences
for record in SeqIO.parse("temp.fasta", "fasta"):
    print(f"Sequence {record.id}: {len(record.seq)} bp")
    print(f"GC%: {(record.seq.count('G') + record.seq.count('C')) / len(record.seq) * 100:.1f}%")
```

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'Bio'"
```bash
# Solution:
pip install biopython
```

### Issue: Rate limiting in Semantic Scholar
```python
# Solution: Use API key and add delays
from semanticscholar import SemanticScholar
import time

sch = SemanticScholar(api_key='your_key')
# Add delay between requests
time.sleep(0.5)
```

### Issue: Empty results from PyTrials
```python
# Solution: Try simpler search terms
results = client.search(condition='Diabetes')  # Instead of long phrase
```

### Issue: pyOpenMS not loading large files
```python
# Solution: Use OnDiscMSExperiment for large files
import pyopenms as oms

od_exp = oms.OnDiscMSExperiment()
od_exp.openFile("large_file.mzML")
```

---

## 📚 Full Documentation

For complete guides with advanced features, see:

1. **Biopython**: `guides/01_biopython_guide.md`
2. **pyOpenMS**: `guides/02_pyopenms_guide.md`
3. **Semantic Scholar**: `guides/03_semanticscholar_guide.md`
4. **Habanero**: `guides/04_habanero_guide.md`
5. **PyTrials**: `guides/05_pytrials_guide.md`
6. **Master Index**: `guides/README.md`

---

## 💡 Tips for Success

1. **Always validate data**: Check for None/empty before accessing
2. **Implement error handling**: Wrap API calls in try-except
3. **Use rate limiting**: Add delays between API requests
4. **Cache results**: Save downloaded data locally
5. **Test locally first**: Verify code works before deployment
6. **Read the docs**: Full guides have detailed examples

---

## 🎯 Next Steps

1. Install the libraries: `pip install -r requirements.txt`
2. Read the relevant guide for your use case
3. Try the quick start examples
4. Refer to full documentation for advanced features
5. Integrate into your project

---

**Happy coding!** 🚀
