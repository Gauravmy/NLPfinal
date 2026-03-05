# Resume Screening Project - Data Integration Guide

## Data Sources

Your project now integrates data from multiple sources:

### 1. **Archive Data (2,484 PDFs)**
- **Location**: `c:\Users\hp\Downloads\archive (19)\data\`
- **Format**: PDF files (numbered like 10554236.pdf, 10674770.pdf, etc.)
- **Count**: 2,484 resume PDFs

### 2. **Resume Dataset (CSV)**
- **Location**: `c:\Users\hp\Downloads\archive (19)\Resume\Resume.csv`
- **Size**: ~53 MB
- **Format**: CSV with columns:
  - `ID`: Resume identifier
  - `Resume_str`: Plain text resume content
  - `Resume_html`: HTML formatted resume
  - `Category`: Job category/domain

## Quick Start

### Option 1: Quick Integration (Recommended)

Run the data integration script to automatically organize CSV data by category:

```bash
cd c:\Users\hp\Desktop\NLPpro\resume_screening_project
python integrate_data.py
```

This will:
- Read the Resume.csv file
- Extract 2,484 resume texts
- Organize them by category in `data/resumes/`
- Generate summary statistics

### Option 2: Run Pipeline with Auto-Integration

Run the pipeline with automatic CSV integration:

```bash
cd c:\Users\hp\Desktop\NLPpro\resume_screening_project
python pipeline.py \
  --csv_path "c:\Users\hp\Downloads\archive (19)\Resume\Resume.csv" \
  --data_path ./data/resumes \
  --job_desc ./job_description.txt \
  --output ./pipeline_results
```

### Option 3: Manual Integration Using Python

```python
from src.data_integrator import quick_integrate_data

csv_path = r"c:\Users\hp\Downloads\archive (19)\Resume\Resume.csv"
output_dir = r"c:\Users\hp\Desktop\NLPpro\resume_screening_project\data\resumes"

# Integrate data
count, stats = quick_integrate_data(csv_path, output_dir)

print(f"Processed {count} resumes")
print(f"Categories: {stats['categories']}")
print(f"Category Distribution:")
for category, count in stats['category_distribution'].items():
    print(f"  - {category}: {count} resumes")
```

## Data Structure

After integration, your project structure will be:

```
resume_screening_project/
├── data/
│   └── resumes/
│       ├── ACCOUNTING/
│       │   ├── csv_100.txt
│       │   ├── csv_101.txt
│       │   └── ...
│       ├── ENGINEERING/
│       │   ├── csv_200.txt
│       │   ├── csv_201.txt
│       │   └── ...
│       ├── INFORMATION-TECHNOLOGY/
│       │   ├── csv_300.txt
│       │   ├── csv_301.txt
│       │   └── ...
│       └── ... (other categories)
├── src/
│   ├── data_integrator.py  (NEW)
│   ├── similarity_model.py
│   ├── ranking_engine.py
│   ├── skill_extractor.py
│   └── ...
├── integrate_data.py  (NEW)
├── pipeline.py
└── ...
```

## Data Statistics

Expected output after integration:

```
Total Resumes: ~2,484
Categories: ~24 different job categories
Average Resume Length: ~2,000-3,000 characters
Category Distribution: Balanced across categories
```

## Key Features

### Data Integrator Module

The `src/data_integrator.py` module provides:

```python
from src.data_integrator import DataIntegrator

integrator = DataIntegrator(
    csv_path="path/to/Resume.csv",
    local_pdf_dir="./data/resumes"
)

# Load and process CSV data
df = integrator.load_csv_data()

# Create structured DataFrame
df_structured = integrator.create_structured_dataframe()

# Save resumes as text files organized by category
count = integrator.organize_csv_resumes_by_category()

# Get summary statistics
stats = integrator.get_summary_statistics()

# Export combined data
integrator.export_combined_data("combined_resumes.csv")
```

### Supported Operations

1. **Load CSV Data**
   - Reads Resume.csv
   - Validates data integrity
   - Returns structured DataFrame

2. **Extract Resume Texts**
   - Extracts `Resume_str` content
   - Preserves category information
   - Handles encoding properly

3. **Organize by Category**
   - Creates category subdirectories
   - Saves resumes as text files
   - Matches expected pipeline structure

4. **Generate Statistics**
   - Count total resumes
   - Category distribution
   - Resume length analysis
   - Data quality metrics

5. **Export Data**
   - Save to structured CSV
   - Maintain metadata
   - Enable reproducibility

## Pipeline Integration

After data integration, the pipeline supports:

```bash
# Run with integrated CSV data
python pipeline.py --csv_path "..." --data_path ./data/resumes

# Run with existing data
python pipeline.py --data_path ./data/resumes

# Run with custom job description and categories
python pipeline.py \
  --data_path ./data/resumes \
  --job_desc ./job_description.txt \
  --relevant_categories ENGINEERING IT FINANCE \
  --output ./results
```

## Performance Notes

- **Data Loading**: ~30-60 seconds for 2,484 resumes
- **Text Preprocessing**: ~2-5 minutes
- **Skill Extraction**: ~5-10 minutes
- **BERT Encoding**: ~15-30 minutes (first run, then cached)
- **Model Comparison**: ~10-20 minutes
- **Total Pipeline**: ~45-90 minutes on first run

## Troubleshooting

### Issue: "CSV file not found"
```python
# Verify the path exists
import os
csv_path = r"c:\Users\hp\Downloads\archive (19)\Resume\Resume.csv"
print(os.path.exists(csv_path))  # Should print True
```

### Issue: "No resumes loaded"
```bash
# Check data directory structure
ls -R c:\Users\hp\Desktop\NLPpro\resume_screening_project\data\resumes\
```

### Issue: "Out of Memory"
- Process in batches using the integrator's `chunksize` parameter
- Preprocess text before loading full dataset

### Issue: "Encoding errors"
- All files saved with UTF-8 encoding
- If rebuilding, use `encoding='utf-8'` for text files

## Next Steps

1. **Run integration**: `python integrate_data.py`
2. **Create job description**: Add `job_description.txt`
3. **Run pipeline**: `python pipeline.py`
4. **Check results**: View `pipeline_results/` directory

## File Organization

```
# After integration, you'll have:
data/resumes/
├── ACCOUNTING/           (e.g., 150 resumes)
├── ENGINEERING/          (e.g., 250 resumes)
├── INFORMATION-TECHNOLOGY/ (e.g., 300 resumes)
├── FINANCE/             (e.g., 200 resumes)
├── SALES/               (e.g., 180 resumes)
├── MARKETING/           (e.g., 150 resumes)
└── ... (remaining 19 categories with varying counts)

Total: 2,484 resumes organized in ~24 categories
```

## Questions or Issues?

Refer to the main [README.md](README.md) or check the logging output when running integration for detailed diagnostics.
