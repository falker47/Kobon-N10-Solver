import numpy as np
from geometry import KobonSolver

def test():
    N = 5
    lines = np.random.randn(N, 3)
    solver = KobonSolver(lines)
    
    print("Computing intersections...")
    try:
        points, mask = solver.compute_intersections()
        print("Success!")
        print("Points shape:", points.shape)
    except Exception as e:
        print("Caught exception:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
