#!/usr/bin/env python3
"""
Generate a second visualization showing the data transformation process
from raw text to fine-tuning ready format
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
plt.figure(figsize=(14, 10))
ax = plt.gca()
ax.set_xlim(0, 100)
ax.set_ylim(0, 70)
ax.axis('off')

# Define colors
colors = {
    'raw': '#e74c3c',         # Red
    'processing': '#3498db',   # Blue
    'cleaned': '#2ecc71',      # Green
    'final': '#9b59b6',        # Purple
    'background': '#f5f6fa',   # Light gray
    'arrow': '#2c3e50',        # Dark blue
    'box': '#ecf0f1',          # White smoke
    'highlight': '#f39c12',    # Orange
}

# Helper functions for drawing
def draw_box(x, y, width, height, title, color, alpha=0.9):
    rect = Rectangle((x, y), width, height, facecolor=color, alpha=alpha, edgecolor='black', linewidth=1)
    ax.add_patch(rect)
    plt.text(x + width/2, y + height - 1, title, ha='center', va='center', fontsize=11, fontweight='bold')

def draw_text_box(x, y, width, height, text, background=colors['box'], border_color='black'):
    rect = Rectangle((x, y), width, height, facecolor=background, alpha=0.9, edgecolor=border_color, linewidth=1)
    ax.add_patch(rect)
    
    # Wrap text to fit box width
    lines = []
    current_line = ""
    words = text.split()
    max_chars = int(width * 3)  # Approximate characters per line
    
    for word in words:
        if len(current_line + " " + word) <= max_chars:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Render text
    line_height = height / (len(lines) + 1)
    for i, line in enumerate(lines):
        plt.text(x + width/2, y + height - (i+1)*line_height, 
                line, ha='center', va='center', fontsize=9)

def draw_arrow(x1, y1, x2, y2, color=colors['arrow']):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), 
                          connectionstyle='arc3,rad=0.0', 
                          arrowstyle='-|>', 
                          mutation_scale=20, 
                          linewidth=2, 
                          color=color)
    ax.add_patch(arrow)

def draw_process_step(x, y, width, height, title, input_text, process, output_text):
    # Draw the main box
    draw_box(x, y, width, height, title, colors['processing'])
    
    # Draw the input box
    input_box_height = height * 0.25
    draw_text_box(x + 2, y + height - input_box_height - 4, width - 4, input_box_height, input_text)
    
    # Draw the process description
    plt.text(x + width/2, y + height/2, process, ha='center', va='center', fontsize=10, 
             fontweight='bold', bbox=dict(facecolor=colors['highlight'], alpha=0.2, boxstyle="round,pad=0.5"))
    
    # Draw the output box
    output_box_height = height * 0.25
    draw_text_box(x + 2, y + 2, width - 4, output_box_height, output_text)
    
    # Draw internal arrows
    internal_arrow_x = x + width/2
    draw_arrow(internal_arrow_x, y + height - input_box_height - 5, internal_arrow_x, y + height/2 + 3)
    draw_arrow(internal_arrow_x, y + height/2 - 3, internal_arrow_x, y + output_box_height + 3)

# Draw the background
background = Rectangle((0, 0), 100, 70, facecolor=colors['background'], edgecolor='none')
ax.add_patch(background)

# Add title
plt.text(50, 66, 'Pashto Text Data Transformation Process', ha='center', va='center', 
         fontsize=16, fontweight='bold')
plt.text(50, 63, 'From Raw Text to Fine-tuning Ready Data', ha='center', va='center', 
         fontsize=14)

# Draw process steps
# Step 1: Raw Text Collection
draw_process_step(10, 45, 30, 15, "1. Raw Text Collection", 
                 "دکندهار دلو يې والو په سيمه کې دبريښناکوټ څنګ ته دوه نفره چې پر موټر سيکل سپاره وه په ماين والوتل", 
                 "Gather text from websites and PDFs", 
                 "Raw collected text with formatting issues, empty lines, etc.")

# Step 2: Text Cleaning
draw_process_step(50, 45, 30, 15, "2. Text Cleaning", 
                 "دکندهار دلو يې والو په سيمه کې دبريښناکوټ\n\nڅنګ ته دوه نفره چې پر موټر سيکل سپاره وه په ماين والوتل", 
                 "Remove empty lines, extra spaces,\nnewlines and special characters", 
                 "دکندهار دلو يې والو په سيمه کې دبريښناکوټ څنګ ته دوه نفره چې پر موټر سيکل سپاره وه په ماين والوتل")

# Step 3: Normalization
draw_process_step(10, 25, 30, 15, "3. Text Normalization", 
                 "دکندهار دلو يې والو په سيمه کې دبريښناکوټ څنګ ته دوه نفره چې پر موټر سيکل سپاره وه په ماين والوتل", 
                 "Normalize Pashto text,\nstandardize character representation", 
                 "Normalized Pashto text with consistent formatting")

# Step 4: Stopword Removal
draw_process_step(50, 25, 30, 15, "4. Stopword Removal (Optional)", 
                 "دکندهار دلو يې والو په سيمه کې دبريښناکوټ څنګ ته دوه نفره چې پر موټر سيکل سپاره وه په ماين والوتل", 
                 "Remove common Pashto stopwords\n(د, په, او, چې, له, نه, etc.)", 
                 "Text with meaningful words only, stopwords removed")

# Step 5: Training Format
draw_process_step(30, 5, 30, 15, "5. Prepare for Fine-tuning", 
                 "Cleaned and normalized text entries", 
                 "Format as prompt-completion pairs\nSplit into train/validation sets", 
                 '{\"prompt\": \"title\", \"completion\": \"content\"}')

# Draw the connections between steps
draw_arrow(40, 52.5, 50, 52.5)  # Step 1 to Step 2
draw_arrow(50, 45, 25, 40)      # Step 2 to Step 3
draw_arrow(40, 32.5, 50, 32.5)  # Step 3 to Step 4
draw_arrow(50, 25, 45, 20)      # Step 4 to Step 5

# Add explanatory text about the process
explanation_text = (
    "The Pashto text data transformation process involves several key steps to prepare raw text for model fine-tuning.\n"
    "Starting with text collection from various sources, the data undergoes cleaning to remove formatting issues,\n"
    "normalization to ensure consistency, optional stopword removal, and finally formatting for the target model.\n"
    "This process ensures high-quality, consistent training data for optimal model performance."
)

plt.text(50, 70-3, explanation_text, ha='center', va='top', fontsize=9, 
         bbox=dict(facecolor='white', alpha=0.7, boxstyle="round,pad=0.5"))

# Save the figure
plt.savefig('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/asset/pashto_data_transformation_process.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization created at: /workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/asset/pashto_data_transformation_process.png")
