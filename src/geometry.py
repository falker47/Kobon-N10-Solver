import numpy as np
from itertools import combinations

class KobonSolver:
    def __init__(self, lines):
        """
        lines: (N, 3) numpy array representing lines ax + by + c = 0
        """
        self.lines = lines
        self.n_lines = len(lines)

    def compute_intersections(self):
        """
        Compute all pairwise intersections.
        Returns:
            points: (N, N, 2) array where points[i, j] is intersection of Line i and Line j.
                    (N, N) mask indicating if intersection exists (parallel lines have none).
        """
        # Cross product in homogeneous coordinates
        # L_i = (a1, b1, c1), L_j = (a2, b2, c2)
        # P = L_i x L_j = (x', y', w')
        # Cartesian: (x'/w', y'/w')
        
        # We need N x N cross products.
        # Broadcast: (N, 1, 3) x (1, N, 3) -> (N, N, 3)
        l1 = self.lines[:, np.newaxis, :]
        l2 = self.lines[np.newaxis, :, :]
        
        # Manual cross product for clarity and guaranteed broadcasting
        # L1: (N, 1, 3) -> a1, b1, c1
        a1 = l1[:, :, 0]
        b1 = l1[:, :, 1]
        c1 = l1[:, :, 2]
        
        # L2: (1, N, 3) -> a2, b2, c2
        a2 = l2[:, :, 0]
        b2 = l2[:, :, 1]
        c2 = l2[:, :, 2]
        
        # Cross product
        # x = b1*c2 - c1*b2
        # y = c1*a2 - a1*c2
        # w = a1*b2 - b1*a2
        
        x_homo = b1 * c2 - c1 * b2
        y_homo = c1 * a2 - a1 * c2
        w = a1 * b2 - b1 * a2
        
        cross_prod = np.stack([x_homo, y_homo, w], axis=2)
        
        # Parallel lines have w near 0
        valid_mask = np.abs(w) > 1e-10
        
        # Identify diagonals (i==j) to ignore
        idx = np.arange(self.n_lines)
        valid_mask[idx, idx] = False
        
        # Calculate coordinates
        # Avoid division by zero where w is small; result will be ignored by mask anyway
        x_homo = cross_prod[:, :, 0]
        y_homo = cross_prod[:, :, 1]
        
        # Initialize points array
        points = np.zeros((self.n_lines, self.n_lines, 2))
        
        # Safe division
        safe_w = np.where(valid_mask, w, 1.0)
        
        # Debugging shapes
        # print(f"points shape: {points.shape}")
        # print(f"x_homo shape: {x_homo.shape}")
        # print(f"safe_w shape: {safe_w.shape}")
        # print(f"x_homo/safe_w shape: {(x_homo/safe_w).shape}")
        
        points[:, :, 0] = x_homo / safe_w
        points[:, :, 1] = y_homo / safe_w
        
        return points, valid_mask

    def find_triangles(self):
        """
        Identify valid triangles formed by the lines.
        Returns: 
            List of tuples (i, j, k) representing line indices of valid triangles.
        """
        points, valid_intersections = self.compute_intersections()
        triangles = []
        
        # Check all combinations of 3 lines
        for i, j, k in combinations(range(self.n_lines), 3):
            # Check if all pairs intersect (not parallel)
            if not (valid_intersections[i, j] and valid_intersections[j, k] and valid_intersections[k, i]):
                continue
                
            # Get vertices
            v1 = points[i, j]
            v2 = points[j, k]
            v3 = points[k, i]
            
            # Check if vertices are distinct (not concurrent 3 lines)
            # 3 lines concurrent if determinant |Li, Lj, Lk| = 0
            if np.linalg.norm(v1 - v2) < 1e-6 or np.linalg.norm(v2 - v3) < 1e-6 or np.linalg.norm(v3 - v1) < 1e-6:
                continue
            
            
            if self.is_valid_triangle(i, j, k, v1, v2, v3):
                # Normalize indices sort
                triangles.append(tuple(sorted((i, j, k))))
                
        return triangles

    def is_valid_triangle(self, i, j, k, v1, v2, v3):
        """
        Kobon Condition: Triangle is valid iff NO other line passes through it.
        Equivalent to: For all other lines m, m does not separate vertices.
        Separation check: Sign of (ax+by+c) for vertices.
        If line m passes through, signs will differ.
        If line m doesn't pass through, all vertices have same sign (or 0).
        """
        
        # Create a mask for lines other than i, j, k
        mask = np.ones(self.n_lines, dtype=bool)
        mask[[i, j, k]] = False
        other_lines = self.lines[mask]
        
        if len(other_lines) == 0:
            return True
            
        # Vertices: (3, 2)
        verts = np.stack([v1, v2, v3])
        
        # Evaluate other lines at vertices
        # Lines: (L-3, 3) (a,b,c)
        # Verts (homogenous): (3, 3) (x, y, 1)
        
        verts_h = np.column_stack((verts, np.ones(3))) # 3 x 3
        
        # Result: (L-3, 3) matrix of values
        # value[m, v] = value of line m at vertex v
        evals = other_lines @ verts_h.T
        
        # Check signs
        # eps tolerance for numerical stability
        eps = 1e-9
        
        # A line intersects the triangle if signs are strictly mixed (ignoring zeros/on-line)
        # However, for rigorous Kobon, we usually care if it passes through the INTERIOR.
        # If a line touches a vertex, it doesn't invalidate the triangle (usually).
        # Assuming "Interior" check:
        # Line cuts interior if specific vertex signs are strictly positive and others strictly negative.
        
        # Logic: A line misses the triangle if all evaluations are >= -eps OR all are <= eps.
        # Conversely, it Hits if min < -eps AND max > eps.
        
        min_vals = np.min(evals, axis=1)
        max_vals = np.max(evals, axis=1)
        
        # If any line has (min < -eps and max > eps), it cuts the triangle
        cuts = (min_vals < -eps) & (max_vals > eps)
        
        # If any line cuts, it's invalid
        if np.any(cuts):
            return False
            
        return True
