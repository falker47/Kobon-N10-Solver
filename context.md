# Project: Kobon Triangle Solver (Computational Geometry)

## 1. Objective
Develop a Python-based engine to search for the maximum number of non-overlapping triangles (Kobon Triangles) formed by $N$ lines in a plane.
- **Target:** Find the configuration for $N=10$ that yields 26 triangles (current record is 25).
- **Constraint:** Code must run on a standard consumer CPU (efficient NumPy vectorization required).

## 2. Mathematical Definitions
- **Line:** Defined by $ax + by + c = 0$.
- **Triangle:** Formed by 3 lines $(L_i, L_j, L_k)$ intersecting at 3 distinct points.
- **Kobon Condition (Validity):** A triangle is valid (non-overlapping) if and only if NO other line $L_m$ passes through the interior of the triangle formed by $(L_i, L_j, L_k)$.
- **Interior Check:** If a line $L_m$ separates any two vertices of the triangle, it intersects the interior. Algebraic check: if the sign of $L_m(x,y)$ is not constant for all 3 vertices, the line cuts the triangle.

## 3. Tech Stack & Style
- **Language:** Python 3.10+
- **Libraries:** `numpy` (heavy linear algebra usage), `matplotlib` (for visualizing the resulting configuration).
- **Style:** Functional or OOP. Type hinting is mandatory.
- **Performance:** Avoid nested Python loops where NumPy broadcasting can be used.

## 4. Architecture Plan
1.  **Geometry Engine:** A class to handle lines, calculate intersection points ($N \times N$ matrix), and validate triangles.
2.  **Optimizer:** A search algorithm (Hill Climbing, Simulated Annealing, or Genetic Algorithm) to perturb line parameters $(a, b, c)$ slightly to increase the triangle count.
3.  **Visualizer:** A function to plot the lines and highlight the valid triangles found.

## 5. User Constraints
- "Zero-Fluff" approach. Code must be dense and direct.
- No heavy frameworks. Keep it lightweight.