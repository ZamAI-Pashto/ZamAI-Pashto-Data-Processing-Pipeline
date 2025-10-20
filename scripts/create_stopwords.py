#!/usr/bin/env python3
"""
This script creates a Pashto stopwords CSV file since the original file was missing.
"""
import pandas as pd

# Common Pashto stop words (pronouns, conjunctions, prepositions)
pashto_stopwords = [
    # Pronouns
    'زه', 'ته', 'هغه', 'هغې', 'موږ', 'تاسو', 'دوی',
    # Conjunctions
    'او', 'یا', 'خو', 'چې', 'که', 'لکه',
    # Prepositions
    'په', 'د', 'له', 'تر', 'نه', 'ته', 'لپاره',
    # Articles and demonstratives
    'دا', 'هغه', 'دغه', 'همدا',
    # Common words
    'ښه', 'نور', 'هم', 'یو', 'یوه', 'ډېر', 'لږ'
]

# Create the DataFrame with the stopwords
df = pd.DataFrame(pashto_stopwords)

# Save to CSV in the project root
df.to_csv('/workspaces/ZamAI-Pashto-Data-Processing-Pipeline/stopwords.csv', index=False, header=False, encoding='utf-8')

print(f"Created stopwords.csv with {len(pashto_stopwords)} Pashto stopwords.")

