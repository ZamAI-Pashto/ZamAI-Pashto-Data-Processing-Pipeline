#!/usr/bin/env python3
"""
Generate a visualization of the Pashto text dataset processing workflow
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np
from matplotlib.path import Path
import matplotlib.patches as patches

# Create directories if they don't exist
os.makedirs('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/asset', exist_ok=True)

# Set up the figure
plt.figure(figsize=(16, 10))
ax = plt.gca()
ax.set_xlim(0, 100)
ax.set_ylim(0, 60)
ax.axis('off')

# Define colors
colors = {
    'data_source': '#3498db',  # Blue
    'process': '#2ecc71',      # Green
    'output': '#e74c3c',       # Red
    'combined': '#9b59b6',     # Purple
    'background': '#f1f2f6',   # Light gray
    'arrow': '#2c3e50',        # Dark blue
    'text': '#000000',         # Black
    'highlight': '#f39c12',    # Orange
}

# Helper functions for drawing
def draw_box(x, y, width, height, title, content, color, alpha=0.9):
    rect = Rectangle((x, y), width, height, facecolor=color, alpha=alpha, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    plt.text(x + width/2, y + height - 1, title, ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Split content by newlines and add each line
    content_lines = content.split('\n')
    line_height = 1.4
    start_y = y + height - 2.5
    
    for i, line in enumerate(content_lines):
        plt.text(x + width/2, start_y - i * line_height, line, ha='center', va='center', fontsize=9)

def draw_arrow(x1, y1, x2, y2, color=colors['arrow']):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), 
                          connectionstyle='arc3,rad=0.1', 
                          arrowstyle='-|>', 
                          mutation_scale=20, 
                          linewidth=2, 
                          color=color)
    ax.add_patch(arrow)

def draw_process_flow(x, y, width, height, title, steps, color):
    # Draw the main box
    rect = Rectangle((x, y), width, height, facecolor=color, alpha=0.9, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    
    # Draw the title
    plt.text(x + width/2, y + height - 1, title, ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Draw the numbered steps
    for i, step in enumerate(steps):
        plt.text(x + 2, y + height - 3 - i*2, f"{i+1}. {step}", va='top', fontsize=9)

# Draw the background
background = Rectangle((0, 0), 100, 60, facecolor=colors['background'], edgecolor='none')
ax.add_patch(background)

# Add title
plt.text(50, 58, 'Pashto Text Dataset Processing Workflow', ha='center', va='center', fontsize=16, fontweight='bold')

# Draw data sources
draw_box(5, 45, 15, 10, "Web Sources", "BBC Pashto\nVOA Pashto\nAzadi Radio\nTolonews\nPajhwok\netc.", colors['data_source'])
draw_box(25, 45, 15, 10, "PDF Documents", "Books\nArticles\nReports\nAcademic papers\nOther documents", colors['data_source'])
draw_box(45, 45, 15, 10, "CSV Files", "Multiple CSV files\nwith Pashto text\n(uncleaned)", colors['data_source'])

# Draw gathering processes
draw_process_flow(5, 30, 15, 10, "Web Scraping", [
    "Find article URLs",
    "Extract content",
    "Extract titles",
    "Basic validation",
    "Save raw data"
], colors['process'])

draw_process_flow(25, 30, 15, 10, "PDF Extraction", [
    "Load PDF document",
    "Extract text content",
    "Use OCR if needed",
    "Extract sections",
    "Validate Pashto text"
], colors['process'])

# Draw cleaning process
draw_process_flow(25, 15, 35, 10, "Data Cleaning Process", [
    "Remove empty records",
    "Handle missing values",
    "Remove duplicates",
    "Filter by content length",
    "Normalize text",
    "Remove stopwords (optional)",
    "Segment into train/validation"
], colors['highlight'])

# Draw output formats
draw_box(70, 30, 15, 10, "Gathered Data", "Raw gathered data\nCSV format\nJSON format\nSource metadata", colors['output'])
draw_box(70, 15, 15, 10, "Extracted PDF Data", "Extracted text\nSection data\nCSV format\nJSON format", colors['output'])
draw_box(70, 0, 15, 10, "Cleaned Data", "Normalized text\nWithout duplicates\nWithout empty values\nFormatted for fine-tuning", colors['output'])

# Draw combined data
draw_box(35, 0, 25, 10, "Combined Dataset", "Merged from all sources\nDuplicates removed\nFully normalized\nReady for fine-tuning\nIn CSV and JSONL formats", colors['combined'])

# Draw connections
# Web sources to scraping
draw_arrow(12.5, 45, 12.5, 40)

# PDF documents to extraction
draw_arrow(32.5, 45, 32.5, 40)

# CSV files to cleaning
draw_arrow(52.5, 45, 42.5, 25)

# Web scraping to gathering output
draw_arrow(20, 35, 70, 35)

# PDF extraction to extraction output
draw_arrow(40, 35, 70, 35)

# Gathering output to cleaning process
draw_arrow(77.5, 30, 60, 25)

# Extraction output to cleaning process
draw_arrow(77.5, 15, 60, 20)

# Cleaning process to cleaned data
draw_arrow(42.5, 15, 70, 5)

# All cleaned data to combined dataset
draw_arrow(70, 5, 60, 5)

# Add legend
legend_x, legend_y = 82, 50
legend_width, legend_height = 15, 8
legend_rect = Rectangle((legend_x, legend_y), legend_width, legend_height, 
                        facecolor='white', alpha=0.8, edgecolor='black')
ax.add_patch(legend_rect)

plt.text(legend_x + legend_width/2, legend_y + legend_height - 0.8, "Legend", 
         ha='center', va='center', fontsize=10, fontweight='bold')

# Legend items
legend_items = [
    (colors['data_source'], "Data Sources"),
    (colors['process'], "Processing Scripts"),
    (colors['highlight'], "Cleaning & Normalization"),
    (colors['output'], "Output Data"),
    (colors['combined'], "Combined Dataset")
]

for i, (color, label) in enumerate(legend_items):
    legend_item_y = legend_y + legend_height - 2 - i*1.2
    rect = Rectangle((legend_x + 1, legend_item_y), 2, 0.8, facecolor=color, edgecolor='black')
    ax.add_patch(rect)
    plt.text(legend_x + 4, legend_item_y + 0.4, label, va='center', fontsize=8)

# Add script names to the diagram
plt.text(12.5, 28, "gather_pashto_data.py", ha='center', va='center', fontsize=7, color='darkblue', rotation=0)
plt.text(32.5, 28, "extract_pashto_from_pdf.py", ha='center', va='center', fontsize=7, color='darkblue', rotation=0)
plt.text(42.5, 13, "Comprehensive_Data_Cleaning.ipynb", ha='center', va='center', fontsize=7, color='darkblue', rotation=0)
plt.text(47.5, 5, "combine_data.py", ha='center', va='center', fontsize=7, color='darkblue', rotation=0)

# Save the figure
plt.savefig('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/asset/pashto_data_processing_workflow.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization created at: /workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/asset/pashto_data_processing_workflow.png")
