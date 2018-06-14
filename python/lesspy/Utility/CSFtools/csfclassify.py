"""
Classify point cloud according to Scalar Value or x, y, z
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


def sub_fun_classify(_fieldList, _threshold, _class_arr, _seg_index, _seg_size):
    # corresponding interval
    lower = _seg_index * _seg_size
    upper = min((_seg_index+1) * _seg_size, len(_fieldList))
    print("Processing from: ", lower, " to ", upper)
    # For each point, find its corresponding cell
    for i in range(lower, upper):
        if _fieldList[i] <= _threshold:
            _class_arr[i] = 0
        else:
            _class_arr[i] = 1

if __name__ == "__main__":
    # parameter handling
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", help="Input las file.", required=True)
    parse.add_argument("-field", help="Which one is the classification based on. field, x, y,z.", required=True)
    parse.add_argument("-value", help="threshold. < value will be 0, > value will be 1. ", required=True, type=float)
    parse.add_argument("-o", help="Output las file name (*.las).", required=True)
    parse.add_argument("-seg_size", help="How many points for each core to run parallelly. ", type=int, default=500000)
    args = parse.parse_args()

    input_las_file = args.i
    output_las_file = args.o
    field = args.field
    threshold = args.value

    start = time.clock()
    print("Reading data...")
    # read point cloud
    inFile = laspy.file.File(input_las_file, mode='r')
    # field list
    fieldList = []
    if field in ("x", "X"):
        fieldList = inFile.x
    elif field in ("y", "Y"):
        fieldList = inFile.y
    elif field in ("z", "Z"):
        fieldList = inFile.z
    elif field in ("intensity", "Intensity"):
        fieldList = inFile.intensity
    elif field in ("return_num", "Return_num"):
        fieldList = inFile.return_num
    elif field in ("num_returns", "Num_returns"):
        fieldList = inFile.num_returns
    elif field in ("scan_angle_rank", "Scan_angle_rank"):
        fieldList = inFile.scan_angle_rank
    elif field in ("time", "Time", "gps_time", "Gps_time"):
        fieldList = inFile.gps_time

    if len(fieldList) == 0:
        print("No field found.")
        import sys
        sys.exit(0)

    point_number = len(fieldList)
    print("Total points:", point_number)
    print("Start to classify...")

    # prepare for parallel computing
    # segment the array into multiple segmentation by define a maximum size of each part
    seg_size = args.seg_size  # 500000 points for each core, parallel
    seg_num = int(math.ceil(point_number / float(seg_size)))
    # read DEM
    folder = tempfile.mkdtemp()
    class_out_name = os.path.join(folder, 'classify')
    class_arr = np.memmap(class_out_name, dtype=int, shape=(len(fieldList),), mode='w+')
    joblib.Parallel(n_jobs=joblib.cpu_count(), max_nbytes=1e4)(joblib.delayed(sub_fun_classify)
                                                               (fieldList, threshold, class_arr, i, seg_size)
                                                                for i in range(0, seg_num))
    out_File = laspy.file.File(output_las_file, mode='w', header=inFile.header)
    out_File.points = inFile.points
    out_File.set_classification(class_arr.tolist())
    out_File.close()
    print("Done.")
    del class_arr
    try:
        shutil.rmtree(folder)
    except OSError:
        print("Failed to delete: " + folder)
    end = time.clock()
    print("Time: ", "%.3fs" % (end - start))