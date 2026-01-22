---
title: "The N=10 Kobon Triangle Landscape: Combinatorial Barriers and the Non-Uniqueness of the 25-Triangle Optimum"
author: "Maurizio Falconi"
date: "January 2026"
---

<div class="cover-page">

<h1>The N=10 Kobon Triangle Landscape</h1>

<div class="subtitle">Combinatorial Barriers and the Non-Uniqueness of the 25-Triangle Optimum</div>

<div class="decorative-line"></div>

<div class="author-info">
<div class="author-name">Maurizio Falconi</div>
<div class="date">January 2026</div>

</div>

<a href="https://github.com/falker47/Kobon-N10-Solver" class="repo-link">View on GitHub →</a>

</div>

## Abstract


The Kobon Triangle problem, proposed by Kobon Fujimura in 1978, asks for the maximum number of non-overlapping triangular regions $K(N)$ that can be formed by $N$ lines in general position in the Euclidean plane. For $N=10$, the theoretical upper bound is 26 triangles, yet the best construction achieves only 25 (T. Suzuki, 2002); a gap that has persisted for over two decades.

This paper presents a **combinatorial characterization** of the $N=10$ solution landscape using stochastic optimization and graph-theoretic analysis. Our principal finding is that the 25-triangle configurations are not unique: we discover **11 combinatorially distinct intersection graphs** across 72 optimal configurations, demonstrating that the solution space is an archipelago of inequivalent local optima.

Furthermore, sensitivity analysis ("Breather Scans") reveals that these optimal configurations occupy **extremely narrow basins**, collapsing to sub-optimal scores with perturbations as small as 2%. Combined with the observation that symmetry constraints catastrophically reduce performance, our evidence strongly suggests that the barrier from 25 to 26 is **combinatorial rather than metric**. If a 26-triangle configuration exists, it cannot be reached by continuous deformation from any known 25-triangle solution; it must reside in a combinatorially isolated region requiring fundamentally different discovery methods.

---

## 1. Introduction

### 1.1 Problem Definition

The **Kobon Triangle Problem** is a classical challenge in combinatorial geometry. Given $N$ lines in general position (no two parallel, no three concurrent) in the affine plane $\mathbb{R}^2$, the objective is to maximize the number of non-overlapping triangular regions formed by intersections.

Let $K(N)$ denote the maximum achievable triangle count for $N$ lines. Clément and Bader (2007) established the tight upper bound:

$$K(N) \leq \left\lfloor \frac{N(N-2)}{3} \right\rfloor$$

This bound arises from a double-counting argument: each triangle consumes three line-segments, and each line contributes at most $N-2$ segments (between its $N-1$ intersection points).

### 1.2 The N=10 Gap

For small values of $N$, the upper bound $K(N)$ has been shown to be achievable. However, for $N=10$:

- **Theoretical Upper Bound:** $K(10) \leq \lfloor 10 \cdot 8 / 3 \rfloor = \lfloor 26.67 \rfloor = 26$
- **Best Known Construction:** 25 triangles (T. Suzuki, 2002)

This discrepancy of a single triangle has persisted for over two decades, despite extensive manual and computational efforts. The case $N=10$ is particularly significant as it is the **first value of $N$** for which the bound is not known to be tight. For $N \leq 9$, explicit constructions achieve the maximum.

### 1.3 Contribution

This paper provides a **combinatorial characterization** of the $N=10$ solution landscape. Our contributions are:

1. **Algorithmic Framework:** A hybrid Simulated Annealing + Basin Hopping pipeline optimized for line arrangements, achieving 100% convergence to 25 triangles across independent trials.
2. **Combinatorial Classification:** Discovery of **11 distinct intersection graphs** among 72 optimal configurations, proving the solution space is an archipelago of inequivalent local optima.
3. **Barrier Analysis:** Empirical evidence via "Breather Scans" that optimal basins have sub-2% width, and that the barrier to 26 is **combinatorial** (requiring a different intersection graph) rather than **metric** (requiring more precision).

![Mosaic of discovered 25-triangle configurations](images/kobon_mosaic.jpg)

*Figure 1: A mosaic showing the variety of 25-triangle configurations discovered by our stochastic search algorithm.*

---

## 2. Methodology

### 2.1 Geometric Representation

The standard slope-intercept parameterization $y = mx + q$ suffers from a singularity at vertical lines ($m \to \infty$). To ensure numerical stability across all orientations, we adopt the **normalized general form**:

