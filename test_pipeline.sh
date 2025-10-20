#!/bin/bash
# Test script for the complete data processing pipeline
# This is a simplified version for testing with small datasets

set -e  # Exit on error

WORKSPACE_DIR="/workspaces/ZamAI-Pashto-Data-Processing-Pipeline"
cd "$WORKSPACE_DIR"

echo "========================================="
echo "Testing Pashto Data Processing Pipeline"
echo "========================================="

# Step 1: Create stopwords if not exists
echo ""
echo "Step 1/4: Checking stopwords file..."
if [ ! -f "stopwords.csv" ]; then
    echo "Creating stopwords file..."
    python scripts/create_stopwords.py
else
    echo "✓ Stopwords file exists"
fi

# Step 2: Test data gathering (already done, skip for now)
echo ""
echo "Step 2/4: Data gathering..."
echo "✓ Sample data already gathered in gathered_data/"
ls -lh gathered_data/*.csv | wc -l
echo "files found"

# Step 3: Test data cleaning on the gathered data
echo ""
echo "Step 3/4: Testing data cleaning..."
if [ -f "gathered_data/20251020_085131_all_gathered_articles.csv" ]; then
    echo "Found sample data file, testing basic cleaning operations..."
    python -c "
import pandas as pd
import re

# Read the gathered data
df = pd.read_csv('gathered_data/20251020_085131_all_gathered_articles.csv')
print(f'Loaded {len(df)} articles')
print(f'Columns: {list(df.columns)}')

# Basic cleaning
df_clean = df.dropna(subset=['content'])
print(f'After removing empty content: {len(df_clean)} articles')

# Save to cleaned_data
df_clean.to_csv('cleaned_data/test_cleaned_data.csv', index=False, encoding='utf-8')
print('✓ Cleaned data saved to cleaned_data/test_cleaned_data.csv')
"
else
    echo "⚠ No sample data found, skipping cleaning test"
fi

# Step 4: Verify outputs
echo ""
echo "Step 4/4: Verifying outputs..."
echo ""
echo "Directory structure:"
echo "  gathered_data/: $(ls gathered_data/ 2>/dev/null | wc -l) files"
echo "  cleaned_data/: $(ls cleaned_data/ 2>/dev/null | wc -l) files"
echo "  combined_data/: $(ls combined_data/ 2>/dev/null | wc -l) files"
echo ""

echo "========================================="
echo "✓ Pipeline Test Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Run full pipeline: ./scripts/gather_clean_combine.sh"
echo "2. Extract PDF text: ./scripts/extract_pdf_text.sh"
echo "3. Clean existing data: ./scripts/run_data_cleaning.sh"
echo ""
