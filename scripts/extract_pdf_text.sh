#!/bin/bash
# Script to extract Pashto text from PDF files

# Set variables
WORKSPACE_DIR="/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets"
SCRIPT_DIR="$WORKSPACE_DIR/scripts"
PDF_DIR="$WORKSPACE_DIR/pdf_documents"
OUTPUT_DIR="$WORKSPACE_DIR/extracted_pdf_data"

# Create directories if they don't exist
mkdir -p "$PDF_DIR"
mkdir -p "$OUTPUT_DIR"

# Make script executable
chmod +x "$SCRIPT_DIR/extract_pashto_from_pdf.py"

# Check if there are any PDF files to process
PDF_COUNT=$(find "$PDF_DIR" -name "*.pdf" | wc -l)
if [ "$PDF_COUNT" -eq 0 ]; then
    echo "========================================="
    echo "No PDF files found in $PDF_DIR"
    echo "Please add PDF files to this directory first."
    echo "========================================="
    exit 1
fi

# Install required dependencies
echo "========================================="
echo "Installing required dependencies..."
echo "========================================="
pip install -q pdfplumber pandas tqdm pymupdf

# Check if OCR is requested
if [ "$1" = "--with-ocr" ]; then
    echo "OCR support requested. Installing additional dependencies..."
    pip install -q pytesseract pillow
    
    # Check if Tesseract OCR is installed
    if ! command -v tesseract &> /dev/null; then
        echo "Warning: Tesseract OCR not found. Trying to install..."
        # Try to install Tesseract OCR based on the platform
        if command -v apt-get &> /dev/null; then
            echo "Installing Tesseract OCR via apt-get..."
            sudo apt-get update
            sudo apt-get install -y tesseract-ocr
        elif command -v brew &> /dev/null; then
            echo "Installing Tesseract OCR via Homebrew..."
            brew install tesseract
        else
            echo "Could not automatically install Tesseract OCR."
            echo "Please install it manually and try again."
            echo "For more info: https://github.com/tesseract-ocr/tesseract"
            echo "Continuing without OCR..."
            USE_OCR=""
        fi
    fi
    
    USE_OCR="--use-ocr --ocr-lang eng+ara"
else
    USE_OCR=""
fi

# Run the extraction script
echo "========================================="
echo "Starting PDF text extraction..."
echo "========================================="
python "$SCRIPT_DIR/extract_pashto_from_pdf.py" --input-dir "$PDF_DIR" --output-dir "$OUTPUT_DIR" $USE_OCR

# Check if the extraction was successful
if [ $? -eq 0 ]; then
    echo "========================================="
    echo "PDF extraction completed successfully!"
    echo "Extracted data saved to: $OUTPUT_DIR"
    echo "========================================="
    
    # Check if we should combine with other data
    if [ "$2" = "--combine" ]; then
        echo "Combining extracted PDF data with other datasets..."
        LATEST_EXTRACTED="$OUTPUT_DIR/latest_extracted_pdf_text.csv"
        LATEST_COMBINED="$WORKSPACE_DIR/combined_data/latest_combined_dataset.csv"
        
        if [ -f "$LATEST_EXTRACTED" ] && [ -f "$LATEST_COMBINED" ]; then
            # Create a simple script to combine data
            COMBINE_SCRIPT="$SCRIPT_DIR/combine_pdf_data.py"
            cat > "$COMBINE_SCRIPT" << EOL
#!/usr/bin/env python3
import pandas as pd
import os
from datetime import datetime

# Load the datasets
extracted_df = pd.read_csv("$LATEST_EXTRACTED")
combined_df = pd.read_csv("$LATEST_COMBINED")

print(f"Extracted PDF data: {len(extracted_df)} records")
print(f"Existing combined data: {len(combined_df)} records")

# Align columns (use common columns)
common_columns = list(set(extracted_df.columns).intersection(set(combined_df.columns)))
if 'title' in common_columns and 'content' in common_columns:
    extracted_df = extracted_df[common_columns]
    
    # Combine and remove duplicates
    new_combined_df = pd.concat([combined_df, extracted_df], ignore_index=True)
    before_len = len(new_combined_df)
    new_combined_df = new_combined_df.drop_duplicates(subset=['content'], keep='first')
    
    print(f"Removed {before_len - len(new_combined_df)} duplicates")
    print(f"New combined dataset: {len(new_combined_df)} records")
    
    # Save the new combined dataset
    output_dir = "$WORKSPACE_DIR/combined_data"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/{timestamp}_combined_with_pdf.csv"
    
    new_combined_df.to_csv(output_file, index=False)
    print(f"Saved new combined dataset to {output_file}")
    
    # Update the latest link
    latest_link = "$WORKSPACE_DIR/combined_data/latest_combined_dataset.csv"
    if os.path.exists(latest_link):
        os.remove(latest_link)
    os.symlink(os.path.basename(output_file), latest_link)
else:
    print("Error: Required columns not found in both datasets")
EOL
            
            # Make the script executable
            chmod +x "$COMBINE_SCRIPT"
            
            # Run the combining script
            echo "----------------------------------------"
            python "$COMBINE_SCRIPT"
            echo "----------------------------------------"
        else
            echo "Required files not found for combining data"
        fi
    fi
else
    echo "========================================="
    echo "Error during PDF extraction process"
    echo "Check the log file for more information"
    echo "========================================="
fi

echo "Done!"
