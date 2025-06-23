#!/bin/bash
# Script to update file paths in Python scripts to use the ZamAI_Pashto_Datasets folder
# Created on: June 23, 2025

# Set variables
TARGET_DIR="/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets"
OLD_PATH="/workspaces/pashto-text-dataset"
NEW_PATH="/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets"

echo "========================================="
echo "Updating paths in Python files to use ZamAI_Pashto_Datasets"
echo "========================================="

# Find all Python files and update the paths
find "$TARGET_DIR" -name "*.py" | while read file; do
    echo "Updating paths in: $(basename "$file")"
    # Replace the old path with the new path in the file
    sed -i "s|$OLD_PATH|$NEW_PATH|g" "$file"
done

# Update paths in notebook files
find "$TARGET_DIR" -name "*.ipynb" | while read file; do
    echo "Updating paths in notebook: $(basename "$file")"
    # Replace the old path with the new path in the notebook
    sed -i "s|$OLD_PATH|$NEW_PATH|g" "$file"
done

echo "========================================="
echo "Path updates completed!"
echo "All Python files and notebooks now use the ZamAI_Pashto_Datasets folder"
echo "========================================="
