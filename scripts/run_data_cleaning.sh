#!/bin/bash

# This script runs the Comprehensive Data Cleaning notebook to clean the Pashto text dataset
# It will create a cleaned_data directory with the processed files ready for model fine-tuning

echo "Starting Pashto dataset cleaning process..."
jupyter nbconvert --to notebook --execute /workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/scripts/Comprehensive_Data_Cleaning.ipynb --output /workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/scripts/Comprehensive_Data_Cleaning_executed.ipynb

if [ $? -eq 0 ]; then
    echo "✅ Data cleaning completed successfully!"
    echo "Cleaned data is available in the /workspaces/pashto-text-dataset/cleaned_data directory."
else
    echo "❌ Error occurred during data cleaning. Please check the notebook for details."
fi
