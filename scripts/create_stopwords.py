#!/usr/bin/env python3
"""
This script creates a Pashto stopwords CSV file since the original file was missing.
"""
import pandas as pd

# Common Pashto stop words (pronouns, conjunctions, prepositions)
pashto_stopwords = [
    # Pronouns
    'ښه', 'خدای', 'نور', 'مهرباني'  # Add more Pashto stopwords as needed
]

df = pd.DataFrame(pashto_stopwords)
df.to_csv('/workspaces/ZamAI-Pashto-Data-Processing-Pipeline/stopwords.csv', index=False, header=False, encoding='utf-8')
print("Stopwords file created successfully!")
]

# Create the DataFrame with the stopwords
df = pd.DataFrame(pashto_stopwords)

# Save to CSV
df.to_csv('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/stopwords.csv', index=False, header=False, encoding='utf-8')

print(f"Created stopwords.csv with {len(pashto_stopwords)} Pashto stopwords.")
