import json
import numpy as np
import copy
from tqdm import tqdm
from geometry import KobonSolver
from visualizer import plot_configuration

# --- Helper Functions ---

def load_variant(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    print(f"Loaded {filepath} with score {data['score']}")
    return np.array(data['lines'])

def normalize_single_line(line):
    # a^2 + b^2 = 1, first non-zero positive
    norm = np.linalg.norm(line[:2])
    if norm < 1e-9: return line
    line = line / norm
    
    if line[0] < -1e-9 or (abs(line[0]) < 1e-9 and line[1] < -1e-9):
        line *= -1
    return line

def get_reflected_line(line):
    # Reflect across Y-axis: x -> -x
    # ax + by + c = 0 -> a(-x) + by + c = 0 -> -ax + by + c = 0
    # So (a,b,c) -> (-a, b, c)
    a, b, c = line
    return np.array([-a, b, c])

def symmetrize_lines(lines):
    """
    Extract 5 master lines that best represent the symmetric version of the input 10 lines.
    Assumes nearly Y-axis symmetric input.
    """
    # 1. Normalize all inputs for comparison
    lines = np.array([normalize_single_line(l) for l in lines])
    
    # 2. Find Pairs
    # For each line, find best match used as reflection
    # We want to pair L_i with L_j such that L_i ~ Reflect(L_j)
    
    pairs = []
    used = [False] * len(lines)
    
    for i in range(len(lines)):
        if used[i]: continue
        
        target = get_reflected_line(lines[i])
        target = normalize_single_line(target) # Normalize valid form
        
        best_j = -1
        best_dist = 1e9
        
        for j in range(i + 1, len(lines)):
            if used[j]: continue
            
            # Compare lines[j] to target
            # Need to handle sign flip (line and -line are same)
            l_j = lines[j]
            d1 = np.linalg.norm(l_j - target)
            d2 = np.linalg.norm(l_j + target)
            dist = min(d1, d2)
            
            if dist < best_dist:
                best_dist = dist
                best_j = j
        
        # We assume they pair up. Even if distance is large, we force it.
        if best_j != -1:
            used[i] = True
            used[best_j] = True
            
            l1 = lines[i]
            l2 = lines[best_j]
            
            # Average them to get perfectly symmetric master
            # To average correctly, align signs
            ref_l2 = get_reflected_line(l2)
            # Try both signs of ref_l2 to match l1
            if np.linalg.norm(l1 - ref_l2) > np.linalg.norm(l1 + ref_l2):
                ref_l2 = -ref_l2
            
            master = (l1 + ref_l2) / 2.0
            master = normalize_single_line(master)
            pairs.append(master)
        else:
            # No pair found? (Odd number of lines or already used)
            # Should not happen for N=10 if symmetric
            pass
            
    if len(pairs) != 5:
        print(f"WARNING: Found {len(pairs)} pairs instead of 5. Filling with randoms or leftovers.")
        # Fallback: Just take first 5 lines
        return lines[:5]
        
    return np.array(pairs)

# --- Constrained Optimizer ---

class SymmetricOptimizer:
    def __init__(self, master_lines):
        self.master_lines = master_lines.copy()
        
    def get_full_state(self, master_lines=None):
        if master_lines is None: master_lines = self.master_lines
        
        full_lines = []
        for l in master_lines:
            full_lines.append(l)
            full_lines.append(get_reflected_line(l))
        return np.array(full_lines)
    
    def objective(self, master_lines):
        full_lines = self.get_full_state(master_lines)
        solver = KobonSolver(full_lines)
        triangles = solver.find_triangles()
        
        count = len(triangles)
        
        # Secondary: Area Variance
        # We want Regular triangles (similar areas) maybe?
        if count >= 20: # Only care if we have decent structure
            if len(triangles) > 0:
                # Calculate areas. 
                # KobonSolver doesn't return coordinates directly in find_triangles list usually
                # But let's assume we just want to break ties.
                # Actually, simply returning count is usually enough for discrete steps.
                # Let's add a tiny bonus for something... maybe spread?
                pass
        
        return count

    def optimize(self, steps=1000):
        current_master = self.master_lines.copy()
        current_score = self.objective(current_master)
        
        best_master = current_master.copy()
        best_score = current_score
        
        print(f"Initial Symmetric Score: {current_score}")
        
        # Annealing on 5 lines
        T = 0.5
        alpha = 0.995
        
        for i in tqdm(range(steps)):
            # Perturb
            noise = np.random.normal(0, 0.05 * T, size=current_master.shape)
            candidate = current_master + noise
            
            # Re-normalize
            for k in range(len(candidate)):
                candidate[k] = normalize_single_line(candidate[k])
                
            score = self.objective(candidate)
            
            if score > current_score or np.random.rand() < np.exp((score - current_score) / T):
                current_master = candidate
                current_score = score
                
                if score > best_score:
                    best_score = score
                    best_master = current_master.copy()
                    print(f"New Best Symmetric Score: {best_score}")
                    
            T *= alpha
            if T < 0.001: T = 0.001
            
        return best_master, best_score

def run_forced_symmetry():
    # Load
    # Assuming path relative to CWD
    target_file = "variants/record_25_variant_49.json"
    lines = load_variant(target_file)
    
    # Symmetrize
    print("Symmetrizing input lines...")
    master_lines = symmetrize_lines(lines)
    print(f"Extracted {len(master_lines)} master lines.")
    
    # Optimize
    opt = SymmetricOptimizer(master_lines)
    best_master, best_score = opt.optimize(steps=10000)
    
    print(f"Final Best Score with Forced Symmetry: {best_score}")
    
    # Save & Visualize
    full_lines = opt.get_full_state(best_master)
    
    out_file = "symmetric_result.json"
    with open(out_file, 'w') as f:
        json.dump({
            "score": best_score,
            "lines": full_lines.tolist()
        }, f, indent=4)
        
    print("Visualizing...")
    solver = KobonSolver(full_lines)
    triangles = solver.find_triangles()
    plot_configuration(full_lines, triangles)

if __name__ == "__main__":
    run_forced_symmetry()