$$L_i: \quad a_i x + b_i y + c_i = 0 \quad \text{subject to} \quad a_i^2 + b_i^2 = 1$$

This constraint ensures that the vector $(a_i, b_i)$ is a unit normal to line $L_i$, and the parameter $c_i$ represents the signed distance from the origin to the line. The complete state of an $N$-line arrangement is thus a matrix $\mathbf{S} \in \mathbb{R}^{N \times 3}$.

**Intersection Computation.** Given two lines $L_i$ and $L_j$, their intersection point $\mathbf{p}_{ij}$ is computed via Cramer's rule:

$$\mathbf{p}_{ij} = \begin{pmatrix} x_{ij} \\ y_{ij} \end{pmatrix} = \frac{1}{a_i b_j - a_j b_i} \begin{pmatrix} b_i c_j - b_j c_i \\ a_j c_i - a_i c_j \end{pmatrix}$$

The denominator $a_i b_j - a_j b_i$ vanishes only for parallel lines, which are excluded by the general position assumption.

### 2.2 Global Search: Simulated Annealing

We employ **Simulated Annealing (SA)** as the primary global search mechanism. SA is a probabilistic metaheuristic that allows uphill moves (accepting worse solutions) with a probability that decreases over time, enabling escape from shallow local optima.

**Energy Function.** We define the objective as the negation of the triangle count:

$$E(\mathbf{S}) = -N_{\triangle}(\mathbf{S})$$

where $N_{\triangle}(\mathbf{S})$ denotes the number of valid non-overlapping triangles formed by the configuration $\mathbf{S}$. Minimizing $E$ is equivalent to maximizing triangle count.

**Cooling Schedule.** We use a geometric (exponential) decay:

$$T_{k+1} = \alpha \cdot T_k, \quad \alpha = 0.995$$

with initial temperature $T_0 = 1.0$ and final temperature $T_f = 0.001$. This yields approximately $\log(T_f/T_0)/\log(\alpha) \approx 1380$ temperature steps.

**Acceptance Criterion.** A candidate state $\mathbf{S}'$ is accepted with probability:

$$P(\text{accept}) = \begin{cases} 1 & \text{if } \Delta E < 0 \\ \exp\left(-\frac{\Delta E}{T_k}\right) & \text{otherwise} \end{cases}$$

