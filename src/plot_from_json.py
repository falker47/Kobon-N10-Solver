import json
import numpy as np
from visualizer import plot_configuration

def plot_json(filename):
    print(f"Loading {filename}...")
    with open(filename, 'r') as f:
        data = json.load(f)
    
    lines = np.array(data['lines'])
    from geometry import KobonSolver
    solver = KobonSolver(lines)
    triangles = solver.find_triangles()
    
    print(f"Plotting configuration with {len(lines)} lines and {len(triangles)} triangles...")
    plot_configuration(lines, triangles)

if __name__ == "__main__":
    plot_json("record_25.json")
