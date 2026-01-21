import json
import numpy as np
import time
from tqdm import tqdm
from geometry import KobonSolver
from optimizer import Optimizer
from visualizer import plot_configuration

def load_config(filename="record_25.json"):
    with open(filename, 'r') as f:
        data = json.load(f)
    print(f"Loaded configuration with Score: {data['score']}")
    return np.array(data['lines']), data['score']

def save_best(lines, score, filename="record_26.json"):
    data = {
        "n_lines": len(lines),
        "score": score,
        "lines": lines.tolist()
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nSAVED NEW BEST: {filename} with score {score}")

def canonicalize(lines):
    """
    Standardize geometric representation of lines for comparison.
    1. Normalize ax+by+c=0 such that a^2+b^2=1.
    2. Enforce sign convention: first non-zero component of (a,b) must be positive.
    3. Sort lines by (a, b, c).
    """
    # 1. Normalize Vector
    norms = np.linalg.norm(lines[:, :2], axis=1, keepdims=True)
    norms[norms < 1e-9] = 1.0
    lines = lines / norms
    
    # 2. Enforce Sign
    # Check 'a'
    neg_a = lines[:, 0] < -1e-9
    # Check 'a' near 0 and 'b' < 0
    zero_a = np.abs(lines[:, 0]) < 1e-9
    neg_b = lines[:, 1] < -1e-9
    flip_mask = neg_a | (zero_a & neg_b)
    
    lines[flip_mask] *= -1
    
    # 3. Sort
    # Lexicographical sort based on columns
    ind = np.lexsort((lines[:, 2], lines[:, 1], lines[:, 0]))
    return lines[ind]

def is_distinct(new_lines, known_configs, threshold=0.1):
    """
    Check if new_lines is distinct from all lines in known_configs.
    Metric: Max Euclidean distance between corresponding canonical lines.
    """
    canon_new = canonicalize(new_lines.copy())
    
    for known in known_configs:
        canon_known = canonicalize(known.copy())
        diff = np.linalg.norm(canon_new - canon_known)
        if diff < threshold:
            return False
    return True

def refine():
    # Load initial state
    initial_lines, initial_score = load_config()
    n_lines = len(initial_lines)
    
    print(f"Starting localized refinement. Baseline score: {initial_score}")
    
    optimizer = Optimizer(n_lines=n_lines)
    
    # Track variants
    known_variants = [initial_lines.copy()]
    variant_count = 0
    
    current_best_lines = initial_lines.copy()
    current_best_score = initial_score
    
    n_kicks = 1000
    iterations_per_kick = 5000
    
    # Kick Schedule Weights
    # 0.5 (Big), 0.1 (Medium), 0.01 (Small)
    sigmas = [0.5, 0.1, 0.01]
    probs = [0.3, 0.4, 0.3]
    
    pbar = tqdm(range(n_kicks), desc="Kicks")
    
    for kick in pbar:
        # Reset to CURRENT BEST (exploitation)
        # OR: Randomly pick from known variants? 
        # Strategy: Stick to current best to dig deeper, but occasionally switch?
        # Let's stick to current best for now.
        optimizer.state = current_best_lines.copy()
        
        # Pick Sigma
        sigma = np.random.choice(sigmas, p=probs)
        
        # Apply Gaussian noise
        noise = np.random.normal(0, sigma, size=optimizer.state.shape)
        optimizer.state += noise
        optimizer.normalize_lines(optimizer.state)
        
        # Optimize
        final_lines, score = optimizer.optimize(
            iterations=iterations_per_kick, 
            T_start=sigma, # Start temp related to kick size?
            T_end=0.0001, 
            verbose=False
        )
        
        pbar.set_postfix({"Best": current_best_score, "Last": score, "Sigma": sigma})
        
        if score >= 25:
            # Check for improvement
            if score > current_best_score:
                print(f"\nFOUND IMPROVEMENT: {score}")
                current_best_score = score
                current_best_lines = final_lines.copy()
                save_best(current_best_lines, current_best_score, f"record_{score}.json")
                if score >= 26: 
                    print("GOAL REACHED!")
                    break
            
            # Check distinctness for score 25
            elif score == 25:
                if is_distinct(final_lines, known_variants):
                    variant_count += 1
                    print(f"\nFound distinct variant #{variant_count} for Score 25 (Sigma={sigma})")
                    known_variants.append(final_lines.copy())
                    save_best(final_lines, 25, f"record_25_variant_{variant_count}.json")

    print("\nRefinement complete.")
    print(f"Final Score: {current_best_score}")
    print(f"Total Variants Found: {variant_count}")
    
    # Vis Best
    print("Visualizing best result...")
    solver = KobonSolver(current_best_lines)
    triangles = solver.find_triangles()
    plot_configuration(current_best_lines, triangles)

if __name__ == "__main__":
    refine()
