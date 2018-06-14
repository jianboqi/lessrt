"""
Normalize point cloud according to DEM
Author: Jianbo Qi
Date: 2017-4-25
"""
import argparse
import laspy
import math
import time
import numpy as np
import joblib
import tempfile
import os
import shutil
from utils import read_file_to_arr




def sub_fun_height(d_xyz, _zarr, dem_data, _seg_index, _num_w, _num_h, _resolution, _seg_size):
    # corresponding interval
    lower = _seg_index * _seg_size
    upper = min((_seg_index+1) * _seg_size, len(d_xyz))
    print("Processing from: ", lower, " to ", upper)
    # For each point, find its corresponding cell
    for i in range(lower, upper):
        row = int(d_xyz[i][1] / _resolution)  # row of the corresponding cell
        col = int(d_xyz[i][0] / _resolution)
        _zarr[i] = d_xyz[i][2] - dem_data[_num_h-row-1][col]
        if _zarr[i] < 0:
            _zarr[i] = 0

if __name__ == "__main__":
    # parameter handling
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", help="Input las file.", required=True)
    parse.add_argument("-dem", help="Input DEM file.", required=True)
    parse.add_argument("-o", help="Output las file name (*.las).", required=True)
    parse.add_argument("-seg_size", help="How many points for each core to run parallelly. ", type=int, default=500000)
    args = parse.parse_args()

    input_las_file = args.i
    output_las_file = args.o
    dem_file = args.dem

    start = time.clock()
    print("Reading data...")
    # read point cloud
    inFile = laspy.file.File(input_las_file, mode='r')
    # x y z of each point
    xyz_total = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
    point_number = len(xyz_total)
    print("Total points:", point_number)
    # offset: relative to the left and bottom corner.
    # computing the xy bounding box of the whole terrain, and number of cells according to resolution
    min_x, min_y = inFile.x.min(), inFile.y.min()
    # height value are no need to offset
    delta_xyz = xyz_total - np.array([min_x, min_y, 0])

    # delta_xy = xyz[:, 0:2] - np.array([min_x, min_y])
    print("Start to calculate...")

    # prepare for parallel computing
    # segment the array into multiple segmentation by define a maximum size of each part
    seg_size = args.seg_size  # 500000 points for each core, parallel
    seg_num = int(math.ceil(point_number / float(seg_size)))
    # read DEM
    width, height, resolution, demdata = read_file_to_arr(dem_file)

    print("DEM size: ", "Width: ", width," Height: ", height)
    folder = tempfile.mkdtemp()
    z_out_name = os.path.join(folder, 'point_z')
    zarr = np.memmap(z_out_name, dtype=float, shape=(len(delta_xyz),), mode='w+')
    joblib.Parallel(n_jobs=joblib.cpu_count(), max_nbytes=1e4)(joblib.delayed(sub_fun_height)(delta_xyz, zarr, demdata, i,
                                                        width, height, resolution, seg_size)
                                       for i in range(0, seg_num))
    out_File = laspy.file.File(output_las_file, mode='w', header=inFile.header)
    out_File.points = inFile.points
    out_File.z = zarr
    out_File.close()
    print("Done.")
    del zarr
    try:
        shutil.rmtree(folder)
    except OSError:
        print("Failed to delete: " + folder)
    end = time.clock()
    print("Time: ", "%.3fs" % (end - start))