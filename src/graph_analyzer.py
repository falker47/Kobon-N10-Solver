"""
Graph Analyzer for Kobon Triangle Configurations

Computes intersection graphs and canonical hashes for topological equivalence
classification. Addresses the methodological weakness of parameter-space clustering.
"""

import numpy as np
import json
import glob
from collections import defaultdict
from itertools import combinations

try:
    import networkx as nx
    from networkx.algorithms.graph_hashing import weisfeiler_lehman_graph_hash
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("WARNING: networkx not installed. Install with: pip install networkx")


def compute_intersections(lines):
    """
    Compute all pairwise intersection points.
    
    Args:
        lines: (N, 3) numpy array representing lines ax + by + c = 0
        
    Returns:
        points: (N, N, 2) array of intersection coordinates
        valid: (N, N) boolean mask for valid (non-parallel) intersections
    """
    n = len(lines)
    a = lines[:, 0]
    b = lines[:, 1]
    c = lines[:, 2]
    
    # Compute denominator for all pairs
    denom = a[:, None] * b[None, :] - a[None, :] * b[:, None]
    
    # Valid if not parallel (denom != 0)
    valid = np.abs(denom) > 1e-10
    np.fill_diagonal(valid, False)  # Exclude self-intersections
    
    # Compute intersection points
    safe_denom = np.where(valid, denom, 1.0)
    x = (b[:, None] * c[None, :] - b[None, :] * c[:, None]) / safe_denom
    y = (a[None, :] * c[:, None] - a[:, None] * c[None, :]) / safe_denom
    
    points = np.zeros((n, n, 2))
    points[:, :, 0] = x
    points[:, :, 1] = y
    
    return points, valid


def extract_intersection_graph(lines):
    """
    Build the intersection graph from a line arrangement.
    
    The intersection graph has:
    - Nodes: intersection points (labeled by line pair (i,j) where i < j)
    - Edges: line segments connecting adjacent intersections on each line
    
    Additionally stores which triangles are valid (Kobon triangles).
    
    Returns:
        G: networkx.Graph with node attributes including 'line_pair'
        triangle_set: set of frozensets representing valid triangles
    """
    if not HAS_NETWORKX:
        raise ImportError("networkx required for graph analysis")
    
    n = len(lines)
    points, valid = compute_intersections(lines)
    
    G = nx.Graph()
    
    # Create nodes for each intersection point
    # Node ID: tuple (i, j) with i < j
    for i in range(n):
        for j in range(i + 1, n):
            if valid[i, j]:
                node_id = (i, j)
                G.add_node(node_id, line_pair=(i, j), pos=tuple(points[i, j]))
    
    # Create edges: connect adjacent intersections along each line
    for line_idx in range(n):
        # Get all intersections on this line
        intersections = []
        for other in range(n):
            if other != line_idx and valid[min(line_idx, other), max(line_idx, other)]:
                i, j = min(line_idx, other), max(line_idx, other)
                pt = points[i, j]
                intersections.append((other, pt, (i, j)))
        
        if len(intersections) < 2:
            continue
            
        # Sort by position along the line
        # Project onto line direction vector (b, -a)
        a, b, c = lines[line_idx]
        direction = np.array([b, -a])  # perpendicular to normal
        
        def project(item):
            return np.dot(item[1], direction)
        
        intersections.sort(key=project)
        
        # Connect adjacent pairs
        for k in range(len(intersections) - 1):
            node1 = intersections[k][2]
            node2 = intersections[k + 1][2]
            G.add_edge(node1, node2, line=line_idx)
    
    # Find valid triangles
    triangle_set = set()
    for i, j, k in combinations(range(n), 3):
        if not (valid[i, j] and valid[j, k] and valid[i, k]):
            continue
        
        v1 = points[i, j]
        v2 = points[j, k]
        v3 = points[i, k]
        
        # Check for concurrent lines
        if (np.linalg.norm(v1 - v2) < 1e-6 or 
            np.linalg.norm(v2 - v3) < 1e-6 or 
            np.linalg.norm(v3 - v1) < 1e-6):
            continue
        
        # Check if any other line cuts through the triangle
        is_valid = True
        verts = np.array([v1, v2, v3])
        verts_h = np.column_stack((verts, np.ones(3)))
        
        for m in range(n):
            if m in (i, j, k):
                continue
            evals = lines[m] @ verts_h.T
            if np.min(evals) < -1e-9 and np.max(evals) > 1e-9:
                is_valid = False
                break
        
        if is_valid:
            triangle_set.add(frozenset([i, j, k]))
    
    return G, triangle_set


