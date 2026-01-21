import matplotlib.pyplot as plt
import numpy as np
from geometry import KobonSolver

def plot_configuration(lines, triangles):
    """
    Plots the lines and highlights valid triangles.
    lines: (N, 3) array
    triangles: List of tuples (i, j, k)
    """
    solver = KobonSolver(lines)
    points, mask = solver.compute_intersections()
    
    plt.figure(figsize=(10, 10))
    
    # Determine bounds based on intersections
    # Filter points that are actually used in logic
    valid_points = points[mask]
    if len(valid_points) > 0:
        x_min, x_max = valid_points[:, 0].min(), valid_points[:, 0].max()
        y_min, y_max = valid_points[:, 1].min(), valid_points[:, 1].max()
        
        margin = max(x_max - x_min, y_max - y_min) * 0.1
        x_lim = (x_min - margin, x_max + margin)
        y_lim = (y_min - margin, y_max + margin)
    else:
        x_lim = (-10, 10)
        y_lim = (-10, 10)
        
    plt.xlim(x_lim)
    plt.ylim(y_lim)
    
    # Plot Lines
    # Clip lines to view
    
    # Create grid of x values to plot lines
    x_vals = np.array(x_lim)
    
    for a, b, c in lines:
        if abs(b) > 1e-6:
            y_vals = (-a * x_vals - c) / b
            plt.plot(x_vals, y_vals, 'k-', linewidth=1, alpha=0.5)
        else:
            # Vertical line x = -c/a
            if abs(a) > 1e-6:
                x_v = -c / a
                plt.axvline(x_v, color='k', linewidth=1, alpha=0.5)
    
    # Highlight Triangles
    # Use distinct colors
    cmap = plt.get_cmap('viridis')
    
    for idx, (i, j, k) in enumerate(triangles):
        # Get vertices
        p1 = points[i, j]
        p2 = points[j, k]
        p3 = points[k, i]
        
        poly = np.stack([p1, p2, p3])
        
        color = cmap(idx / max(1, len(triangles)))
        t_poly = plt.Polygon(poly, facecolor=color, alpha=0.5, edgecolor='none')
        plt.gca().add_patch(t_poly)
        
        # Centroid for label
        centroid = np.mean(poly, axis=0)
        plt.text(centroid[0], centroid[1], str(idx+1), fontsize=8, ha='center', va='center', color='black')
        
    plt.title(f"Kobon Triangles: {len(triangles)} found")
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.savefig('kobon_result.png')
    print("Result saved to kobon_result.png")
    # plt.show()
