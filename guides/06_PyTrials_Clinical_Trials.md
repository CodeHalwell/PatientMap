# PyTrials - Clinical Research Agent Guide

## Overview
PyTrials is the **PRIMARY tool for clinical trials research** within the Clinical Researcher Agent to search and retrieve active clinical trials and research protocols.

The library provides access to the **ClinicalTrials.gov registry of 500,000+ clinical trials** with:
- Active, recruiting, and completed trial discovery
- Trial phase filtering (Phase 1-4 for evidence hierarchy)
- Eligibility criteria and inclusion/exclusion parameters
- Trial outcomes and primary endpoints
- Enrollment status and participant information
- Geographic and institutional search

For clinical research, PyTrials complements literature search with practical evidence from ongoing clinical research.

## Installation

### Using pip
```bash
pip install pytrials
```

### From Source
```bash
git clone https://github.com/your-repo/pytrials.git
cd pytrials
pip install .
```

## Clinical Use Cases

### 1. Active Trial Discovery
```python
# Find active clinical trials for a condition
from pytrials import ClinicalTrials

ct = ClinicalTrials()

# Search for recruiting trials
trials = ct.get_full_studies(
    search_expr="Type 2 Diabetes",
    status="RECRUITING"  # Only actively recruiting
)

print(f"Found {len(trials)} recruiting trials")
for trial in trials[:3]:
    print(f"NCT: {trial['NCTId']}")
    print(f"Title: {trial['StudyTitle']}")
    print(f"Status: {trial['OverallStatus']}")
```

### 2. Phase-Based Evidence Hierarchy
```python
# Find confirmatory trials (Phase 3/4)
confirmatory_trials = ct.get_full_studies(
    search_expr="metformin AND Type 2 Diabetes",
    phase="Phase 3|Phase 4"  # Advanced research
)

# Find early-stage trials (Phase 1/2)
exploratory_trials = ct.get_full_studies(
    search_expr="novel GLP-1 agonist",
    phase="Phase 1|Phase 2"  # Early research
)

print(f"Confirmatory trials: {len(confirmatory_trials)}")
print(f"Exploratory trials: {len(exploratory_trials)}")
```

### 3. Eligibility Criteria Analysis
```python
# Extract eligibility criteria
trial = ct.get_single_study("NCT04123456")
study = trial['ProtocolSection']

# Get study design
eligibility = study.get('EligibilityModule', {})
print(f"Study Type: {study['StudyType']}")
print(f"Phases: {study['DesignModule']['Phases']}")

# Inclusion/Exclusion criteria
criteria = eligibility.get('EligibilityCriteria', {})
print(f"Criteria: {criteria.get('EligibilityCriteria', 'Not specified')[:200]}")

# Enrollment
enrollment = eligibility.get('EnrollmentInfo', {})
print(f"Enrollment: {enrollment.get('EnrollmentCount', 'N/A')}")
```

### 4. Outcomes & Endpoints Research
```python
# Find trials with specific outcomes
trial = ct.get_single_study("NCT04123456")
study = trial['ProtocolSection']

# Primary outcomes
outcomes = study.get('OutcomesModule', {})
primary = outcomes.get('PrimaryOutcomes', [])
print("Primary Outcomes:")
for outcome in primary:
    print(f"  - {outcome.get('Measure', 'Unknown')}")

# Secondary outcomes
secondary = outcomes.get('SecondaryOutcomes', [])
print(f"Secondary Outcomes: {len(secondary)}")
```

### 5. Geographic & Institutional Search
```python
# Find trials in specific locations
trials = ct.get_full_studies(
    search_expr="Type 2 Diabetes",
    country="United States",
    status="RECRUITING"
)

# Extract trial sites
for trial in trials[:2]:
    locations = trial.get('LocationsModule', {})
    facilities = locations.get('LocationList', {}).get('Location', [])
    
    print(f"Trial: {trial['NCTId']}")
    for facility in facilities[:3]:
        print(f"  - {facility.get('FacilityName', 'Unknown')}")
```

