import glob
import json
import numpy as np
from geometry import KobonSolver

def save_report(report_text):
    with open("analysis_report_utf8.txt", "w", encoding="utf-8") as f:
        f.write(report_text)


def normalize_and_sort(lines):
    """
    Canonicalize the lines for comparison.
    1. Normalize ax+by+c=0 such that a^2+b^2=1.
    2. Enforce sign convention: first non-zero component of (a,b) must be positive.
    3. Sort lines by (a, b, c).
    """
    lines = lines.copy()
    
    # 1. Normalize Vector
    norms = np.linalg.norm(lines[:, :2], axis=1, keepdims=True)
    # Avoid div by zero
    norms[norms < 1e-9] = 1.0
    lines = lines / norms
    
    # 2. Enforce Sign
    # We want a deterministic sign.
    # Rule: If a < 0, flip. If a == 0 and b < 0, flip.
    
    neg_a = lines[:, 0] < -1e-9
    zero_a = np.abs(lines[:, 0]) < 1e-9
    neg_b = lines[:, 1] < -1e-9
    
    flip_mask = neg_a | (zero_a & neg_b)
    
    lines[flip_mask] *= -1
    
    # 3. Sort
    # Sort by a, then b, then c
    ind = np.lexsort((lines[:, 2], lines[:, 1], lines[:, 0]))
    return lines[ind]

def load_and_verify():
    files = glob.glob("variants/record_25*.json")
    print(f"Found {len(files)} files to analyze.")
    
    valid_configs = []
    
    for fpath in files:
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            
            lines = np.array(data['lines'])
            
            # Verify Score
            solver = KobonSolver(lines)
            triangles = solver.find_triangles()
            score = len(triangles)
            
            if score < 25:
                print(f"[FAKE] {fpath}: Score is {score}, expected 25+")
            else:
                # Store
                canon_lines = normalize_and_sort(lines)
                valid_configs.append({
                    "file": fpath,
                    "lines": lines,      # Original
                    "canon": canon_lines # Canonical
                })
                # print(f"[OK] {fpath}: Score {score}")
                
        except Exception as e:
            print(f"[ERROR] {fpath}: {e}")
            
    return valid_configs

def analyze_families(configs):
    if not configs:
        print("No valid configurations found.")
        return

    output = []
    families = []
    # Each family is a list of config indices
    
    assigned = [False] * len(configs)
    
    output.append("\n--- Geometric Analysis ---")
    
    for i in range(len(configs)):
        if assigned[i]:
            continue
            
        # Start a new family
        current_family = [configs[i]['file']]
        assigned[i] = True
        
        root_canon = configs[i]['canon']
        
        for j in range(i + 1, len(configs)):
            if assigned[j]:
                continue
            
            target_canon = configs[j]['canon']
            
            # Calculate distance
            # Mean Absolute Error between sorted lines
            diff = np.abs(root_canon - target_canon)
            mae = np.mean(diff)
            
            # Threshold for "CLONE"
            if mae < 0.05:
                current_family.append(configs[j]['file'])
                assigned[j] = True
        
        families.append(current_family)

    output.append(f"\nTotal Unique Geometric Families: {len(families)}")
    for idx, fam in enumerate(families):
        output.append(f"\nFamily #{idx+1} ({len(fam)} members):")
        for member in fam:
            output.append(f"  - {member}")

    report = "\n".join(output)
    print(report)
    save_report(report)

if __name__ == "__main__":
    configs = load_and_verify()
    analyze_families(configs)
