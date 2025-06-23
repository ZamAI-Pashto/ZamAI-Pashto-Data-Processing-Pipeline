#!/bin/bash
# Script to make all scripts executable in the Pashto text dataset project
# Created on: June 23, 2025

# Set variables
WORKSPACE_DIR="/workspaces/pashto-text-dataset"
SCRIPT_DIR="$WORKSPACE_DIR/scripts"

echo "========================================="
echo "Making scripts executable in the Pashto Text Dataset project"
echo "========================================="

# Make all Python and Shell scripts in the scripts directory executable
echo "Making scripts in $SCRIPT_DIR executable..."
find "$SCRIPT_DIR" -name "*.py" -o -name "*.sh" | while read file; do
    if [ -f "$file" ]; then
        chmod +x "$file"
        echo "Made executable: $(basename "$file")"
    fi
done

# Check for any scripts in the main workspace directory
echo -e "\nChecking for scripts in root directory..."
find "$WORKSPACE_DIR" -maxdepth 1 \( -name "*.py" -o -name "*.sh" \) | while read file; do
    if [ -f "$file" ]; then
        chmod +x "$file"
        echo "Made executable: $(basename "$file")"
    fi
done

# Verify scripts are executable
echo -e "\nVerifying executable permissions:"
echo "-----------------------------------------"
find "$SCRIPT_DIR" -name "*.py" -o -name "*.sh" | while read file; do
    if [ -x "$file" ]; then
        echo "✓ $(basename "$file")"
    else
        echo "✗ $(basename "$file") (Failed to make executable)"
    fi
done

echo "========================================="
echo "Script execution completed!"
echo "All Python and Shell scripts should now be executable."
echo "========================================="

# Provide helpful information about running the scripts
echo -e "\nTo run the full data processing pipeline:"
echo "  cd $SCRIPT_DIR && ./gather_clean_combine.sh"
echo
echo "To extract text from PDF files:"
echo "  cd $SCRIPT_DIR && ./extract_pdf_text.sh"
echo
echo "To run data cleaning only:"
echo "  cd $SCRIPT_DIR && ./run_data_cleaning.sh"
echo "========================================="
