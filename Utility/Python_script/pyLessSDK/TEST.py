# coding: utf-8
# Testing

# Test 01: test the generated normals whether it coordinates with the equation
import numpy as np
input_obj = r"d:\crown.obj"
f = open(input_obj)
points = []
thetas = []
for line in f:
    arr = line.split(" ")
    if arr[0] == "v":
        p = list(map(lambda x: float(x), arr[1:]))
        points.append(np.array(p))
    if arr[0] == "f":
        p1p2 = points[1] - points[0]
        p1p4 = points[3] - points[0]
        n = np.cross(p1p2, p1p4)
        n = n / np.linalg.norm(n)
        costheta = np.dot(n, np.array([0, 1, 0]))
        theta = np.arccos(costheta)
        thetas.append(theta/np.pi*180)
        points = []
# import matplotlib.pyplot as plt
# plt.hist(thetas, bins=50)
# plt.show()