### 6. Evidence Integration (Literature + Trials)
```python
# Combine clinical trials with literature findings
from semanticscholar import SemanticScholar
from pytrials import ClinicalTrials

sch = SemanticScholar()
ct = ClinicalTrials()

condition = "Type 2 Diabetes"

# Get literature evidence
papers = sch.search_paper(
    query=condition,
    year_start=2020,
    citation_limit=50,
    limit=10
)

# Get active trials
trials = ct.get_full_studies(
    search_expr=condition,
    status="RECRUITING"
)

evidence_summary = {
    'literature': len(papers),
    'active_trials': len(trials),
    'recent_papers': sum(1 for p in papers if p.year >= 2023)
}

print(f"Evidence Summary for {condition}:")
for key, value in evidence_summary.items():
    print(f"  {key}: {value}")
```

## Core Concepts

### Clinical Trials Data
PyTrials provides access to:
- **Trial Metadata**: NCT numbers, titles, recruitment status
- **Trial Status**: Ongoing, completed, suspended, terminated
- **Participant Information**: Enrollment numbers, inclusion/exclusion criteria
- **Study Design**: Phase, type, duration
- **Outcomes**: Primary, secondary, tertiary outcomes
- **Conditions**: Diseases and health conditions being studied
- **Interventions**: Drugs, devices, procedures being tested
- **Locations**: Trial sites and countries
- **Contacts**: Principal investigator and study contact information

## Initialization

### Basic Client Setup
```python
import pytrials

# Initialize client for ClinicalTrials.gov
client = pytrials.ClinicalTrials()

# Alternative: Initialize with specific registry
# client = pytrials.EudraCT()  # For European trials
```

## Searching Clinical Trials

### Search by Condition
```python
# Search trials for specific condition
results = client.search(condition='Diabetes Mellitus')

# Search with multiple conditions
results = client.search(condition=['Cancer', 'Lung Cancer'])

# Get trial count
print(f"Total trials found: {results['NStudiesReturned']}")
```

### Search by Intervention
```python
# Search trials by drug/intervention
results = client.search(intervention='Metformin')

# Search by intervention type
results = client.search(intervention_type='Drug')  # Drug, Device, Behavioral, Dietary Supplement, etc.

# Search for placebo-controlled trials
results = client.search(intervention=['Placebo', 'Control'])
```

### Search by Recruitment Status
```python
# Search actively recruiting trials
results = client.search(status='Recruiting')

# Search completed trials
results = client.search(status='Completed')

# Search by multiple statuses
results = client.search(status=['Recruiting', 'Enrolling by invitation'])

# All possible statuses:
# - Recruiting
# - Enrolling by invitation
# - Active, not recruiting
# - Suspended
# - Terminated
# - Completed
# - Withdrawn
# - Unknown status
```

### Search by Trial Phase
```python
# Search Phase 2 trials
results = client.search(phase='Phase 2')

# Search by multiple phases
results = client.search(phase=['Phase 1', 'Phase 2'])

# Available phases: Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, N/A
```

### Search by Sponsor
```python
# Search trials sponsored by specific organization
results = client.search(sponsor='National Institutes of Health')

# Search by lead sponsor
results = client.search(lead_sponsor='Pfizer')
```

### Search by Location
```python
# Search trials by country
results = client.search(country='United States')

# Search by state/province
results = client.search(state='California', country='United States')

# Search by city
results = client.search(city='San Francisco', state='California', country='United States')
```

### Search by Study Type
```python
# Search interventional studies
results = client.search(study_type='Interventional')

# Search observational studies
results = client.search(study_type='Observational')

# Available types: Interventional, Observational, Expanded Access, Patient Registry
```

### Search by Gender
```python
# Search gender-specific trials
results = client.search(gender='Female')  # Female, Male, or All

# Search age groups
results = client.search(age='Adult')  # Child, Adult, Older Adult, or All
```

## Advanced Searching

### Combining Search Criteria
```python
# Complex search
results = client.search(
    condition='Type 2 Diabetes',
    intervention='Insulin',
    status='Recruiting',
    phase='Phase 3',
    country='United States'
)

print(f"Found {results['NStudiesReturned']} matching trials")
```

### Keyword Search
```python
# General keyword search
results = client.search(
    keyword='immunotherapy',
    condition='Cancer'
)
```

### Search by NCT Number
```python
# Search by NCT (National Clinical Trial) number
results = client.get_full_studies(search_expr='NCT04293614', max_rnk=1)
```

## Extracting Trial Data

