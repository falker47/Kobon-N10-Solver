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
    # a^2 + b^2 = 1
    norm = np.linalg.norm(line[:2])
    if norm < 1e-9: return line
    line = line / norm
    
    # Enforce sign convention for comparison: First non-zero positive
    if line[0] < -1e-9 or (abs(line[0]) < 1e-9 and line[1] < -1e-9):
        line *= -1
    return line

def get_reflected_line(line):
    # Reflect across Y-axis: (a,b,c) -> (-a, b, c)
    a, b, c = line
    return np.array([-a, b, c])

def detect_pairs(lines):
    """
    Automatically pair lines (Li, Lj) such that Li ~ Reflect(Lj).
    Returns list of indices (i, j).
    """
    normalized = np.array([normalize_single_line(l) for l in lines])
    used = [False] * len(lines)
    pairs = []
    
    for i in range(len(lines)):
        if used[i]: continue
        
        target = get_reflected_line(normalized[i])
        target = normalize_single_line(target)
        
        best_j = -1
        best_dist = 1e9
        
        for j in range(i, len(lines)): # Check self (i) too!
            if used[j] and j != i: continue # Can't reuse others, but check self
            if used[j]: continue
            
            # Distance metric: min(norm(u-v), norm(u+v))
            l_j = normalized[j]
            d1 = np.linalg.norm(l_j - target)
            d2 = np.linalg.norm(l_j + target)
            dist = min(d1, d2)
            
            if dist < best_dist:
                best_dist = dist
                best_j = j
        
        # Threshold? For now just take best match.
        # Self-reflection check: if best_j == i
        if best_j != -1:
            pairs.append((i, best_j))
            used[i] = True
            used[best_j] = True
            
    return pairs

def calculate_symmetry_error(lines, pairs):
    error = 0.0
    # Use normalized copies for error calculation to be scale invariant?
    # Or just use raw? The user said "Euclidean distance".
    # Raw lines might drift in scale? 
    # Let's normalize inside the loop for error calc to catch shape only.
    
    for i, j in pairs:
        l1 = normalize_single_line(lines[i].copy())
        l2 = normalize_single_line(lines[j].copy())
        
        ref_l1 = get_reflected_line(l1)
        # Normalize result again just in case
        ref_l1 = normalize_single_line(ref_l1)
        
        # Dist
        d1 = np.linalg.norm(ref_l1 - l2)
        d2 = np.linalg.norm(ref_l1 + l2)
        dist_sq = min(d1, d2)**2
        
        error += dist_sq
        
    return error

def calculate_energy(lines, pairs):
    # 1. Triangle Score
    solver = KobonSolver(lines)
    triangles = solver.find_triangles()
    score = len(triangles)
    
    # 2. Symmetry Error
    sym_error = calculate_symmetry_error(lines, pairs)
    
    # Energy: Minimize this
    # Large penalty for missing triangles
    # Small penalty for asymmetry
    energy = -(score * 1000) + (sym_error * 10)
    
    return energy, score, sym_error

def run_soft_symmetry():
    target_file = "variants/record_25_variant_49.json"
    current_lines = load_variant(target_file)
    n_lines = len(current_lines)
    
    print("Detecting Symmetry Pairs...")
    pairs = detect_pairs(current_lines)
    print(f"Pairs found: {pairs}")
    
    # Initial Energy
    current_energy, current_score, current_sym = calculate_energy(current_lines, pairs)
    print(f"Initial: Score={current_score}, SymError={current_sym:.4f}, Energy={current_energy:.4f}")
    
    best_lines = current_lines.copy()
    best_score = current_score
    best_sym_lines = current_lines.copy()
    best_combined_energy = current_energy
    
    # Annealing
    steps = 20000
    T_start = 1.0
    T_end = 0.001
    
    pbar = tqdm(range(steps))
    
    for k in pbar:
        T = T_start * ((T_end / T_start) ** (k / steps))
        
        # Pertub
        candidate = current_lines + np.random.normal(0, 0.02 * T, size=current_lines.shape)
        
        # Normalize geometry (a^2+b^2=1) but keep signs for now
        # Actually calculate_energy handles normalization internally for error, 
        # but we should normalize state to keep params bounded.
        for idx in range(n_lines):
            norm = np.linalg.norm(candidate[idx, :2])
            if norm > 1e-9:
                candidate[idx] /= norm
        
        new_energy, new_score, new_sym = calculate_energy(candidate, pairs)
        
        delta = new_energy - current_energy
        
        if delta < 0 or np.random.rand() < np.exp(-delta / T):
            current_lines = candidate
            current_energy = new_energy
            current_score = new_score
            
            # Update Bests
            if current_score > best_score:
                best_score = current_score
                best_lines = current_lines.copy()
                tqdm.write(f"NEW SCORE RECORD: {best_score} (SymErr: {new_sym:.4f})")
                
                with open(f"record_{best_score}_soft.json", "w") as f:
                    json.dump({"score": best_score, "lines": best_lines.tolist()}, f)
                
                if best_score >= 26:
                    print("GOAL 26 REACHED!")
                    break
            
            # Track best energy (best compromise)
            if current_energy < best_combined_energy:
                best_combined_energy = current_energy
                best_sym_lines = current_lines.copy()
    
    print("Optimization Complete.")
    print(f"Best Score: {best_score}")
    
    # Visualize the "Best Compromise" (Most symmetric 25 or 26)
    print("Visualizing Best Combined Result...")
    solver = KobonSolver(best_sym_lines)
    tris = solver.find_triangles()
    plot_configuration(best_sym_lines, tris)
    
    # Save final
    with open("soft_symmetry_final.json", "w") as f:
        json.dump({"score": len(tris), "lines": best_sym_lines.tolist()}, f, indent=4)

if __name__ == "__main__":
    run_soft_symmetry()
