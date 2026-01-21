import json
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from geometry import KobonSolver

def load_lines(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    print(f"Loaded {filename} with score {data['score']}")
    return np.array(data['lines'])

def run_breather():
    # 1. Load
    filename = "soft_symmetry_final.json"
    lines = load_lines(filename)
    
    # Ensure normalization (a^2+b^2=1) for accurate distance comparison
    norms = np.linalg.norm(lines[:, :2], axis=1)
    lines[:, :2] /= norms[:, np.newaxis]
    lines[:, 2] /= norms # Normalize c too to match
    
    # 2. Classify Lines
    # Distance to origin is |c| (since normal is length 1)
    dists = np.abs(lines[:, 2])
    
    # Sort indices by distance
    sorted_indices = np.argsort(dists)
    
    inner_indices = sorted_indices[:5]
    outer_indices = sorted_indices[5:]
    
    print(f"Inner Lines Indices: {inner_indices}")
    print(f"Outer Lines Indices: {outer_indices}")
    print(f"Inner Dists: {dists[inner_indices]}")
    print(f"Outer Dists: {dists[outer_indices]}")
    
    # 3. Breathing Loop
    base_lines = lines.copy()
    scales = np.arange(0.800, 1.200, 0.0005)
    
    scores = []
    best_score_found = 0
    saved_best = False
    
    print(f"Starting sweep from scale {scales[0]} to {scales[-1]}...")
    
    for scale in tqdm(scales):
        current_lines = base_lines.copy()
        
        # Scale Inner Lines' C parameter
        # C represents distance from origin if normal is fixed
        current_lines[inner_indices, 2] *= scale
        
        # Solve
        solver = KobonSolver(current_lines)
        # Note: KobonSolver doesn't need to be re-instantiated if we just updated geometry,
        # but the class currently takes lines in init.
        # Efficient enough for this loop.
        
        triangles = solver.find_triangles()
        score = len(triangles)
        scores.append(score)
        
        if score > 25:
            print(f"\n!!! FOUND SCORE {score} AT SCALE {scale:.4f} !!!")
            
            # Save immediately
            output_file = f"record_{score}_breather.json"
            with open(output_file, 'w') as f:
                json.dump({
                    "score": score,
                    "scale_factor": scale,
                    "lines": current_lines.tolist()
                }, f, indent=4)
            print(f"Saved to {output_file}")
            saved_best = True
            best_score_found = score
            break
            
        if score > best_score_found:
            best_score_found = score
            
    print(f"\nSweep Complete. Max Score: {best_score_found}")
    
    # 4. Plot
    plt.figure(figsize=(10, 6))
    plt.plot(scales[:len(scores)], scores, 'b-', label='Triangle Count')
    plt.axhline(25, color='r', linestyle='--', label='Baseline (25)')
    plt.xlabel('Scale Factor (Inner Lines)')
    plt.ylabel('Score')
    plt.title('Breather Scan: Score vs Scale')
    plt.legend()
    plt.grid(True)
    
    plt.savefig('breather_scan.png')
    print("Saved plot to breather_scan.png")

if __name__ == "__main__":
    run_breather()
