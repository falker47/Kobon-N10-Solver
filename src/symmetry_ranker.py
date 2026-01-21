import glob
import json
import numpy as np
import matplotlib.pyplot as plt
# from scipy.spatial import KDTree 
# Removed scipy dependency
from geometry import KobonSolver

def get_intersection_points(lines):
    solver = KobonSolver(lines)
    # This returns (N,N,2) and mask
    raw_points, mask = solver.compute_intersections()
    # Flatten
    points = raw_points[mask]
    return points

def normalize_points(points):
    """
    Center points at (0,0) and scale so mean distance to origin is 1.
    """
    centroid = np.mean(points, axis=0)
    points_centered = points - centroid
    
    mean_dist = np.mean(np.linalg.norm(points_centered, axis=1))
    if mean_dist < 1e-9: mean_dist = 1.0 # fallback
    
    return points_centered / mean_dist, centroid, mean_dist

def compute_symmetry_error(points, transform_fn):
    """
    Compute average distance between transformed points and nearest original points.
    Using Numpy broadcasting for N^2 distance matrix.
    """
    transformed = transform_fn(points)
    
    # Points: (N, 2)
    # Transformed: (N, 2)
    
    # Broadcasting: (N, 1, 2) - (1, N, 2) -> (N, N, 2)
    diffs = transformed[:, np.newaxis, :] - points[np.newaxis, :, :]
    
    # Distance matrix (N, N)
    dists = np.linalg.norm(diffs, axis=2)
    
    # For each transformed point, find min dist to any original point
    min_dists = np.min(dists, axis=1)
    
    # We want low mean error
    return np.mean(min_dists)

def rank_symmetries():
    files = glob.glob("variants/record_25*.json")
    if not files:
        print("No variants found in variants/")
        return

    results = []

    print(f"Analyzing {len(files)} variants for symmetry...")

    for fpath in files:
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            lines = np.array(data['lines'])
            
            points = get_intersection_points(lines)
            if len(points) == 0:
                continue
                
            norm_points, _, _ = normalize_points(points)
            
            # --- Define Symmetries to Test ---
            scores = {}
            
            # 1. Rotational 72 deg (C5)
            theta = 2 * np.pi / 5
            c, s = np.cos(theta), np.sin(theta)
            rot_matrix = np.array([[c, -s], [s, c]])
            scores['Rot_72'] = compute_symmetry_error(norm_points, lambda p: p @ rot_matrix.T)
            
            # 1b. Rotational 180 deg (C2)
            scores['Rot_180'] = compute_symmetry_error(norm_points, lambda p: -p)
            
            # 2. Axial X (Reflection across Y-axis, i.e., x -> -x)
            scores['Ref_Y_Axis'] = compute_symmetry_error(norm_points, lambda p: p * [-1, 1])
            
            # 3. Axial Y (Reflection across X-axis, i.e., y -> -y)
            scores['Ref_X_Axis'] = compute_symmetry_error(norm_points, lambda p: p * [1, -1])
            
            # 4. Diagonal y=x (swap x,y)
            scores['Ref_Diag_POS'] = compute_symmetry_error(norm_points, lambda p: p[:, [1, 0]])

             # 5. Diagonal y=-x (swap x,y and negate both?) -> (-y, -x)
            scores['Ref_Diag_NEG'] = compute_symmetry_error(norm_points, lambda p: -p[:, [1, 0]])

            
            # Best score implies the geometry *has* that symmetry
            best_sym_name = min(scores, key=scores.get)
            best_sym_score = scores[best_sym_name]
            
            results.append({
                'file': fpath,
                'best_sym_name': best_sym_name,
                'score': best_sym_score,
                'all_scores': scores
            })

        except Exception as e:
            print(f"Error processing {fpath}: {e}")

    # Sort by Score (Lower is better)
    results.sort(key=lambda x: x['score'])
    
    print("\n--- Top 5 Most Symmetric Variants ---")
    print(f"{'Rank':<5} {'File':<40} {'Symmetry':<15} {'Score (Error)':<15}")
    print("-" * 80)
    
    for i, res in enumerate(results[:5]):
        fname = res['file'].replace("variants\\", "").replace("variants/", "")
        print(f"{i+1:<5} {fname:<40} {res['best_sym_name']:<15} {res['score']:.5f}")
        
    # Visualize #1
    if results:
        best = results[0]
        print(f"\nVisualizing best variant: {best['file']} ({best['best_sym_name']})")
        visualize_symmetry(best['file'], best['best_sym_name'])

def visualize_symmetry(filename, sym_name):
    with open(filename, 'r') as f:
        data = json.load(f)
    lines = np.array(data['lines'])
    
    # Recalculate normalization info for plotting center
    points = get_intersection_points(lines)
    _, centroid, _ = normalize_points(points)
    
    plt.figure(figsize=(8, 8))
    
    # Plot Lines
    x_lim = (-10, 10)
    x_vals = np.array(x_lim)
    for a, b, c in lines:
        if abs(b) > 1e-6:
            y_vals = (-a * x_vals - c) / b
            plt.plot(x_vals, y_vals, 'k-', linewidth=1)
        else:
            if abs(a) > 1e-6:
                x_v = -c / a
                plt.axvline(x_v, color='k', linewidth=1)
                
    # Overlay Symmetry Axis/Center
    if 'Rot' in sym_name:
        # Plot center
        plt.plot(centroid[0], centroid[1], 'ro', markersize=10, label='Rotation Center')
    elif 'Ref' in sym_name:
        # Plot Axis relative to centroid
        cx, cy = centroid
        if sym_name == 'Ref_Y_Axis': # x -> -x relative to center? No, my math was origin relative normalized
            # The calculation was on centered points.
            # So axis passes through centroid.
            plt.axvline(cx, color='r', linestyle='--', linewidth=2, label='Reflection Axis')
        elif sym_name == 'Ref_X_Axis':
            plt.axhline(cy, color='r', linestyle='--', linewidth=2, label='Reflection Axis')
        elif sym_name == 'Ref_Diag_POS': # y-cy = x-cx
            plt.plot(x_vals, x_vals - cx + cy, 'r--', linewidth=2, label='Reflection Axis')
        elif sym_name == 'Ref_Diag_NEG': # y-cy = -(x-cx)
            plt.plot(x_vals, -(x_vals - cx) + cy, 'r--', linewidth=2, label='Reflection Axis')

    plt.title(f"Best Symmetric Candidate\n{filename}\n(Symmetry: {sym_name})")
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.gca().set_aspect('equal')
    plt.legend()
    plt.savefig('most_symmetric_kobon.png')
    print("Saved visualization to most_symmetric_kobon.png")

if __name__ == "__main__":
    rank_symmetries()
