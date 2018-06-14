#coding: utf-8
"""
Estimate LAI from discrete Lidar
Implementation of "Forest Leaf Area Index (LAI) Estimation Using Airborne Discrete‐Return Lidar Data"
This method has three options for LAI inversion: uncorrected echo intensity, corrected echo intensity, echo counts
Author: Jianbo Qi
Date: 2017-4-25
"""
import argparse
import time
import laspy
import numpy as np
import math
import tempfile
import os
import joblib
from utils import saveToHdr


def compute_bounding_box(input_File, cell_resolution):
    mins = input_File.header.min
    maxs = input_File.header.max
    # add a small value to be more convenient to do gridding
    width = maxs[0] - mins[0] + 0.00001
    height = maxs[1] - mins[1] + 0.00001
    min_x, min_y = mins[0], mins[1]
    num_w = int(math.ceil(width / float(cell_resolution)))
    num_h = int(math.ceil(height / float(cell_resolution)))
    return min_x, min_y, width, height, num_w, num_h

def transmittance2lai_simple(arr):
    # assuming the LAD is spherical, and ingore the scanning angle
    G = 0.5
    LAI = -np.log(arr)/G
    return LAI

def sub_fun_EC_lai(_delta_xyz, _classification, _output_ground_echo, _output_vegetation_echo, _seg_index, _num_h, _resolution, _seg_size):
    lower = _seg_index * _seg_size
    upper = min((_seg_index + 1) * _seg_size, len(_delta_xyz))
    print("Processing from: ", lower, " to ", upper)
    for i in range(lower, upper):
        row = int(_delta_xyz[i][1] / _resolution)
        col = int(_delta_xyz[i][0] / _resolution)
        if _classification[i] == 0:
            _output_ground_echo[_num_h-row-1][col] += 1
        if _classification[i] == 1:
            _output_vegetation_echo[_num_h-row-1][col] += 1

def sub_fun_UEI_lai(_delta_xyz, _classification, _intensity, _output_ground_echo, _output_vegetation_echo, _seg_index, _num_h, _resolution, _seg_size):
    lower = _seg_index * _seg_size
    upper = min((_seg_index + 1) * _seg_size, len(_delta_xyz))
    print("Processing from: ", lower, " to ", upper)
    for i in range(lower, upper):
        row = int(_delta_xyz[i][1] / _resolution)
        col = int(_delta_xyz[i][0] / _resolution)
        if _classification[i] == 0:
            _output_ground_echo[_num_h-row-1][col] += _intensity[i]
        if _classification[i] == 1:
            _output_vegetation_echo[_num_h-row-1][col] += _intensity[i]

def sub_fun_CEI_lai(_delta_xyz, _classification, _intensity, _scanning_angle, _avgHeight, _output_ground_echo, _output_vegetation_echo, _seg_index, _num_h, _resolution, _seg_size):
    lower = _seg_index * _seg_size
    upper = min((_seg_index + 1) * _seg_size, len(_delta_xyz))
    print("Processing from: ", lower, " to ", upper)
    for i in range(lower, upper):
        row = int(_delta_xyz[i][1] / _resolution)
        col = int(_delta_xyz[i][0] / _resolution)
        # normalize intensity
        R = (_avgHeight - _delta_xyz[i][2])/math.cos(_scanning_angle[i]/180.0*math.pi)
        n_intensity = _intensity[i]*R*R/float(_avgHeight*_avgHeight)
        if _classification[i] == 0:
            _output_ground_echo[_num_h-row-1][col] += n_intensity
        if _classification[i] == 1:
            _output_vegetation_echo[_num_h-row-1][col] += n_intensity