### Get Study Information
```python
# Get full study details
studies = client.get_full_studies(search_expr='Type 2 Diabetes', max_rnk=100)

# Extract information from studies
for study in studies['NStudiesReturned']:
    trial = study['ProtocolSection']
    
    nct_id = trial['IdentificationModule']['NCTId']
    title = trial['IdentificationModule']['OrgStudyIdInfo']['OrgStudyId']
    status = trial['StatusModule']['OverallStatus']
    
    print(f"NCT ID: {nct_id}")
    print(f"Title: {title}")
    print(f"Status: {status}")
```

### Extract Detailed Trial Information
```python
def extract_trial_info(trial_data):
    """Extract commonly used fields from trial data"""
    protocol = trial_data['ProtocolSection']
    
    return {
        'nct_id': protocol['IdentificationModule']['NCTId'],
        'title': protocol['IdentificationModule']['OrgStudyIdInfo']['OrgStudyId'],
        'official_title': protocol['IdentificationModule'].get('OfficialTitle', ''),
        'status': protocol['StatusModule']['OverallStatus'],
        'phase': protocol['DesignModule'].get('PhaseList', {}).get('Phase', []),
        'study_type': protocol['DesignModule'].get('StudyType', ''),
        'enrollment': protocol['DesignModule'].get('EnrollmentInfo', {}).get('EnrollmentValue', 0),
        'start_date': protocol['StatusModule'].get('StartDateStruct', {}).get('StartDate', ''),
        'completion_date': protocol['StatusModule'].get('PrimaryCompletionDateStruct', {}).get('CompletionDate', ''),
        'locations': [],
        'conditions': [],
        'interventions': [],
        'outcomes': []
    }

# Usage
studies = client.get_full_studies(search_expr='Diabetes', max_rnk=10)
trial_info = [extract_trial_info(study) for study in studies['NStudiesReturned']]
```

### Extract Conditions
```python
# Get list of conditions studied
result = client.search(condition='Cancer')

# Access detailed condition information
for study in result:
    conditions = study.get('Condition', [])
    print(f"Study conditions: {conditions}")
```

### Extract Interventions
```python
# Get list of interventions in trials
result = client.search(intervention='Chemotherapy')

# Access detailed intervention information
for study in result:
    interventions = study.get('Intervention', [])
    for intervention in interventions:
        print(f"Type: {intervention.get('InterventionType')}")
        print(f"Name: {intervention.get('InterventionName')}")
```

### Extract Outcomes
```python
# Get primary and secondary outcomes
studies = client.get_full_studies(search_expr='Hypertension', max_rnk=5)

for study in studies['NStudiesReturned']:
    outcomes = study['ProtocolSection'].get('OutcomesModule', {})
    
    primary_outcomes = outcomes.get('PrimaryOutcomeList', {}).get('PrimaryOutcome', [])
    secondary_outcomes = outcomes.get('SecondaryOutcomeList', {}).get('SecondaryOutcome', [])
    
    print("Primary Outcomes:")
    for outcome in primary_outcomes:
        print(f"  - {outcome.get('Measure')}")
    
    print("Secondary Outcomes:")
    for outcome in secondary_outcomes:
        print(f"  - {outcome.get('Measure')}")
```

### Extract Eligibility Criteria
```python
# Get inclusion/exclusion criteria
studies = client.get_full_studies(search_expr='COVID-19', max_rnk=1)

for study in studies['NStudiesReturned']:
    eligibility = study['ProtocolSection'].get('EligibilityModule', {})
    
    criteria = eligibility.get('EligibilityCriteria', '')
    min_age = eligibility.get('MinimumAge', 'Not specified')
    max_age = eligibility.get('MaximumAge', 'Not specified')
    gender = eligibility.get('Gender', 'All')
    accepts_healthy_volunteers = eligibility.get('HealthyVolunteers', 'Not specified')
    
    print(f"Age Range: {min_age} to {max_age}")
    print(f"Gender: {gender}")
    print(f"Criteria: {criteria}")
```

## Data Analysis

