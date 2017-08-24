
import numpy as np

def triArea(factor):
    p1 = np.array([1, 2, 3]) * factor
    p2 = np.array([4, 5, 6]) * factor
    p3 = np.array([1, 6, 7]) * factor

    print p1, p2, p3

    p1p3 = p3 - p1
    p1p2 = p2 - p1

    cross = np.cross(p1p3, p1p2)
    area = np.linalg.norm(cross) * 0.5
    return area


a = triArea([0.2, 1.0, 1.0])
b = triArea([1.0, 1.0, 1.0])
print a, b, b/a