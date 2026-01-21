import argparse
import numpy as np
import time
import json
from tqdm import tqdm
from geometry import KobonSolver
from optimizer import Optimizer
from visualizer import plot_configuration

def save_best_config(lines, score, filename="best_kobon_10.json"):
    data = {
        "n_lines": len(lines),
        "score": score,
        "lines": lines.tolist()
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nSaved new best configuration (Score: {score}) to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Kobon Triangle Solver - N=10 Challenge")
    parser.add_argument("-n", "--lines", type=int, default=10, help="Number of lines")
    parser.add_argument("-i", "--iterations", type=int, default=100000, help="Optimization iterations per run")
    parser.add_argument("-r", "--runs", type=int, default=20, help="Number of independent runs")
    parser.add_argument("--seed", type=int, default=None, help="Global random seed")
    parser.add_argument("--alpha", type=float, default=0.001, help="Cooling schedule T_end (lower = slower/deeper cooling)")
    args = parser.parse_args()

    if args.seed:
        np.random.seed(args.seed)

    print(f"Starting Kobon Triangle Search for N={args.lines} lines...")
    print(f"Configuration: {args.runs} runs x {args.iterations} iterations.")
    
    global_best_score = -1
    global_best_config = None
    
    start_time_all = time.time()
    
    # Outer loop with progress bar
    for run_idx in tqdm(range(args.runs), desc="Runs"):
        # Initialize Optimizer
        optimizer = Optimizer(n_lines=args.lines)
        
        # Run optimization
        # Use T_end from args (user called it alpha)
        best_state, best_score = optimizer.optimize(
            iterations=args.iterations, 
            T_end=args.alpha,
            verbose=False # Keep it clean for tqdm
        )
        
        # Check global best
        if best_score > global_best_score:
            global_best_score = best_score
            global_best_config = best_state
            tqdm.write(f"Run {run_idx+1}: Found new global best! Score: {global_best_score}")
            save_best_config(global_best_config, global_best_score)
            
    elapsed_all = time.time() - start_time_all
    print(f"\nAll runs complete in {elapsed_all:.2f}s.")
    print(f"Final Best Triangle Count: {global_best_score}")
    
    # Visualize Best
    if global_best_config is not None:
        print("Generating visualization for best result...")
        solver = KobonSolver(global_best_config)
        triangles = solver.find_triangles()
        plot_configuration(global_best_config, triangles)

if __name__ == "__main__":
    main()
