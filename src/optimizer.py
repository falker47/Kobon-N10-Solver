import numpy as np
import copy
from geometry import KobonSolver

class Optimizer:
    def __init__(self, n_lines=10):
        self.n_lines = n_lines
        # Random initialization
        # Lines: ax + by + c = 0
        # Random normal initialization
        self.state = np.random.randn(n_lines, 3)
        # Normalize a,b to unit vector for stability? Not strictly necessary but efficient.
        self.normalize_lines(self.state)

    def normalize_lines(self, lines):
        # Normalize (a,b) such that a^2 + b^2 = 1
        norms = np.linalg.norm(lines[:, :2], axis=1, keepdims=True)
        # Avoid zero division
        norms[norms < 1e-9] = 1.0
        
        # Normalize all components (a, b, c) by the norm of (a, b)
        # This keeps the geometric line identical but standardizes parameters
        lines /= norms

    def objective(self, lines):
        solver = KobonSolver(lines)
        triangles = solver.find_triangles()
        return len(triangles)

    def optimize(self, iterations=1000, T_start=1.0, T_end=0.001, verbose=False):
        current_state = self.state.copy()
        current_score = self.objective(current_state)
        
        best_state = current_state.copy()
        best_score = current_score
        
        if verbose:
            print(f"Initial Score: {current_score}")
        
        for i in range(iterations):
            # Exponential decay schedule
            # T(t) = T_start * (T_end/T_start) ^ (t/max_t)
            # This is equivalent to geometric decay T_{t+1} = T_t * alpha where alpha = (T_end/T_start)^(1/iterations)
            T = T_start * ((T_end / T_start) ** (i / iterations))
            
            # Perturb
            candidate_state = current_state + np.random.normal(0, 0.1 * T, size=current_state.shape)
            
            candidate_score = self.objective(candidate_state)
            
            delta = candidate_score - current_score
            
            if delta > 0 or np.random.rand() < np.exp(delta / T):
                current_state = candidate_state
                current_score = candidate_score
                
                if current_score > best_score:
                    best_score = current_score
                    best_state = current_state.copy()
                    if verbose:
                        print(f"Iter {i}: New Best! {best_score}")

        return best_state, best_score
