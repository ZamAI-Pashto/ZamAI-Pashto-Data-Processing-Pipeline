#!/usr/bin/env python3
"""
This script creates a Pashto stopwords CSV file since the original file was missing.
"""
import pandas as pd

# Common Pashto stop words (pronouns, conjunctions, prepositions)
pashto_stopwords = [
    # Pronouns
    'زه', 'ته', 'دی', 'دا', 'موږ', 'تاسو', 'هغوی', 'زما', 'ستا', 'زموږ', 'ستاسو', 'هغه', 
    
    # Conjunctions
    'او', 'یا', 'خو', 'چې', 'نو', 'که', 'مګر', 'لاکن', 'همدا', 'همدغه', 'هم',
    
    # Prepositions
    'د', 'په', 'له', 'څخه', 'سره', 'ته', 'لپاره', 'پورې', 'باندې', 'لاندې', 'کې',
    
    # Articles and demonstratives
    'یو', 'یوه', 'دا', 'هغه', 'دغه',
    
    # Numbers
    'یو', 'دوه', 'درې', 'څلور', 'پنځه', 'شپږ', 'اووه', 'اته', 'نه', 'لس',
    
    # Common verbs (conjugations)
    'دی', 'ده', 'وم', 'وې', 'و', 'وو', 'شو', 'شوه', 'شول', 'کړ', 'کړه', 'کړل',
    
    # Adverbs
    'نه', 'هو', 'بیا', 'اوس', 'بس', 'نور', 'دلته', 'هلته',
    
    # Various common words
    'به', 'باید', 'کولای', 'کولی', 'شي', 'وي'
]

# Create the DataFrame with the stopwords
df = pd.DataFrame(pashto_stopwords)

# Save to CSV
df.to_csv('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/stopwords.csv', index=False, header=False, encoding='utf-8')

print(f"Created stopwords.csv with {len(pashto_stopwords)} Pashto stopwords.")
