#!/bin/bash
# Script to gather, clean, and normalize Pashto text data

# Set variables
WORKSPACE_DIR="/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets"
SCRIPT_DIR="$WORKSPACE_DIR/scripts"
GATHERED_DIR="$WORKSPACE_DIR/gathered_data"
CLEANED_DIR="$WORKSPACE_DIR/cleaned_data"
COMBINED_DIR="$WORKSPACE_DIR/combined_data"
MAX_ARTICLES=50
DELAY=1.5

# Create directories if they don't exist
mkdir -p "$GATHERED_DIR"
mkdir -p "$CLEANED_DIR"
mkdir -p "$COMBINED_DIR"

# Make sure scripts are executable
chmod +x "$SCRIPT_DIR/gather_pashto_data.py"
chmod +x "$SCRIPT_DIR/create_stopwords.py"

# Step 1: Create stopwords file if it doesn't exist
echo "========================================="
echo "Creating stopwords file..."
echo "========================================="
python "$SCRIPT_DIR/create_stopwords.py"

# Step 2: Install required dependencies
echo "========================================="
echo "Installing required dependencies..."
echo "========================================="
pip install -q requests beautifulsoup4 pandas numpy tqdm scikit-learn matplotlib jupyter

# Step 3: Gather fresh data from the internet
echo "========================================="
echo "Gathering fresh Pashto text data from the internet..."
echo "========================================="
python "$SCRIPT_DIR/gather_pashto_data.py" --max-articles $MAX_ARTICLES --delay $DELAY --output-dir "$GATHERED_DIR"

# Step 4: Clean and normalize the gathered data
echo "========================================="
echo "Cleaning and normalizing the gathered data..."
echo "========================================="
# First convert the notebook to a Python script that can be executed directly
jupyter nbconvert --to python "$SCRIPT_DIR/Comprehensive_Data_Cleaning.ipynb" --output "$SCRIPT_DIR/run_cleaning.py"

# Modify the script to process the gathered data
cat > "$SCRIPT_DIR/clean_gathered_data.py" << EOL
#!/usr/bin/env python3
"""
Script to clean the gathered Pashto text data
"""
import pandas as pd
import glob
import os
import sys
from datetime import datetime

# Add necessary imports and functions from the converted notebook
sys.path.append("$SCRIPT_DIR")
from run_cleaning import normalize_pashto_text, preprocessing

# Find the most recent gathered data file
gathered_files = glob.glob("$GATHERED_DIR/*_all_gathered_articles.csv")
if not gathered_files:
    print("No gathered data files found!")
    sys.exit(1)

# Sort by modification time (most recent first)
gathered_files.sort(key=os.path.getmtime, reverse=True)
latest_file = gathered_files[0]
print(f"Processing latest gathered data: {latest_file}")

# Load the data
df = pd.read_csv(latest_file, encoding='utf-8')
print(f"Loaded {len(df)} articles")

# Apply cleaning and normalization
print("Cleaning and normalizing...")
df['cleaned_title'] = df['title'].apply(normalize_pashto_text)
df['cleaned_content'] = df['content'].apply(normalize_pashto_text)

# Remove entries with empty content after cleaning
before_len = len(df)
df = df[df['cleaned_content'].str.strip() != ""]
print(f"Removed {before_len - len(df)} entries with empty content")

# Remove duplicates
before_len = len(df)
df = df.drop_duplicates(subset=['cleaned_content'], keep='first')
print(f"Removed {before_len - len(df)} duplicate entries")

# Save the cleaned data
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"$CLEANED_DIR/{timestamp}_cleaned_gathered_data.csv"
df.to_csv(output_file, index=False, encoding='utf-8')
print(f"Saved cleaned data to {output_file}")

# Also save in JSONL format for model fine-tuning
jsonl_file = f"$CLEANED_DIR/{timestamp}_cleaned_gathered_data.jsonl"
with open(jsonl_file, 'w', encoding='utf-8') as f:
    for _, row in df.iterrows():
        f.write('{"prompt": "' + row['cleaned_title'].replace('"', '\\"') + '", "completion": "' + row['cleaned_content'].replace('"', '\\"') + '"}\n')
print(f"Saved JSONL format for model fine-tuning to {jsonl_file}")
EOL

# Make the script executable
chmod +x "$SCRIPT_DIR/clean_gathered_data.py"

# Run the cleaning script
python "$SCRIPT_DIR/clean_gathered_data.py"

# Step 5: Combine with existing cleaned data
echo "========================================="
echo "Combining with existing cleaned data..."
echo "========================================="

# Check if we have existing cleaned data to combine with
EXISTING_CLEANED=$(ls "$CLEANED_DIR/pashto_cleaned_full_dataset.csv" 2>/dev/null)
NEWLY_CLEANED=$(ls -t "$CLEANED_DIR"/*_cleaned_gathered_data.csv 2>/dev/null | head -1)

cat > "$SCRIPT_DIR/combine_data.py" << EOL
#!/usr/bin/env python3
"""
Script to combine existing cleaned data with newly gathered and cleaned data
"""
import pandas as pd
import os
from datetime import datetime

# Check if files exist
existing_file = "$EXISTING_CLEANED"
new_file = "$NEWLY_CLEANED"

combined_df = None

if os.path.exists(existing_file) and os.path.exists(new_file):
    print(f"Combining existing data {existing_file} with new data {new_file}")
    existing_df = pd.read_csv(existing_file, encoding='utf-8')
    new_df = pd.read_csv(new_file, encoding='utf-8')
    
    # Align columns if needed
    existing_columns = set(existing_df.columns)
    new_columns = set(new_df.columns)
    
    # For simplicity, we'll use only common columns
    common_columns = list(existing_columns.intersection(new_columns))
    if 'title' in common_columns and 'content' in common_columns:
        print(f"Using common columns: {common_columns}")
        existing_df = existing_df[common_columns]
        new_df = new_df[common_columns]
        
        # Combine and remove any duplicates
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        before_len = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['content'], keep='first')
        print(f"Removed {before_len - len(combined_df)} duplicates from combined dataset")
    else:
        print("Warning: Required columns 'title' and 'content' not found in both datasets")
        combined_df = new_df  # Just use the new data
elif os.path.exists(new_file):
    print(f"No existing cleaned data found. Using only new data {new_file}")
    combined_df = pd.read_csv(new_file, encoding='utf-8')
else:
    print("No data files found to combine!")
    exit(1)

# Save the combined dataset
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"$COMBINED_DIR/{timestamp}_combined_pashto_dataset.csv"
combined_df.to_csv(output_file, index=False, encoding='utf-8')
print(f"Saved combined dataset ({len(combined_df)} entries) to {output_file}")

# Create a symbolic link or copy to a standard name for easy access
standard_file = "$COMBINED_DIR/latest_combined_dataset.csv"
if os.path.exists(standard_file):
    os.remove(standard_file)
os.symlink(output_file, standard_file)
print(f"Created symbolic link to latest dataset at {standard_file}")
EOL

# Make the script executable
chmod +x "$SCRIPT_DIR/combine_data.py"

# Run the combining script
python "$SCRIPT_DIR/combine_data.py"

echo "========================================="
echo "Data gathering and processing workflow completed!"
echo "========================================="
echo "Summary:"
echo "1. Gathered new data from internet sources"
echo "2. Cleaned and normalized the gathered data"
echo "3. Combined with existing data"
echo ""
echo "You can find the final dataset at: $COMBINED_DIR/latest_combined_dataset.csv"
echo "This dataset is ready for your model fine-tuning!"
