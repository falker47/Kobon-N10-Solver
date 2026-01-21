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
    
    # Custom Title Clean
    if "variant_soft_symmetry" in title: t = "Soft Sym (25)"
    elif "variant0" in title: t = "Variant 0 (25)"
    elif "symmetric_variant_18" in title: t = "Hard Sym (18)"
    else: t = title.replace(".json","").replace("variant","v").replace("family","F").replace("singleton","S").replace("_"," ")
    
    ax.set_title(t, fontsize=6)

def create_mosaic():
    # Source: solutions_final/
    files = glob.glob("solutions_final/*.json")
    if not files:
        print("No files found in solutions_final/")
        return

    # Specific Order:
    # 1. Soft Symmetry
    # 2. Variant 0
    # 3. Symmetric 18
    # 4. Others (sorted naturally)
    
    ordered_files = []
    others = []
    
    specials = {
        "variant_soft_symmetry.json": None,
        "variant0.json": None,
        "symmetric_variant_18triangles.json": None
    }
    
    for f in files:
        fname = os.path.basename(f)
        if fname in specials:
            specials[fname] = f
        else:
            others.append(f)
            
    others.sort(key=lambda x: natural_sort_key(os.path.basename(x)))
    
    if specials["variant_soft_symmetry.json"]: ordered_files.append(specials["variant_soft_symmetry.json"])
    if specials["variant0.json"]: ordered_files.append(specials["variant0.json"])
    if specials["symmetric_variant_18triangles.json"]: ordered_files.append(specials["symmetric_variant_18triangles.json"])
    
    ordered_files.extend(others)
    
    n_files = len(ordered_files)
    print(f"Plotting {n_files} solutions...")
    
    cols = math.ceil(math.sqrt(n_files))
    rows = math.ceil(n_files / cols)
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.5, rows * 2.5))
    axes_flat = axes.flatten()
    
    for i, fpath in enumerate(ordered_files):
        ax = axes_flat[i]
        try:
            with open(fpath, 'r') as f: data = json.load(f)
            plot_lines(ax, np.array(data['lines']), os.path.basename(fpath))
        except:
            ax.text(0.5, 0.5, "Error", ha='center')
            
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].axis('off')
        
    plt.tight_layout()
    plt.savefig('images/kobon_mosaic.jpg', dpi=1000, format='jpg')
    print("Saved images/kobon_mosaic.jpg")
    plt.close()

if __name__ == "__main__":
    create_mosaic()
