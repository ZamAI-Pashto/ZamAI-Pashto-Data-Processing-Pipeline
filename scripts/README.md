# Pashto Text Dataset Tools

This directory contains scripts for gathering, cleaning, and processing Pashto text data for language model fine-tuning.

## Key Files

### Data Gathering and Processing

- `gather_pashto_data.py` - Script for gathering Pashto text from various online sources
- `gather_clean_combine.sh` - Complete workflow script that gathers, cleans, and combines data
- `pashto_sources.json` - Configuration file with sources for data gathering
- `create_stopwords.py` - Script to create a Pashto stopwords list
- `Comprehensive_Data_Cleaning.ipynb` - Jupyter notebook for cleaning and normalizing the dataset
- `run_data_cleaning.sh` - Script to run the cleaning notebook on existing CSV files

### PDF Text Extraction

- `extract_pashto_from_pdf.py` - Script for extracting Pashto text from PDF documents
- `extract_pdf_text.sh` - Helper script to extract text from PDFs with optional OCR support

### Generated Files (Created during execution)

- `clean_gathered_data.py` - Generated script to clean newly gathered data
- `combine_data.py` - Generated script to combine existing data with newly gathered data
- `run_cleaning.py` - Generated from the notebook for direct execution

## How to Use

### Option 1: Complete Automated Workflow

To gather new data from the internet, clean it, and combine with existing data:

```bash
./gather_clean_combine.sh
```

This script:
1. Creates a stopwords file if needed
2. Installs required dependencies
3. Gathers fresh text data from Pashto websites
4. Cleans and normalizes the gathered data
5. Combines the new data with existing cleaned data

### Option 2: Extract Text from PDF Documents

To extract text from PDF documents containing Pashto text:

```bash
# Basic extraction
./extract_pdf_text.sh

# With OCR support for scanned PDFs
./extract_pdf_text.sh --with-ocr

# Extract and combine with existing dataset
./extract_pdf_text.sh --with-ocr --combine
```

Place your PDF files in the `/workspaces/pashto-text-dataset/pdf_documents` directory before running the script.

### Option 3: Manual Steps

#### Gather Data Only

To only gather new data from the internet:

```bash
python gather_pashto_data.py --max-articles 50 --delay 1.5
```

Options:
- `--max-articles`: Maximum articles to gather per source (default: 50)
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--output-dir`: Directory to save gathered data
- `--sources-file`: JSON file with custom sources (default: built-in sources)

#### Extract PDF Text Manually

```bash
python extract_pashto_from_pdf.py --input-dir /path/to/pdfs --output-dir /path/for/output
```

Options:
- `--input-dir`: Directory containing PDF files
- `--output-dir`: Directory to save extracted text
- `--use-ocr`: Use OCR for scanned PDFs (requires tesseract)
- `--ocr-lang`: Tesseract language(s) for OCR (default: eng+ara)
- `--min-length`: Minimum length for extracted text sections
- `--no-sections`: Do not attempt to extract sections from text
- `--install-deps`: Install dependencies before running

#### Clean Existing Files

To clean the existing CSV files:

```bash
./run_data_cleaning.sh
```

## Output Files

- Gathered data: `/workspaces/pashto-text-dataset/gathered_data/`
- Extracted PDF data: `/workspaces/pashto-text-dataset/extracted_pdf_data/`
- Cleaned data: `/workspaces/pashto-text-dataset/cleaned_data/`
- Combined data: `/workspaces/pashto-text-dataset/combined_data/`

The final dataset for model fine-tuning will be available at:
`/workspaces/pashto-text-dataset/combined_data/latest_combined_dataset.csv`