def canonical_hash(G, triangle_set=None):
    """
    Compute a canonical hash for graph isomorphism comparison.
    
    Uses Weisfeiler-Lehman graph hashing which captures local structure.
    Also incorporates triangle count as a primary discriminator.
    """
    if not HAS_NETWORKX:
        raise ImportError("networkx required for graph analysis")
    
    # Primary: triangle count (different counts = definitely not isomorphic)
    n_triangles = len(triangle_set) if triangle_set else 0
    
    # Secondary: WL hash of the intersection graph structure
    # Note: We use edge count as node attribute to capture degree info
    for node in G.nodes():
        G.nodes[node]['degree'] = G.degree(node)
    
    wl_hash = weisfeiler_lehman_graph_hash(G, node_attr='degree', iterations=3)
    
    return f"{n_triangles}_{wl_hash}"


def load_configuration(filepath):
    """Load a configuration from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return np.array(data['lines'])


def classify_configurations(solution_dir="solutions"):
    """
    Classify all configurations by topological equivalence.
    
    Returns:
        families: dict mapping canonical_hash -> list of filenames
        stats: dict with summary statistics
    """
    if not HAS_NETWORKX:
        raise ImportError("networkx required for classification")
    
    files = glob.glob(f"{solution_dir}/variant*.json")
    print(f"Found {len(files)} configuration files")
    
    families = defaultdict(list)
    errors = []
    
    for filepath in files:
        try:
            lines = load_configuration(filepath)
            G, triangles = extract_intersection_graph(lines)
            hash_val = canonical_hash(G, triangles)
            families[hash_val].append(filepath)
        except Exception as e:
            errors.append((filepath, str(e)))
            print(f"[ERROR] {filepath}: {e}")
    
    # Sort families by size
    sorted_families = sorted(families.items(), key=lambda x: -len(x[1]))
    
    stats = {
        'total_files': len(files),
        'unique_graphs': len(families),
        'largest_family': max(len(v) for v in families.values()) if families else 0,
        'singletons': sum(1 for v in families.values() if len(v) == 1),
        'errors': len(errors)
    }
    
    return dict(sorted_families), stats


def print_classification_report(families, stats):
    """Print a formatted report of the classification results."""
    print("\n" + "=" * 60)
    print("TOPOLOGICAL CLASSIFICATION REPORT")
    print("=" * 60)
    print(f"\nTotal configurations analyzed: {stats['total_files']}")
    print(f"Topologically distinct graphs: {stats['unique_graphs']}")
    print(f"Largest equivalence class:     {stats['largest_family']} members")
    print(f"Singleton configurations:      {stats['singletons']}")
    print(f"Errors:                        {stats['errors']}")
    
    print("\n" + "-" * 60)
    print("EQUIVALENCE CLASSES (by size)")
    print("-" * 60)
    
    for idx, (hash_val, members) in enumerate(families.items(), 1):
        n_tri = hash_val.split('_')[0]
        print(f"\nClass #{idx} ({len(members)} members, {n_tri} triangles):")
        for m in members[:5]:  # Show first 5
            print(f"  - {m}")
        if len(members) > 5:
            print(f"  ... and {len(members) - 5} more")


def test_hash_consistency():
    """
    Test that the hash is invariant under geometric transformations
    that preserve the intersection graph (rotation, translation, scaling).
    """
    print("Testing hash consistency under transformations...")
    
    # Create a simple test configuration
    test_lines = np.array([
        [1.0, 0.0, -1.0],   # x = 1
        [0.0, 1.0, -1.0],   # y = 1
        [1.0, 1.0, -3.0],   # x + y = 3
    ])
    
    G1, tri1 = extract_intersection_graph(test_lines)
    hash1 = canonical_hash(G1, tri1)
    
    # Apply rotation (45 degrees)
    theta = np.pi / 4
    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])
    
    rotated_lines = test_lines.copy()
    for i in range(len(test_lines)):
        a, b, c = test_lines[i]
        normal = np.array([a, b])
        new_normal = R @ normal
        rotated_lines[i, :2] = new_normal
        # c stays same for rotation around origin
    
    G2, tri2 = extract_intersection_graph(rotated_lines)
    hash2 = canonical_hash(G2, tri2)
    
    print(f"Original hash:  {hash1}")
    print(f"Rotated hash:   {hash2}")
    print(f"Hashes match:   {hash1 == hash2}")
    
    return hash1 == hash2


if __name__ == "__main__":
    import os
    
    # Change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))
    
    print("Kobon Triangle Topological Analyzer")
    print("=" * 40)
    
    # Run classification
    families, stats = classify_configurations("solutions")
    print_classification_report(families, stats)