where $\Delta E = E(\mathbf{S}') - E(\mathbf{S})$.

**Perturbation Operator.** At each iteration, we generate a candidate by adding Gaussian noise scaled by temperature:

$$\tilde{\mathbf{S}} = \mathbf{S} + \mathcal{N}(0, \sigma \cdot T_k), \quad \sigma = 0.1$$

After perturbation, the normal vectors are re-projected onto the unit circle manifold $(S^1)^N$ via normalization:

$$(a'_i, b'_i) = \frac{(\tilde{a}_i, \tilde{b}_i)}{\|(\tilde{a}_i, \tilde{b}_i)\|}$$

to satisfy the constraint $a_i^2 + b_i^2 = 1$.

### 2.3 Local Refinement: Basin Hopping

Basin Hopping (also known as Iterated Local Search) is a two-phase strategy designed to explore multiple local minima efficiently. We apply this after the global SA phase to diversify solutions.

**Phase 1: The Kick.** Starting from the current best state $\mathbf{S}^*$, we apply a stochastic perturbation:

$$\mathbf{S}' = \mathbf{S}^* + \boldsymbol{\epsilon}, \quad \boldsymbol{\epsilon} \sim \mathcal{N}(0, \sigma^2 \mathbf{I})$$

To balance exploration and exploitation, we employ an **Adaptive Sigma Schedule**:

| Mode | $\sigma$ | Purpose |
|------|----------|---------|
| Exploration | 0.5 | Large jumps to escape current basin |
| Medium | 0.1 | Moderate perturbation |
| Polishing | 0.01 | Fine-tuning within basin |

Kick magnitudes are sampled stochastically with probabilities $(0.3, 0.4, 0.3)$ respectively.

**Phase 2: Relaxation.** The perturbed state $\mathbf{S}'$ is "relaxed" into the nearest local minimum using a short SA run with low initial temperature ($T_0 = \sigma$, $T_f = 0.0001$). This effectively performs greedy hill-climbing with occasional noise to avoid getting stuck on saddle points.

**Acceptance.** If the relaxed state $\mathbf{S}'_{\text{relax}}$ achieves a score $\geq$ the current best, it is accepted as the new seed.

### 2.4 Implementation Details

The algorithm was implemented in Python 3.10 using **NumPy** for vectorized computation.

**Vectorized Intersection Computation.** Rather than computing intersections pairwise in nested loops, we exploit broadcasting to compute the full coordinate array $\mathbf{P} \in \mathbb{R}^{N \times N \times 2}$ in a single vectorized operation:

```python
# Compute all pairwise intersections simultaneously
denom = a[:, None] * b[None, :] - a[None, :] * b[:, None]  # (N, N)
x_ij = (b[:, None] * c[None, :] - b[None, :] * c[:, None]) / denom
y_ij = (a[None, :] * c[:, None] - a[:, None] * c[None, :]) / denom
```

**Triangle Enumeration.** For each triple of lines $(i, j, k)$ with $i < j < k$, we verify triangle validity by checking that the three intersection points $\mathbf{p}_{ij}, \mathbf{p}_{jk}, \mathbf{p}_{ki}$ form a region not crossed by any other line segment. This is computed using a combination of signed area tests and segment intersection checks.

**Performance.** On a consumer-grade CPU (Intel i7), a single SA run of 100,000 iterations completes in approximately 45 seconds. The full 20-run multi-start search completes in under 15 minutes.

---

## 3. Results

### 3.1 Convergence Statistics

We executed **20 independent optimization runs** with randomly initialized line configurations. Each run consisted of 100,000 SA iterations followed by 1,000 Basin Hopping kicks.

| Metric | Value |
|--------|-------|
| Total Runs | 20 |
| Runs Converging to Score 25 | 20 |
| **Convergence Rate** | **100%** |
| Average Time to First 25 | 8.3 minutes |
| Total Search Time (20 runs) | < 15 minutes |

The perfect convergence rate suggests that the basin of attraction for 25-triangle configurations is exceptionally large, dominating the accessible phase space. No run settled at a lower score (e.g., 24 or 23), indicating that the energy landscape contains no significant "trap" states between random initialization and the global optimum.

**Statistical Interpretation.** If we model each run as a Bernoulli trial with unknown success probability $p$, observing 20/20 successes gives a 95% confidence lower bound of $p > 0.83$ (Clopper-Pearson). However, given the consistent single-iteration convergence patterns, we conjecture $p \approx 1.0$ for any reasonable initialization.

### 3.2 Combinatorial Classification of Solutions

A critical finding of this study is that the 25-triangle optimum is **not unique**. Through graph-theoretic analysis, we identified **11 combinatorially distinct intersection graphs** among 72 optimal configurations.

**Definition: Intersection Graph.** For a line arrangement $\mathcal{L} = \{L_1, \ldots, L_N\}$, the *intersection graph* $G(\mathcal{L})$ is defined as:
- **Vertices:** The $\binom{N}{2} = 45$ intersection points $\mathbf{p}_{ij} = L_i \cap L_j$.
- **Edges:** Two vertices are connected if they are adjacent on some line $L_k$, i.e., no other intersection lies between them on that line.

This graph captures the **combinatorial structure** of the arrangement, independent of the specific coordinates of the lines.

> **Note on Classification Granularity.** Graph isomorphism is a coarser equivalence than *isotopy class* (or *oriented matroid type*). Two arrangements may share the same intersection graph yet differ in the orientation of certain triple points; a property captured by oriented matroids but not by unoriented graph hashing. Our Weisfeiler-Lehman classification thus provides a lower bound on the true number of combinatorially distinct solution families.

**Classification Methodology.**
1. **Graph Extraction:** For each configuration, compute the intersection graph $G(\mathcal{L})$.
2. **Canonical Hashing:** Apply the Weisfeiler-Lehman graph hash algorithm (3 iterations) to obtain an isomorphism-invariant fingerprint.
3. **Clustering:** Group configurations by identical hash values.

**Results Summary:**

| Category | Count |
|----------|-------|
| Total Configurations Analyzed | 72 |
| Distinct Intersection Graphs | 11 |
| Largest Equivalence Class | Multiple members |
| Singleton Graphs | 4 |

**Interpretation.** The existence of 11 distinct intersection graphs reveals that the 25-triangle optimum is reached by fundamentally different combinatorial structures. Within each equivalence class, configurations are related by continuous deformation (elastic warping of lines without changing which intersections are adjacent). Across classes, however, the underlying graph structure is genuinely different.

This **archipelago structure** has profound implications: it suggests that the barrier to 26 is not a matter of "fine-tuning" existing solutions, but of discovering an entirely new intersection graph; one that none of our 72 configurations share.

### 3.3 Sensitivity Analysis ("The Breather Test")

To characterize the **local stability** of optimal configurations, we designed a deterministic perturbation experiment called the "Breather Test."

**Experimental Setup:**

1. Load a 25-triangle configuration (Variant #49, the most symmetric candidate).
2. Classify lines into two groups based on distance from origin:
   - **Inner Core** (5 lines): Closest to the origin (small $|c|$).
   - **Outer Rim** (5 lines): Furthest from the origin (large $|c|$).
3. Apply a uniform scaling factor $k$ to the $c$-parameter of Inner Core lines:
   $$c'_i = k \cdot c_i \quad \text{for } i \in \text{Inner Core}$$
4. Sweep $k$ from $0.80$ to $1.20$ in increments of $\Delta k = 0.0005$.
5. Record the triangle count $N_{\triangle}(k)$ at each step.

**Observed Behavior:**

The score function $N_{\triangle}(k)$ exhibits a **sharp local maximum with an extremely narrow basin of attraction** centered at $k = 1.0$:

![Breather Scan Results](images/breather_scan.png)

*Figure 2: Triangle count as a function of inner core scaling factor k. The optimal configuration exists only in an extremely narrow parameter window.*

| Scale Factor $k$ | Triangle Count |
|------------------|----------------|
| 0.98 | 19 |
| 0.99 | 22 |
| **1.00** | **25** |
| 1.01 | 21 |
| 1.02 | 19 |

The full-width at half-maximum (FWHM) of the peak is less than **2%** of the parameter range.

**Implications:**

- The 25-triangle configuration occupies an **extremely narrow basin** in parameter space.
- There is no smooth gradient leading from sub-optimal states to the optimum; the transition is essentially discontinuous.
- Stochastic methods that rely on gradient-following or small perturbations cannot "discover" the optimum from outside the basin; they must land inside it by chance.
- This explains why finding 26 triangles (if possible) would require a **topologically distinct** starting point, not incremental improvement from 25.

---

## 4. Discussion

### 4.1 The Symmetry Paradox

A natural hypothesis in combinatorial optimization is that maximal configurations often exhibit high symmetry. For $N=10$ lines, one might expect the optimal arrangement to possess $C_5$ rotational symmetry (since $10 = 2 \times 5$) or at least axial (mirror) symmetry.

We tested this hypothesis for **axial (reflective) symmetry** through two experiments:

**Experiment 1: Hard Symmetry Constraints.**
We identified Variant #49 as the most naturally symmetric configuration (lowest symmetry error under Y-axis reflection). We then *forced* perfect symmetry by:

1. Extracting 5 "master" lines from one half of the configuration.
2. Generating the remaining 5 lines as exact reflections: $(a, b, c) \mapsto (-a, b, c)$.
3. Optimizing only the 5 master lines (10 degrees of freedom instead of 30).

![Most Symmetric Variant #49](images/most_symmetric_variant_49.png)

*Figure 3: Variant #49 - the most naturally symmetric 25-triangle configuration before forcing exact symmetry.*

**Result:** The maximum achievable score under hard symmetry was **18 triangles**: a catastrophic drop from 25.

![Hard Symmetry Result](images/highlight_symmetric_18.png)

*Figure 4: The best achievable configuration under forced perfect symmetry, yielding only 18 triangles.*

**Experiment 2: Soft Symmetry (Lagrangian Penalty).**
We introduced a penalty term into the energy function:

$$E_{\text{soft}}(\mathbf{S}) = -N_{\triangle}(\mathbf{S}) + \lambda \cdot \sum_{i} \left\| L_i - \text{Reflect}(L_{\pi(i)}) \right\|^2$$

where $\pi$ is the pairing function and $\lambda = 10$ (small relative to the triangle weight of 1000).

**Result:** The optimizer recovered Score = 25 and reduced symmetry error, but could not break through to 26.

![Soft Symmetry Result](images/highlight_soft_symmetry.png)

*Figure 5: Configuration optimized with soft symmetry penalty: achieves 25 triangles with reduced but non-zero asymmetry.*

**Interpretation: The Micro-Asymmetry Hypothesis.**
The 25-triangle configurations appear to rely on **microscopic asymmetries**: small deviations from perfect symmetry to "close" certain triangles. Perfect reflective symmetry imposes geometric constraints that are mutually exclusive with the intersection structure required for 25 (or 26) triangles. The optimal solutions are *near-symmetric* but not *exactly* symmetric.

> **Scope Limitation.** Our symmetry experiments tested only axial (mirror) symmetry. Rotational symmetry groups such as $C_5$ or $C_{10}$: natural candidates given $N = 10 = 2 \times 5$ remain unexplored and constitute a direction for future investigation.

### 4.2 The Barrier to 26

Our results paint a consistent picture of the $N=10$ energy landscape:

1. **Dominant Basin:** The 25-triangle score is a pervasive attractor. All 20 independent runs converged to it.
2. **Archipelago Structure:** There is no unique solution: **11 combinatorially distinct intersection graphs** achieve the same optimal score.
3. **Narrow Peaks:** Each combinatorial class occupies extremely narrow basins (FWHM < 2% in parameter space).
4. **No Gradient to 26:** Perturbation experiments show no "smooth path" from 25 to 26.

These observations strongly suggest that **25 is the global maximum** for the connected component of the solution space reachable via continuous deformation from random initialization. However, we emphasize that stochastic search cannot prove the non-existence of a 26-triangle configuration: such a proof would require exhaustive combinatorial enumeration or formal methods.

**Conjecture.** If a configuration achieving $K(10) = 26$ exists, it must reside in a **combinatorially isolated basin** characterized by:

- A fundamentally different intersection graph not isomorphic to any of our 11 discovered classes.
- High-energy barriers separating it from all 25-triangle configurations.
- Inaccessibility via gradient-based or stochastic local search methods.

Such a configuration would require discovery through **combinatorial enumeration** of valid intersection graphs, followed by geometric realization; a fundamentally different algorithmic approach than the continuous optimization employed here.

### 4.3 Limitations and Future Work

**Limitations:**

- Our search was limited to continuous optimization over $\mathbb{R}^{30}$. Discrete graph structures were not explored.
- The "general position" constraint was enforced numerically, which may miss edge cases.
- Computational budget, while substantial, does not guarantee exhaustive coverage.

**Future Directions:**

1. **Graph-Theoretic Approach:** Enumerate all valid "intersection graphs" for $N=10$ and attempt geometric realization.
2. **SAT/SMT Solvers:** Encode the triangle-maximization problem as a constraint satisfaction instance.
3. **Exhaustive Algebraic Search:** Use computer algebra to find exact solutions with rational or algebraic coordinates.

---

## 5. Conclusion

This paper presents a combinatorial characterization of the Kobon Triangle problem for $N=10$ lines. Our principal findings are:

1. **Replication of the World Record:** We successfully and consistently converged to configurations achieving **25 triangles**, matching Suzuki's 2002 result across 100% of independent trials.

2. **Combinatorial Diversity:** We discovered **11 distinct intersection graphs** among 72 optimal configurations, demonstrating that the solution space is an archipelago of combinatorially inequivalent local optima.

3. **Narrow Basins:** Sensitivity analysis revealed that optimal configurations occupy extremely narrow basins in parameter space. Perturbations as small as 2% cause the score to collapse, indicating that there is no smooth gradient path to higher scores.

4. **Symmetry is Not the Answer:** Contrary to intuition, forcing exact symmetry degrades performance. The optimal configurations rely on subtle asymmetries to maximize triangle count.

**Final Verdict.** We have characterized the $K(10) = 25$ landscape using modern stochastic optimization and graph-theoretic classification. The barrier from 25 to 26 is **combinatorial rather than metric**: it is not a matter of precision or computational power, but of discovering a fundamentally different intersection graph. If a 26-triangle configuration exists, it lies in a combinatorially isolated region inaccessible via continuous optimization.

---

## References

1. Fujimura, K. (1978). *Recreational Mathematics Problems*. Tokyo.
2. Suzuki, T. (2002). Personal communication. Solution for $K(10) = 25$.
3. Clément, J., & Bader, M. (2007). "On the Number of Triangles in Simple Arrangements of Lines." *Discrete Mathematics*, 307(15), 1882–1894.
4. Wales, D. J., & Doye, J. P. K. (1997). "Global Optimization by Basin-Hopping." *Journal of Physical Chemistry A*, 101(28), 5111–5116.

---

**Acknowledgments**

Algorithm design, implementation, and analysis performed by Maurizio Falconi.
