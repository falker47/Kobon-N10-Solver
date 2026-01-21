import json
import numpy as np

def analyze():
    with open('record_25.json', 'r') as f:
        data = json.load(f)
    
    lines = np.array(data['lines'])
    # lines shape (N, 3) (a, b, c)
    
    print("Parameter Statistics:")
    
    # Calculate mean absolute value for each component type
    mean_abs_params = np.mean(np.abs(lines), axis=0)
    overall_mean_abs = np.mean(np.abs(lines))
    
    print(f"Mean Abs a: {mean_abs_params[0]:.4f}")
    print(f"Mean Abs b: {mean_abs_params[1]:.4f}")
    print(f"Mean Abs c: {mean_abs_params[2]:.4f}")
    print(f"Overall Mean Abs Parameter: {overall_mean_abs:.4f}")
    
    sigma = 0.01
    relative_change = (sigma / overall_mean_abs) * 100
    
    print(f"\nCurrent Sigma: {sigma}")
    print(f"Approximate Relative Perturbation: {relative_change:.2f}%")
    
    # Check norms of (a,b)
    norms = np.linalg.norm(lines[:, :2], axis=1)
    print(f"\nMean Norm(a,b): {np.mean(norms):.4f}")
    
    # If lines are normalized such that a^2+b^2=1 (which they should be roughly if optimize was run)
    # Then sigma=0.01 on a unit vector is ~1% rotation/length change.
    # But let's check c separately.
    
    mean_abs_c = np.mean(np.abs(lines[:, 2]))
    rel_change_c = (sigma / mean_abs_c) * 100
    print(f"Relative Perturbation on C (Intercept): {rel_change_c:.2f}%")

if __name__ == "__main__":
    analyze()
