import json
import numpy as np
import matplotlib.pyplot as plt
import os
from visualizer import plot_configuration
from geometry import KobonSolver

def plot_single(filepath, output_name):
    print(f"Plotting {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        lines = np.array(data['lines'])
        
        # Calculate Triangles for overlay
        solver = KobonSolver(lines)
        triangles = solver.find_triangles()
        
        plt.figure(figsize=(10, 10))
        plot_configuration(lines, triangles) # This uses visualizer.py logic (shows triangles)
        
        # Override title slightly or trust visualizer? 
        # Visualizer saves to 'kobon_result.png' by default in some versions or plt.show()
        # We need to save manually to output_name
        plt.savefig(f"images/{output_name}", dpi=1000)
        plt.close()
        print(f"Saved images/{output_name}")
        
    except Exception as e:
        print(f"Failed to plot {filepath}: {e}")

def run_highlights():
    # 1. Variant 0 (Original Record 25)
    plot_single("solutions_final/variant0.json", "highlight_variant0.png")
    
    # 2. Symmetric (Score 18)
    plot_single("solutions_final/symmetric_variant_18triangles.json", "highlight_symmetric_18.png")
    
    # 3. Soft Symmetry (Optimal 25)
    plot_single("solutions_final/variant_soft_symmetry.json", "highlight_soft_symmetry.png")

if __name__ == "__main__":
    run_highlights()
