# 📐 Kobon Triangle Hunter (N=10)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Robust%20Local%20Optimum-yellow)
![Record](https://img.shields.io/badge/Best%20Score-25%20Triangles-green)

A high-performance algorithmic framework devised to solve the **Kobon Triangle Problem** for N=10 lines.
This project successfully replicated the **World Record (25 Triangles)** using consumer hardware through advanced optimization techniques, identifying **52 distinct geometric families** of solutions.

![Kobon Mosaic](images/kobon_mosaic.jpg)
*A mosaic of unique geometric configurations found, all achieving the record score of 25.*

## 🎯 The Challenge
The goal is to arrange N lines in a plane to maximize the number of non-overlapping triangles.
For N=10, the theoretical upper bound is 26. However, no configuration with 26 triangles has ever been found. The known record is **25**.

## 📂 Project Structure

- `src/`: Core logic (main.py, geometry.py, optimizer.py, etc.)
- `solutions/`: Dataset of JSON solutions (Families & Singletons)
- `images/`: Visual Analysis (Mosaic & Scans)
- `ANALYSIS.md`: Scientific Post-Mortem & Findings

## 🚀 Usage

### 1. Global Search
Launch a distributed search to find promising basins of attraction:
`python src/main.py --lines 10 --iterations 100000 --runs 20`

### 2. Local Refinement
Take the best candidates and apply Gaussian "kicks" to find variations:
`python src/refiner.py --sigma 0.1 --kicks 1000`

### 3. Topological Scan ("The Breather")
Stress-test a solution by scaling internal geometry to find phase transitions:
`python src/breather.py`

## 📊 Key Results
- **Optimization:** Reached global maximum (25) in < 15 minutes.
- **Diversity:** Mapped **52 geometrically unique** solutions.
- **Stability:** Proved that the 25-triangle configuration is a "Deep Well" local minimum.

See [ANALYSIS.md](ANALYSIS.md) for the full scientific report.
