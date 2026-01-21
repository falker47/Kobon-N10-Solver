import glob
import json
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import re

def natural_sort_key(s):
    """Sort strings with embedded numbers naturally."""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def plot_lines(ax, lines, title):
    """Plot lines on the given axis."""
    # Viewport
    x_lim = (-10, 10)
    y_lim = (-10, 10)
    
    # Grid for plotting
    x_vals = np.array(x_lim)
    
    for a, b, c in lines:
        if abs(b) > 1e-6:
            y_vals = (-a * x_vals - c) / b
            ax.plot(x_vals, y_vals, 'k-', linewidth=0.5, alpha=0.7)
        else:
            # Vertical line x = -c/a
            if abs(a) > 1e-6:
                x_v = -c / a
                ax.axvline(x_v, color='k', linewidth=0.5, alpha=0.7)
    
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Clean filename for title
    # record_25_variant_12.json -> var_12
    # record_25.json -> base
    short_title = title.replace("record_25_variant_", "var_").replace("record_25.json", "base").replace(".json", "")
    ax.set_title(short_title, fontsize=8)

def create_mosaic():
    files = glob.glob("variants/record_25*.json")
    files.sort(key=natural_sort_key)
    
    n_files = len(files)
    if n_files == 0:
        print("No files found.")
        return

    print(f"Found {n_files} files. Generating mosaic...")

    # Dynamic Grid sizing
    cols = math.ceil(math.sqrt(n_files))
    rows = math.ceil(n_files / cols)
    
    # Create Figure
    # Scale figure size based on grid (e.g. 3 inches per subplot)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
    
    # Flatten axes for easy iteration
    axes_flat = axes.flatten() if n_files > 1 else [axes]
    
    for i, fpath in enumerate(files):
        ax = axes_flat[i]
        
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            lines = np.array(data['lines'])
            
            plot_lines(ax, lines, os.path.basename(fpath))
            
        except Exception as e:
            print(f"Error reading {fpath}: {e}")
            ax.text(0, 0, "Error", ha='center')
    
    # Hide unused subplots
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].axis('off')
        
    plt.tight_layout()
    output_file = "kobon_mosaic.png"
    plt.savefig(output_file, dpi=300)
    print(f"Mosaic saved to {output_file}")
    plt.close()

if __name__ == "__main__":
    create_mosaic()