if __name__ == "__main__":
    # parameter handling
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", help="Input las file, must be output of csfclassify.py.", required=True)
    parse.add_argument("-o", help="LAI product.", required=True)
    parse.add_argument("-resolution", help="Resolution of LAI.", required=True,type=float, default=10)
    parse.add_argument("-method", help="Inversion method: UEI, CEI, EC", required=True, default="EC")
    parse.add_argument("-avgFlightHeight", help="Average Flight Height (altitude, m)",type=float)
    parse.add_argument("-originlas", help="Original Las file.")
    parse.add_argument("-seg_size", help="How many points for each core to run parallelly. ", type=int, default=500000)
    args = parse.parse_args()

    input_las_file = args.i
    lai_out_file = args.o
    resolution = args.resolution
    method = args.method
    if method == "CEI":
        if args.avgFlightHeight is None:
            print("Please input the average flight height.")
            import sys
            sys.exit(0)
        if args.originlas is None:
            print("Please input the original las file.")
            import sys
            sys.exit(0)

    start = time.clock()
    print("Method:", method)
    print("Reading data...")
    # read point cloud
    inFile = laspy.file.File(input_las_file, mode='r')
    # x y z of each point
    if method == "CEI": # CEI method need original Z value
        oinFile = laspy.file.File(args.originlas, mode='r')
        xyz_total = np.vstack((inFile.x, inFile.y, oinFile.z)).transpose()
    else:
        xyz_total = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()

    classification = inFile.classification
    geoTransform = (inFile.x.min(), resolution, 0, inFile.y.max(), 0, -resolution)
    point_number = len(xyz_total)
    print("Total points:", point_number)

    min_x, min_y, width, height, num_w, num_h = compute_bounding_box(inFile, resolution)
    print("LAI product size: ", "Width: ", num_w, " Height: ", num_h)
    # height value are no need to offset
    delta_xyz = xyz_total - np.array([min_x, min_y, 0])
    # prepare for parallel computing
    # segment the array into multiple segmentation by define a maximum size of each part
    seg_size = args.seg_size  # 500000 points for each core, parallel
    seg_num = int(math.ceil(point_number / float(seg_size)))

    # define a memmap for output
    folder = tempfile.mkdtemp()
    output_ground_echo = np.memmap(os.path.join(folder, 'ground'), dtype=int, shape=(num_h, num_w), mode='w+')
    output_vegetation_echo = np.memmap(os.path.join(folder, 'vegetation'), dtype=int, shape=(num_h, num_w), mode='w+')

    if method == "EC":
        joblib.Parallel(n_jobs=joblib.cpu_count(), max_nbytes=1e4)(
            joblib.delayed(sub_fun_EC_lai)(delta_xyz,classification, output_ground_echo,output_vegetation_echo , i, num_h, resolution, seg_size)
                                                                                for i in range(0, seg_num))

    if method == "UEI":
        echo_intensity = inFile.intensity
        joblib.Parallel(n_jobs=joblib.cpu_count(), max_nbytes=1e4)(
            joblib.delayed(sub_fun_UEI_lai)(delta_xyz, classification, echo_intensity.astype(int), output_ground_echo, output_vegetation_echo, i, num_h, resolution, seg_size)
                                                                                 for i in range(0, seg_num))

    if method == "CEI":
        avgHeight = args.avgFlightHeight
        echo_intensity = inFile.intensity
        scanning_angle = inFile.scan_angle_rank
        joblib.Parallel(n_jobs=joblib.cpu_count(), max_nbytes=1e4)(
            joblib.delayed(sub_fun_CEI_lai)(delta_xyz, classification, echo_intensity.astype(int),scanning_angle.astype(int),avgHeight, output_ground_echo, output_vegetation_echo, i, num_h, resolution, seg_size)
                                                                                 for i in range(0, seg_num))

    if method == "CEI":
        transmittance = output_ground_echo / (output_ground_echo + 0.5*output_vegetation_echo).astype(float)
    else:
        transmittance = output_ground_echo/(output_ground_echo+output_vegetation_echo).astype(float)
    transmittance[transmittance==0] = 0.5
    LAI = transmittance2lai_simple(transmittance)
    saveToHdr(LAI, lai_out_file, geoTransform)
    del output_ground_echo
    del output_vegetation_echo
    print("Done.")
    try:
        import shutil
        shutil.rmtree(folder)
    except OSError:
        print("Failed to delete: " + folder)

    end = time.clock()
    print("Time: ", "%.3fs" % (end - start))







