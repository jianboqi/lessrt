"""
Point normalization
Author: Jianbo Qi
Date: 2017-1-15
"""
import argparse
import laspy
import numpy as np
from scipy.spatial import Delaunay

parse = argparse.ArgumentParser()
parse.add_argument("-i", help="Input las file.", required=True)
parse.add_argument("-ground_points", help="Optional. Provide ground las file.")
parse.add_argument("-o", help="Output las file of normalized cloud.", required=True)
args = parse.parse_args()

input_las_file = args.i
output_las_file = args.o

input_File = laspy.file.File(input_las_file, mode='r')
xyz = np.vstack((input_File.x, input_File.y, input_File.z)).transpose()
ground_points = xyz[input_File.classification == 2]
# Triangulation
points_xy = [[x[0], x[1]] for x in ground_points]
print len(points_xy)
tri = Delaunay(points_xy)
print len(tri.simplices)

import matplotlib.pyplot as plt
plt.triplot(ground_points[:,0], ground_points[:,1], tri.simplices.copy())
# plt.plot(ground_points[:,0], ground_points[:,1], '.')
plt.show()