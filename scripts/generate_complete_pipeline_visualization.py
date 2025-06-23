#!/usr/bin/env python3
"""
Generate a unified visualization showing the complete Pashto text dataset workflow
combining data sources, processing steps, and final outputs
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, FancyBboxPatch
import numpy as np
import matplotlib.gridspec as gridspec

# Create directories if they don't exist
os.makedirs('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/asset', exist_ok=True)

# Set up the figure with grid layout
fig = plt.figure(figsize=(18, 12))
gs = gridspec.GridSpec(12, 12)
ax = plt.subplot(gs[:, :])
ax.set_xlim(0, 100)
ax.set_ylim(0, 70)
ax.axis('off')

# Define colors
colors = {
    'source': '#3498db',       # Blue
    'process': '#2ecc71',      # Green
    'output': '#e74c3c',       # Red
    'combined': '#9b59b6',     # Purple
    'background': '#f9f9f9',   # Light gray
    'arrow': '#34495e',        # Dark blue
    'text': '#2c3e50',         # Dark text
    'highlight': '#f1c40f',    # Yellow
    'scripts': '#1abc9c',      # Turquoise
    'header': '#2980b9',       # Deep blue
}

# Helper functions for drawing
def draw_box(x, y, width, height, title, content, color, alpha=0.9, fontsize=10):
    rect = FancyBboxPatch((x, y), width, height, 
                         boxstyle=f"round,pad=0.6,rounding_size=0.8",
                         facecolor=color, alpha=alpha, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    
    plt.text(x + width/2, y + height - 1, title, ha='center', va='center', 
             fontsize=fontsize+1, fontweight='bold', color=colors['text'])
    
    # Split content by newlines and add each line
    if content:
        content_lines = content.split('\n')
        line_height = 1.4
        start_y = y + height - 3
        
        for i, line in enumerate(content_lines):
            plt.text(x + width/2, start_y - i * line_height, line, ha='center', 
                     va='center', fontsize=fontsize-1, color=colors['text'])

def draw_arrow(x1, y1, x2, y2, color=colors['arrow'], style='arc3,rad=0.1'):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), 
                          connectionstyle=style, 
                          arrowstyle='-|>', 
                          mutation_scale=20, 
                          linewidth=2, 
                          color=color)
    ax.add_patch(arrow)

def draw_script_label(x, y, script_name, width=10, height=2):
    rect = FancyBboxPatch((x-width/2, y-height/2), width, height, 
                         boxstyle="round,pad=0.3,rounding_size=0.5",
                         facecolor=colors['scripts'], alpha=0.85, 
                         edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    plt.text(x, y, script_name, ha='center', va='center', 
             fontsize=8, color='white', fontweight='bold')

# Draw the background
background = Rectangle((0, 0), 100, 70, facecolor=colors['background'], edgecolor='none')
ax.add_patch(background)

# Add main title
title_bg = Rectangle((0, 65), 100, 5, facecolor=colors['header'], alpha=0.9, edgecolor='none')
ax.add_patch(title_bg)

plt.text(50, 67.5, 'PASHTO TEXT DATASET PROCESSING PIPELINE', ha='center', va='center', 
         fontsize=20, fontweight='bold', color='white')

# 1. DATA SOURCES SECTION
# Draw data sources header
source_header = Rectangle((5, 55), 90, 3, facecolor=colors['source'], alpha=0.7, edgecolor='none')
ax.add_patch(source_header)
plt.text(50, 56.5, 'DATA SOURCES', ha='center', va='center', fontsize=14, fontweight='bold', color='white')

# Draw data sources
draw_box(5, 45, 25, 8, "Web Sources", "BBC Pashto • VOA Pashto • Azadi Radio\nTolonews • Pajhwok • Taand\nOnline Pashto news and content", colors['source'], fontsize=11)
draw_box(37.5, 45, 25, 8, "PDF Documents", "Books • Academic papers • Articles\nReports • Magazines • Documents\nwith Pashto text content", colors['source'], fontsize=11)
draw_box(70, 45, 25, 8, "Existing CSV Files", "Multiple Pashto text CSV files\nRaw, uncleaned text data\nNeeds normalization and cleaning", colors['source'], fontsize=11)

# 2. DATA EXTRACTION SECTION
# Draw processing header
process_header = Rectangle((5, 38), 90, 3, facecolor=colors['process'], alpha=0.7, edgecolor='none')
ax.add_patch(process_header)
plt.text(50, 39.5, 'DATA EXTRACTION & GATHERING', ha='center', va='center', fontsize=14, fontweight='bold', color='white')

# Draw extraction processes
draw_box(5, 28, 25, 8, "Web Scraping", "1. Find article URLs from sources\n2. Extract title and content\n3. Save raw gathered data\n4. Basic text validation", colors['process'], fontsize=11)
draw_box(37.5, 28, 25, 8, "PDF Text Extraction", "1. Extract text from PDF files\n2. Apply OCR for scanned PDFs\n3. Detect and extract sections\n4. Filter non-Pashto content", colors['process'], fontsize=11)
draw_box(70, 28, 25, 8, "Load CSV Files", "1. Find all CSV files\n2. Load data with proper encoding\n3. Concatenate into single dataframe\n4. Check for encoding issues", colors['process'], fontsize=11)

# 3. DATA CLEANING SECTION
# Draw cleaning header
cleaning_header = Rectangle((5, 21), 90, 3, facecolor=colors['highlight'], alpha=0.7, edgecolor='none')
ax.add_patch(cleaning_header)
plt.text(50, 22.5, 'DATA CLEANING & NORMALIZATION', ha='center', va='center', fontsize=14, fontweight='bold', color='white')

# Draw cleaning processes
draw_box(5, 11, 28, 8, "Handle Missing Values", "1. Identify missing/empty values\n2. Remove rows with insufficient data\n3. Fill or discard incomplete entries\n4. Check data integrity", colors['highlight'], fontsize=11)
draw_box(36, 11, 28, 8, "Text Normalization", "1. Remove extra whitespace/newlines\n2. Handle special characters\n3. Standardize text format\n4. Remove stopwords (optional)", colors['highlight'], fontsize=11)
draw_box(67, 11, 28, 8, "Remove Duplicates", "1. Identify duplicate content\n2. Filter redundant data\n3. Keep unique entries\n4. Ensure data quality", colors['highlight'], fontsize=11)

# 4. FINAL OUTPUT SECTION
# Draw output header
output_header = Rectangle((5, 4), 90, 3, facecolor=colors['output'], alpha=0.7, edgecolor='none')
ax.add_patch(output_header)
plt.text(50, 5.5, 'FINAL OUTPUT FOR MODEL FINE-TUNING', ha='center', va='center', fontsize=14, fontweight='bold', color='white')

# Draw output formats
draw_box(20, 1, 28, 2, "", "CSV Format", colors['output'], alpha=0.6, fontsize=9)
draw_box(50, 1, 28, 2, "", "JSONL Format (for model fine-tuning)", colors['output'], alpha=0.6, fontsize=9)
draw_box(80, 1, 15, 2, "", "Train/Val Split", colors['output'], alpha=0.6, fontsize=9)

# Draw the combined output
draw_box(36, 1, 28, 2, "Combined Clean Dataset", "", colors['combined'], fontsize=11)

# Add script labels
draw_script_label(17.5, 25, "gather_pashto_data.py")
draw_script_label(50, 25, "extract_pashto_from_pdf.py")
draw_script_label(82.5, 25, "read_csv in cleaning notebook")

draw_script_label(50, 8, "Comprehensive_Data_Cleaning.ipynb")
draw_script_label(82.5, 8, "combine_data.py")

# Connect everything with arrows
# Sources to extraction
draw_arrow(17.5, 45, 17.5, 36, style='arc3,rad=0')
draw_arrow(50, 45, 50, 36, style='arc3,rad=0')
draw_arrow(82.5, 45, 82.5, 36, style='arc3,rad=0')

# Extraction to cleaning
draw_arrow(17.5, 28, 19, 19, style='arc3,rad=-0.1')
draw_arrow(50, 28, 50, 19, style='arc3,rad=0')
draw_arrow(82.5, 28, 81, 19, style='arc3,rad=0.1')

# Cleaning interconnections
draw_arrow(33, 15, 36, 15, style='arc3,rad=0')
draw_arrow(64, 15, 67, 15, style='arc3,rad=0')

# Cleaning to output
draw_arrow(19, 11, 20, 3, style='arc3,rad=-0.2')
draw_arrow(50, 11, 50, 3, style='arc3,rad=0')
draw_arrow(81, 11, 80, 3, style='arc3,rad=0.2')

# Add a legend
legend_x, legend_y = 88, 62
legend_items = [
    (colors['source'], "Data Sources"),
    (colors['process'], "Extraction Processes"),
    (colors['highlight'], "Cleaning & Normalization"),
    (colors['output'], "Output Formats"),
    (colors['combined'], "Final Dataset"),
    (colors['scripts'], "Processing Scripts")
]

# Draw legend box
legend_bg = Rectangle((85, 56), 13, 8, facecolor='white', alpha=0.8, edgecolor='black', linewidth=1)
ax.add_patch(legend_bg)
plt.text(91.5, 63, "Legend", ha='center', fontsize=10, fontweight='bold')

# Draw legend items
for i, (color, label) in enumerate(legend_items):
    rect = Rectangle((86, 62-i*1.2), 1.5, 1, facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    plt.text(88.5, 62.5-i*1.2, label, va='center', fontsize=9)

# Add a pipeline flow diagram at the bottom
flow_x = 3
flow_y = 2
flow_steps = ["Raw Data", "→", "Extraction", "→", "Cleaning", "→", "Normalization", "→", "Fine-tuning Ready"]
flow_colors = [colors['source'], 'black', colors['process'], 'black', colors['highlight'], 'black', colors['highlight'], 'black', colors['combined']]

for i, (step, color) in enumerate(zip(flow_steps, flow_colors)):
    plt.text(flow_x + i*10.5, flow_y, step, ha='center', va='center', fontsize=10, 
             color='white' if color != 'black' else 'black',
             fontweight='bold' if color != 'black' else 'normal',
             bbox=dict(facecolor=color if color != 'black' else 'none', 
                      edgecolor='none', 
                      alpha=0.8 if color != 'black' else 1.0,
                      boxstyle="round,pad=0.3" if color != 'black' else "round,pad=0"))

# Save the figure with high resolution
plt.savefig('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/asset/pashto_complete_data_pipeline.png', dpi=300, bbox_inches='tight')
plt.close()

print("Complete visualization created at: /workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/asset/pashto_complete_data_pipeline.png")