### Trial Statistics
```python
# Collect and analyze trial data
import pandas as pd

results = client.search(
    condition='Diabetes',
    country='United States'
)

# Convert to DataFrame
trials_data = []
for trial in results:
    trials_data.append({
        'nct_id': trial.get('NCTId'),
        'title': trial.get('OrgStudyId'),
        'status': trial.get('OverallStatus'),
        'phase': trial.get('Phase'),
        'enrollment': trial.get('Enrollment', 0)
    })

df = pd.DataFrame(trials_data)

# Analyze
print(f"Total trials: {len(df)}")
print(f"\nStatus distribution:")
print(df['status'].value_counts())
print(f"\nPhase distribution:")
print(df['phase'].value_counts())
print(f"\nAverage enrollment: {df['enrollment'].astype(int).mean():.0f}")
```

### Trial Timeline Analysis
```python
# Analyze trial timelines
import datetime

studies = client.get_full_studies(search_expr='Cancer', max_rnk=100)

for study in studies['NStudiesReturned']:
    protocol = study['ProtocolSection']
    start_date = protocol['StatusModule'].get('StartDateStruct', {}).get('StartDate', '')
    completion_date = protocol['StatusModule'].get('PrimaryCompletionDateStruct', {}).get('CompletionDate', '')
    
    if start_date and completion_date:
        print(f"Duration: {start_date} to {completion_date}")
```

## Error Handling

### Handling Empty Results
```python
# Check for empty results
results = client.search(condition='Rare Disease XYZ')

if not results or results.get('NStudiesReturned', 0) == 0:
    print("No trials found matching criteria")
else:
    print(f"Found {results['NStudiesReturned']} trials")
```

### Rate Limiting
```python
import time

# Implement delays to avoid rate limiting
queries = ['Diabetes', 'Cancer', 'Heart Disease']

for query in queries:
    results = client.search(condition=query)
    print(f"Found {results.get('NStudiesReturned', 0)} trials for {query}")
    time.sleep(1)  # 1 second delay between requests
```

## Best Practices

1. **Always validate data**: Check for missing fields before accessing
   ```python
   enrollment = trial.get('Enrollment', 0)
   ```

2. **Implement delays**: Respect API rate limits
   ```python
   time.sleep(0.5)
   ```

3. **Cache results**: Store data locally to avoid repeated API calls
   ```python
   import json
   with open('trials_cache.json', 'w') as f:
       json.dump(results, f)
   ```

4. **Use specific searches**: More specific queries return more relevant results

5. **Handle pagination**: Use max_rnk parameter for large result sets

## Example Workflows

### Workflow 1: Find Recruiting Trials by Condition
```python
import pytrials
import json

client = pytrials.ClinicalTrials()

# Search actively recruiting diabetes trials
results = client.search(
    condition='Type 2 Diabetes',
    status='Recruiting',
    country='United States'
)

# Display results
for trial in results[:5]:  # Show first 5
    print(f"NCT Number: {trial.get('NCTId')}")
    print(f"Title: {trial.get('OrgStudyId')}")
    print(f"Location: {trial.get('LocationCountries')}")
    print()
```

### Workflow 2: Analyze Trial Phases by Condition
```python
import pytrials
from collections import Counter

client = pytrials.ClinicalTrials()

# Search cancer trials
results = client.search(condition='Cancer')

# Count trials by phase
phases = [trial.get('Phase', 'N/A') for trial in results]
phase_counts = Counter(phases)

print("Cancer Trials by Phase:")
for phase, count in phase_counts.most_common():
    print(f"  {phase}: {count}")
```

### Workflow 3: Create Trial Database
```python
import pytrials
import pandas as pd
import json

client = pytrials.ClinicalTrials()

# Collect data on multiple conditions
conditions = ['Hypertension', 'Diabetes', 'Asthma']
all_trials = []

for condition in conditions:
    results = client.search(
        condition=condition,
        status='Recruiting'
    )
    all_trials.extend(results)

# Create DataFrame
df = pd.DataFrame(all_trials)

# Save to file
df.to_csv('clinical_trials.csv', index=False)

# Generate statistics
print(f"Total trials: {len(df)}")
print(f"Countries: {df['LocationCountries'].nunique()}")
print(f"Average enrollment: {df['Enrollment'].astype(int).mean():.0f}")
```

## Documentation and Resources
- **Official GitHub**: https://github.com/your-repo/pytrials
- **ClinicalTrials.gov**: https://clinicaltrials.gov
- **ClinicalTrials.gov API**: https://clinicaltrials.gov/api/gui
- **EudraCT Database**: https://www.clinicaltrialsregister.eu/
- **PyPI**: https://pypi.org/project/pytrials/
