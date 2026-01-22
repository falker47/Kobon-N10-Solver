import glob
import json
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import re

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def extract_variant_number(filename):
    # Matches "variant" followed by digits, e.g., "variant0.json", "variant12_singleton.json"
    match = re.search(r'variant(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def plot_lines(ax, lines, title):
    x_lim = (-10, 10)
    y_lim = (-10, 10)
    x_vals = np.array(x_lim)
    
    for a, b, c in lines:
        if abs(b) > 1e-6:
            y_vals = (-a * x_vals - c) / b
            ax.plot(x_vals, y_vals, 'k-', linewidth=0.5, alpha=0.7)
        else:
            if abs(a) > 1e-6:
                x_v = -c / a
                ax.axvline(x_v, color='k', linewidth=0.5, alpha=0.7)
    
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Clean Title
    # Extract just the number or simple name
    num = extract_variant_number(title)
    if num is not None:
        if num == 0:
            t = "Variant 0 (25)"
        else:
            t = f"Variant {num}"
    else:
        t = title
    
    ax.set_title(t, fontsize=6)

def create_mosaic(source_dir, output_path, dpi_val):
    search_pattern = os.path.join(source_dir, "*.json")
    files = glob.glob(search_pattern)
    if not files:
        print(f"No files found in {source_dir}")
        return

    # Filter for Variant 0 to 71
    selected_files = []
    
    # Map variant number to file path to ensure we get exactly 0-71
    variant_map = {}
    
    for f in files:
        fname = os.path.basename(f)
        num = extract_variant_number(fname)
        if num is not None and 0 <= num <= 71:
            # Check if this file is the "primary" one for this number
            # The list shows e.g. "variant1_singleton.json", "variant0.json"
            # If duplicates exist (unlikely based on list), we take first found or warn.
            # Based on file list, they seem unique per number.
            variant_map[num] = f

    # Create ordered list 0 to 71
    ordered_files = []
    missing = []
    for i in range(72):
        if i in variant_map:
            ordered_files.append(variant_map[i])
        else:
            missing.append(i)
            
    if missing:
        print(f"Warning: Missing variants: {missing}")
    
    n_files = len(ordered_files)
    print(f"Plotting {n_files} solutions to {output_path}...")
    
    if n_files == 0:
        return

    cols = math.ceil(math.sqrt(n_files))
    rows = math.ceil(n_files / cols)
    
    # Adjust figure size based on DPI to ensure lines aren't too thin/thick? 
    # Or keep physical size constant. 
    # The previous code used (cols * 2.5, rows * 2.5).
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.5, rows * 2.5))
    axes_flat = axes.flatten()
    
    for i, fpath in enumerate(ordered_files):
        ax = axes_flat[i]
        try:
            with open(fpath, 'r') as f: data = json.load(f)
            plot_lines(ax, np.array(data['lines']), os.path.basename(fpath))
        except Exception as e:
            print(f"Error plotting {fpath}: {e}")
            ax.text(0.5, 0.5, "Error", ha='center')
            
    # Hide unused subplots
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].axis('off')
        
    plt.tight_layout()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=dpi_val, format='jpg')
    print(f"Saved {output_path} at {dpi_val} DPI")
    plt.close()

if __name__ == "__main__":
    # 1. High Res Version
    # "crea un nuovo @[images/originals/kobon_mosaic.jpg] ... mi serve una versione con dpi = 500 da mettere in @[images/originals]"
    create_mosaic("solutions", "images/originals/kobon_mosaic.jpg", 500)
    
    # 2. Light Version
    # "e una leggera che andrà integrata nel pdf da inserire nel percorso @[images]"
    # Assuming 'images/kobon_mosaic.jpg' is the target path for the one to be used in PDF/images dir
    create_mosaic("solutions", "images/kobon_mosaic.jpg", 150)

