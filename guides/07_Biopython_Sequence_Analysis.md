# Biopython Comprehensive Guide

## Overview
Biopython is a set of freely available tools for biological computation written in Python. It provides modules for biological sequence analysis, sequence alignment, phylogenetic analysis, and much more.

## Installation

### Using pip (Recommended)
```bash
pip install biopython
```

### Using Conda
```bash
conda install -c conda-forge biopython
conda update -c conda-forge biopython
```

### From Source
```bash
python setup.py build
python setup.py test
python setup.py install
```

### Platform-Specific Installation

**Ubuntu/Debian:**
```bash
sudo apt-get install python-biopython
sudo apt-get install python-biopython-doc
sudo apt-get install python-biopython-sql
```

**Fedora:**
```bash
yum install python-biopython
yum install python3-biopython
```

**Archlinux:**
```bash
pacman -S python2-biopython
pacman -S python-biopython
```

**Gentoo:**
```bash
emerge -va biopython
```

**FreeBSD:**
```bash
cd /usr/ports/biology/py-biopython
make install clean
```

### macOS
First install Xcode command line tools:
```bash
xcode-select --install
```

Then install Biopython:
```bash
pip install biopython
```

## Verification
Check if Biopython is correctly installed:
```python
import Bio
```

If no ImportError is raised, Biopython is installed correctly.

## Core Concepts

### Seq Objects
The `Bio.Seq` module provides the Seq class for sequence manipulation.

```python
from Bio.Seq import Seq

# Create a sequence object
my_seq = Seq("CATGTAGACTAG")

# Get details
print(f"seq {my_seq} is {len(my_seq)} bases long")
print(f"reverse complement is {my_seq.reverse_complement()}")
print(f"protein translation is {my_seq.translate()}")
```

### Sequence I/O

#### FASTA Format
Example FASTA file content:
```fasta
>gi|2765658|emb|Z78533.1|CIZ78533 C.irapeanum 5.8S rRNA gene and ITS1 and ITS2 DNA
CGTAACAAGGTTTCCGTAGGTGAACCTGCGGAAGGATCATTGATGAGACCGTGGAATAAACGATCGAGTG
GAATCCGGAGGACCGGTGTACTCAGCTCACCGGGGGCATTGCTCCCGTGGTGACCCTGATTTGTTGTTGGG
...
```

#### GenBank Format
Example GenBank header:
```
LOCUS       ATCOR66M      513 bp    mRNA            PLN       02-MAR-1992
DEFINITION  A.thaliana cor6.6 mRNA.
ACCESSION   X55053
VERSION     X55053.1  GI:16229
...
```

#### FASTQ Format
Example FASTQ file:
```fastq
@EAS54_6_R1_2_1_413_324
CCCTTCTTGTCTTCAGCGTTTCTCC
+
;;3;;;;;;;;;;;;7;;;;;;;88
```

### SeqIO Module
Use `Bio.SeqIO` for reading and writing sequence files:

```python
from Bio import SeqIO

# Read sequences
records = SeqIO.parse("sequences.fasta", "fasta")
for record in records:
    print(record.id)
    print(record.seq)

# Write sequences
SeqIO.write(records, "output.fasta", "fasta")

# Convert between formats
SeqIO.convert("input.gb", "genbank", "output.fasta", "fasta")

# Help on convert function
help(SeqIO.convert)
```

### Sequence Features and Annotations
Create SimpleLocation objects:

```python
from Bio.SeqFeature import SimpleLocation

# Forward strand
f = SimpleLocation(122, 150)
print(f.start)  # 122
print(f.end)    # 150
print(f.strand) # None

# Reverse strand
r = SimpleLocation(122, 150, strand=-1)
print(r.strand) # -1

# Get length
loc = SimpleLocation(5, 10)
print(len(loc))  # 5
```

## Advanced Topics

### BLAST Analysis
```python
from Bio import Blast

# Get help on qblast function
help(Blast.qblast)

# Parse BLAST results
with Blast.parse("my_blast.xml") as blast_records:
    print(blast_records)  # Print summary
```

### Multiple Sequence Alignment
```python
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment

a = SeqRecord(Seq("ACTGCTAGCTAG"), id="Alpha")
b = SeqRecord(Seq("ACT-CTAGCTAG"), id="Beta")
c = SeqRecord(Seq("ACTGCTAGATAG"), id="Gamma")

align = MultipleSeqAlignment([a, b, c])
print(len(align))             # 3 sequences
print(align.get_alignment_length())  # 12 positions

# Slice alignment
print(align[:, 9:])  # Get columns from position 9 onwards
```

### Phylogenetic Analysis
```python
from Bio.Phylo.PAML import codeml

cml = codeml.Codeml()
cml.alignment = "alignment.phylip"
cml.tree = "species.tree"
cml.out_file = "results.out"
cml.working_dir = "./scratch"
cml.set_options(seqtype=1, model=0, NSsites=[0, 1, 2])
results = cml.run()
```

### Sequence Alignment (EMBOSS)
```python
from Bio.Emboss.Applications import WaterCommandline

water_cmd = WaterCommandline(
    r"C:\Program Files\EMBOSS\water.exe",
    gapopen=10,
    gapextend=0.5,
    asequence="asis:ACCCGGGCGCGGT",
    bsequence="asis:ACCCGAGCGCGGT",
    outfile="temp_water.txt"
)
print(water_cmd)
```

### Pairwise Alignment
```python
from Bio import Align

aligner = Align.PairwiseAligner()
alignments = aligner.align("GAACT", "GAT")
alignment = alignments[0]

print(alignment)
print(alignment.aligned)  # Get aligned subsequences
```

### BioSQL Integration
```python
from BioSQL import BioSeqDatabase

server = BioSeqDatabase.open_database(
    driver="MySQLdb",
    user="gbrowse",
    passwd="biosql",
    host="localhost",
    db="test_biosql"
)

try:
    db = server["test"]
except KeyError:
    db = server.new_database("test", description="For testing")
```

### Command-Line Tools
Biopython provides wrappers for various command-line tools:

```python
# BWA MEM
from Bio.Sequencing.Applications import BwaMemCommandline
reference_genome = "/path/to/reference_genome.fasta"
read_file = "/path/to/read_1.fq"
output_sam_file = "/path/to/output.sam"
align_cmd = BwaMemCommandline(reference=reference_genome, read_file1=read_file)
print(align_cmd)

# Samtools
from Bio.Sequencing.Applications import SamtoolsMpileupCommandline
input_file = ["/path/to/sam_or_bam_file"]
samtools_mpileup_cmd = SamtoolsMpileupCommandline(input_file=input_file)
print(samtools_mpileup_cmd)
```

### DNA Motif Analysis
See `Bio.Motifs` for working with DNA motifs and transcription factor binding sites.

## Testing
Run Biopython tests:

```bash
python setup.py test
```

Or from the Tests directory:
```bash
cd Tests
python run_tests.py
```

## Deprecations and Best Practices
- The `Bio.Fasta` module was deprecated in Biopython 1.51 and removed in 1.55. Use `Bio.SeqIO` instead.
- Command-line tool execution was deprecated in Biopython 1.78. Use Python's `subprocess` module directly.
- `Bio.SeqIO.index_db()` requires Biopython 1.57+ with SQLite3 support.

## Documentation and Resources
- **Tutorial PDF:** Available for each Biopython version
- **API Documentation:** Comprehensive reference for all modules
- **GitHub:** https://github.com/biopython/biopython
- **Homepage:** https://biopython.org

## Support and Contributing
For issues, questions, or contributions, visit the Biopython GitHub repository or official website.
