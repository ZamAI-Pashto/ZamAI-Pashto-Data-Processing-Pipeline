#!/bin/bash
# ZamAI Pashto Dataset - Getting Started Script
# Created on: June 23, 2025

# Set variables
WORKSPACE_DIR="/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets"
SCRIPT_DIR="$WORKSPACE_DIR/scripts"

echo "========================================="
echo "ZamAI Pashto Text Dataset - Getting Started"
echo "========================================="

# Create necessary directories
mkdir -p "$WORKSPACE_DIR/pdf_documents"
mkdir -p "$WORKSPACE_DIR/gathered_data"
mkdir -p "$WORKSPACE_DIR/cleaned_data"
mkdir -p "$WORKSPACE_DIR/combined_data"
mkdir -p "$WORKSPACE_DIR/extracted_pdf_data"

# Make all scripts executable
if [ -f "$SCRIPT_DIR/make_scripts_executable.sh" ]; then
    echo "Making all scripts executable..."
    bash "$SCRIPT_DIR/make_scripts_executable.sh"
fi

echo "========================================="
echo "ZamAI Pashto Dataset is ready to use!"
echo "========================================="

# Display directory structure
echo -e "\nDirectory Structure:"
find "$WORKSPACE_DIR" -type d -maxdepth 1 | sort

# Display available options
echo -e "\nAvailable Options:"
echo "1. Run the complete data pipeline:"
echo "   cd $SCRIPT_DIR && ./gather_clean_combine.sh"
echo
echo "2. Extract text from PDF files:"
echo "   cd $SCRIPT_DIR && ./extract_pdf_text.sh"
echo
echo "3. Run data cleaning only:"
echo "   cd $SCRIPT_DIR && ./run_data_cleaning.sh"
echo
echo "4. View documentation and visualizations:"
echo "   ls $WORKSPACE_DIR/asset"
echo "========================================="
echo "Enter your choice (1-4) or press Enter to exit:"
read choice

case $choice in
    1)
        cd "$SCRIPT_DIR" && ./gather_clean_combine.sh
        ;;
    2)
        cd "$SCRIPT_DIR" && ./extract_pdf_text.sh
        ;;
    3)
        cd "$SCRIPT_DIR" && ./run_data_cleaning.sh
        ;;
    4)
        ls -la "$WORKSPACE_DIR/asset"
        ;;
    *)
        echo "Exiting. You can run any script manually from the scripts directory."
        ;;
esac
