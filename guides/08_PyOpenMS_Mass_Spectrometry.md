# pyOpenMS Comprehensive Guide

## Overview
pyOpenMS is a comprehensive Python wrapper for the OpenMS C++ library, providing tools for mass spectrometry data analysis. It supports processing of proteomics and metabolomics data with advanced algorithms for feature detection, alignment, and identification.

## Installation

### Using pip
```bash
pip install pyopenms
```

### Using Conda
```bash
conda install -c conda-forge pyopenms
```

## Core Concepts and Data Structures

### Basic Data Types

#### AASequence
Represents a sequence of amino acids:
```python
from Bio.SeqFeature import AASequence

seq = AASequence()
# Create peptide sequences with mass information
```

#### Adduct
Stores information about chemical adducts in MS experiments:
```python
import pyopenms as oms

adduct = oms.Adduct()
# Configure adduct parameters for charge and formula
```

#### Acquisition
Represents MS acquisition parameters:
```python
acq = oms.Acquisition()
# Set acquisition settings like scan numbers, retention times
```

### MSExperiment
The primary container for mass spectrometry data:

```python
import pyopenms as oms

exp = oms.MSExperiment()

# Get number of spectra
num_spectra = exp.getNrSpectra()

# Get 2D peak data within ranges
rt_array, mz_array, intensity_array = exp.get2DPeakData(
    min_rt=100.0,
    max_rt=2000.0,
    min_mz=400.0,
    max_mz=1600.0,
    ms_level=2
)

# With Ion Mobility data
rt_array, mz_array, intensity_array, ion_mobility = exp.get2DPeakDataIM(
    min_rt=100.0,
    max_rt=2000.0,
    min_mz=400.0,
    max_mz=1600.0,
    ms_level=2
)
```

### PeakSpectrum
Represents a single mass spectrometry spectrum:

```python
spectrum = oms.PeakSpectrum()

# Access data
has_im_data = spectrum.containsIMData()
mz_array = spectrum.get_mz_array()
intensity_array = spectrum.get_intensity_array()

# Data aggregation
tic = spectrum.calculateTIC()  # Total Ion Current

# Clear data
spectrum.clear(clear_meta_data=True)
spectrum.clearMetaInfo()
spectrum.clearRanges()
```

### FeatureMap
Container for detected features:

```python
feature_map = oms.FeatureMap()

# Data processing
data_processing_info = oms.DataProcessing()
feature_map.setDataProcessing(data_processing_info)
data_processing_list = feature_map.getDataProcessing()

# Identifiers
identifier = feature_map.getIdentifier()
feature_map.setUniqueId(new_id)
feature_map.ensureUniqueId()

# Clearing data
feature_map.clear()
feature_map.clearMetaInfo()
feature_map.clearRanges()
feature_map.clearUniqueId()
```

### FloatDataArray
Stores arrays of floating-point numbers:

```python
fd = pyopenms.FloatDataArray()

# Get data (unsafe but fast view)
data = fd.get_data()

# Set data
import numpy as np
data = np.array([1, 2, 3, 5, 6]).astype(np.float32)
fd.set_data(data)
```

### PeakFileOptions
Control data format and compression:

```python
options = pyopenms.PeakFileOptions()

# Set compression
options.setCompression("zlib")
compression = options.getCompression()

# Set precision
options.setIntensity32Bit(True)
options.setMz32Bit(False)

# Fill missing data
options.setFillData(True)
```

## Reading Raw MS Data

### Basic mzML File Loading
```python
import pyopenms as oms

exp = oms.MSExperiment()
oms.MzMLFile().load("test.mzML", exp)

# Access data
print(exp.getNrSpectra())
```

### OnDiscMSExperiment for Large Files
Read indexed mzML files without loading all data into memory:

```python
import pyopenms as oms

od_exp = oms.OnDiscMSExperiment()
od_exp.openFile("test.mzML")

# Get metadata (fast)
meta_data = od_exp.getMetaData()
meta_data.getNrChromatograms()
od_exp.getNrChromatograms()

# Access metadata properties (fast)
native_id = meta_data.getChromatogram(0).getNativeID()

# Load actual data only when needed (slow)
actual_data = od_exp.getChromatogram(0).get_peaks()[1]
```

### Caching mzML Data
Cache mzML files to disk for faster access:

```python
import pyopenms as oms

# Load and cache
exp = oms.MSExperiment()
oms.MzMLFile().load("test.mzML", exp)
oms.CachedmzML().store("myCache.mzML", exp)

# Load from cache
cfile = oms.CachedmzML()
oms.CachedmzML().load("myCache.mzML", cfile)

# Metadata access (fast)
meta_data = cfile.getMetaData()
meta_data.getNrChromatograms()

# Data access (may be slow)
chromatogram_data = cfile.getChromatogram(0).get_peaks()[1]
```

## Reading Other MS Data Formats

### ConsensusXML Format
Load/store quantitative data from multiple LC-MS/MS runs:

```python
import pyopenms as oms
from urllib.request import urlretrieve

# Load
consensus_features = oms.ConsensusMap()
oms.ConsensusXMLFile().load("test.consensusXML", consensus_features)

# Store
oms.ConsensusXMLFile().store("test.out.consensusXML", consensus_features)
```

## Quality Control

### Generate mzQC Report
Export quality control data to an mzQC file:

```python
import pyopenms as oms
from urllib.request import urlretrieve

# Load mzML
exp = oms.MSExperiment()
oms.MzMLFile().load("input.mzML", exp)

# Optional: Load features
feature_map = oms.FeatureMap()
oms.FeatureXMLFile().load("features.featureXML", feature_map)

# Optional: Load identifications
prot_ids = []
pep_ids = []
oms.IdXMLFile().load("ids.idXML", prot_ids, pep_ids)

# Create mzQC file
mzqc = oms.MzQCFile()
mzqc.store(
    "input.mzML",
    "result.mzQC",
    exp,
    contact_name="Your Name",
    contact_address="your.email@example.com",
    description="QC Report",
    label="run_label",
    feature_map=feature_map,
    prot_ids=prot_ids,
    pep_ids=pep_ids
)
```

## Feature Detection and Alignment

### MRMRTNormalizer
Normalize retention times in MRM data:

```python
normalizer = pyopenms.MRMRTNormalizer()
# Configure with reference data and normalization algorithm
# Corrects for retention time shifts across different runs
```

### FeatureGroupingAlgorithm
Group features across multiple samples:

```python
grouping = pyopenms.FeatureGroupingAlgorithm()
# Aligns features from different runs for quantitative analysis
```

### FeatureGroupingAlgorithmKD
K-D tree based feature grouping algorithm for efficient alignment.

## Quantification Methods

### AbsoluteQuantitation
Perform absolute quantification analysis:

```python
quant_method = pyopenms.AbsoluteQuantitationMethod()
# Define parameters for absolute quantification
```

### IsobaricQuantificationMethod
Handle isobaric tagging methods (TMT, iTRAQ):

```python
iso_quant = pyopenms.IsobaricQuantifierStatistics()
# Configure for isobaric quantification analysis
```

### IsotopeLabelingMDVs
Work with metabolic label data:

```python
mdv_data = pyopenms.IsotopeLabelingMDVs()
# Analyze mass distribution vectors for stable isotope labeling
```

## Advanced Analysis

### InternalCalibration
Perform internal mass calibration:

```python
calibration = pyopenms.InternalCalibration()
# Calibrate mass measurements using internal standards
```

### BilinearInterpolation
For data interpolation:

```python
interp = pyopenms.BilinearInterpolation()
data = interp.getData()
interp.setData(new_data)
```

### TransformationModelLinear
Linear transformation models for data normalization:

```python
model = pyopenms.TransformationModelLinear()
# Validate data points and weights
model.checkDatumRange(datum, min_val, max_val)
```

## Data Array Types

### IndexedMzMLHandler
Manage indexed mzML files:

```python
# Working with data arrays
float_array = pyopenms.FloatDataArray()
int_array = pyopenms.IntegerDataArray()
```

### FeatureMapping
Map features to experimental data:

```python
mapping = pyopenms.FeatureMapping()
# Maps features to MS2 scan indices
feature_to_ms2 = pyopenms.FeatureMapping_FeatureToMs2Indices()
```

## Performance Optimization

### Caching and Memory Management
- Use `OnDiscMSExperiment` for very large files to avoid loading all data
- Use `CachedmzML` to pre-process files for faster access
- Consider data precision settings with `PeakFileOptions`

### Data Consumers
Process MS data efficiently:

```python
# MSDataStoringConsumer - Store information during processing
# MSDataCachedConsumer - Cache frequently accessed data
# MSDataAggregatingConsumer - Combine data from multiple sources
```

## Best Practices

1. **Memory Management**: Use `OnDiscMSExperiment` for files larger than available RAM
2. **Data Precision**: Configure `PeakFileOptions` based on your data quality needs
3. **Batch Processing**: Use appropriate data consumers for batch processing workflows
4. **Error Handling**: Always validate loaded data structure integrity

## Example: Complete Analysis Workflow

```python
import pyopenms as oms
import numpy as np

# Load data
exp = oms.MSExperiment()
oms.MzMLFile().load("raw_data.mzML", exp)

# Extract 2D peak data
rt, mz, intensity = exp.get2DPeakData(
    min_rt=500.0, max_rt=2500.0,
    min_mz=200.0, max_mz=1400.0,
    ms_level=2
)

# Process data
print(f"Loaded {len(rt)} peaks")

# Feature detection would follow here
```

## Documentation and Resources
- **Official Documentation**: https://pyopenms.readthedocs.io
- **GitHub**: https://github.com/OpenMS/pyopenms
- **API Documentation**: Comprehensive API reference available online
