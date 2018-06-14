"""
DEM Generation from point cloud
Author: Jianbo Qi
Date: 2017-1-15
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



# interpolate the empty cells after rasterization
def interpolate(data_arr, size=1):
    rows, cols = data_arr.shape
    rpos, cpos = np.where(data_arr==0)
    print("Processing empty cells... ")
    print("Total empty cells: ", len(rpos))
    for i in range(0, len(rpos)):
        while True:
            left = max(0, cpos[i]-size)
            right = min(cols-1, cpos[i] + size)
            up = max(0, rpos[i] - size)
            down = min(rows-1, rpos[i] + size)
            empty = True
            t_w = 0
            interpolated_value = 0
            for m in range(up, down+1):
                for n in range(left, right+1):
                    if data_arr[m][n] > 0:
                        w = 1/float((m-rpos[i])**2+(n-cpos[i])**2)
                        interpolated_value += data_arr[m][n]*w
                        t_w += w
                        empty = False
            if not empty:
                interpolated_value /= t_w
                data_arr[rpos[i]][cpos[i]] = interpolated_value
                break
            size += 1

def fillHoleofchm(datarr, h):
    rows, cols = datarr.shape
    for i in range(0, rows):
        for j in range(0, cols):
            pv = datarr[i][j]
            left = max(0, j - 1)
            right = min(j + 1, cols-1)
            up = max(0, i - 1)
            down = min(i + 1, rows-1)
            total = np.array([datarr[i][left], datarr[i][right], datarr[up][j], datarr[down][j]])
            diff = total - pv
            diff = diff > h
            if diff.sum() > 2:
                # if pv < left - t and pv < right-t and pv < up -t and pv < down-t:
                datarr[i][j] = total.sum() * 0.25


def sub_fun_dem(d_xyz, output_arr_dem, _output_dem_num, _seg_index, _num_w, _num_h, _resolution, _search_length, _seg_size, _method):
    # corresponding interval
    lower = _seg_index * _seg_size
    upper = min((_seg_index+1) * _seg_size, len(d_xyz))
    print("Processing from: ", lower, " to ", upper)
    # For each point, find its corresponding cell
    for i in range(lower, upper):
        row = int(d_xyz[i][1] / _resolution)  # row of the corresponding cell
        col = int(d_xyz[i][0] / _resolution)
        # determine neighbors
        # the position of each cell's left bottom corner
        cell_x_start = col * _resolution
        cell_y_start = row * _resolution
        # position relative to cell left bottom corner
        # for each points, calculate the relatively position to the cell's left corner
        # thus this values should in [0, resolution]
        cell_relative_x = d_xyz[i][0] - cell_x_start
        cell_relative_y = d_xyz[i][1] - cell_y_start
        # compute influence region: for each point, computing the influenced cells.
        # down and up influence
        delta_y_down, delta_y_up = _search_length*0.5 - cell_relative_y, \
                                   _search_length*0.5 - (_resolution - cell_relative_y)
        influence_down_num, influence_up_num = max(0,int(math.ceil(delta_y_down / float(_resolution)))), \
                                                   max(0,int(math.ceil(delta_y_up / float(_resolution))))
        delta_x_left, delta_x_right = _search_length*0.5 - cell_relative_x, \
                                      _search_length*0.5 - (_resolution - cell_relative_x)
        influence_left_num, influence_right_num = max(0,int(math.ceil(delta_x_left / float(_resolution)))), \
                                                      max(0,int(math.ceil(delta_x_right / float(_resolution))))
        # print influence_right_num, influence_left_num, influence_down_num, influence_up_num
        for rr in range(row - influence_down_num, row + influence_up_num + 1):
            for cc in range(col - influence_left_num, col + influence_right_num + 1):
                if (-1 < rr < _num_h) and (-1 < cc < _num_w):
                        _output_dem_num[_num_h - rr - 1][cc] += 1
                        output_arr_dem[_num_h - rr - 1][cc] += d_xyz[i][2]
                        # output_arr_dem[_num_h - rr - 1][cc] = min(output_arr_dem[_num_h - rr - 1][cc], d_xyz[i][2])


def sub_fun_dsm_dem(d_xyz, _classification, output_arr_dem, _output_dem_num, output_arr_dsm, _seg_index, _num_w, _num_h, _resolution, _search_length, _seg_size, _method):
    # corresponding interval
    lower = _seg_index * _seg_size
    upper = min((_seg_index+1) * _seg_size, len(d_xyz))
    print("Processing from: ", lower, " to ", upper)
    for i in range(lower, upper):
        row = int(d_xyz[i][1] / _resolution)
        col = int(d_xyz[i][0] / _resolution)
        # determine neighbors
        # the position of each cell's left bottom corner
        cell_x_start = col * _resolution
        cell_y_start = row * _resolution
        # position relative to cell left bottom corner
        # for each points, calculate the relatively position to the cell's left corner
        # thus this values should in [0, resolution]
        cell_relative_x = d_xyz[i][0] - cell_x_start
        cell_relative_y = d_xyz[i][1] - cell_y_start
        # compute influence region: for each point, computing the influenced cells.
        # down and up influence
        delta_y_down, delta_y_up = _search_length*0.5 - cell_relative_y, \
                                   _search_length*0.5 - (_resolution - cell_relative_y)
        influence_down_num, influence_up_num = max(0, int(math.ceil(delta_y_down / float(_resolution)))), \
                                               max(0,int(math.ceil(delta_y_up / float(_resolution))))
        # print delta_y_down, delta_y_up
        delta_x_left, delta_x_right = _search_length*0.5 - cell_relative_x, \
                                      _search_length*0.5 - (_resolution - cell_relative_x)
        influence_left_num, influence_right_num = max(0,int(math.ceil(delta_x_left / float(_resolution)))), \
                                                  max(0,int(math.ceil(delta_x_right / float(_resolution))))
        # print influence_right_num, influence_left_num, influence_down_num, influence_up_num
        for rr in range(row - influence_down_num, row + influence_up_num + 1):
            for cc in range(col - influence_left_num, col + influence_right_num + 1):
                if (-1 < rr < _num_h) and (-1 < cc < _num_w):
                        if _classification[i] == 2:
                            _output_dem_num[_num_h - rr - 1][cc] += 1
                            output_arr_dem[_num_h - rr - 1][cc] += d_xyz[i][2]
                            # output_arr_dem[_num_h - rr - 1][cc] = min(output_arr_dem[_num_h - rr - 1][cc],d_xyz[i][2])
        output_arr_dsm[_num_h - row - 1][col] = max(output_arr_dsm[_num_h - row - 1][col], d_xyz[i][2])
                        # output_arr[_num_h - rr - 1][cc] = 2

if __name__ == "__main__":
    # parameter handling
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", help="Input las file.", required=True)
    parse.add_argument("-o", help="Output image file name (envi).", required=True)
    parse.add_argument("-dsm", help="Output dsm image file name (envi).")
    parse.add_argument("-chm", help="Output chm image file name (envi).")
    parse.add_argument("-fillholeofchm", help="Fill hole within corwn, specify a height difference.",type=float,default=3)
    parse.add_argument("-resolution", type=float, help="Resolution of final image.", required=True)
    parse.add_argument("-method", help="Method to estimate DEM value: min, max, mean.(No use now)", default="min")
    parse.add_argument("-box_radius", type=float, default=-1,
                       help="Search radius used to determined height value of each pixel.")
    parse.add_argument("-fill_radius", help="Make point cloud denser by add points around each point.",type=float)
    parse.add_argument("-fill_num", help="How many points to fill around each point.", type=int, default=3)
    parse.add_argument("-seg_size", help="How many points for each core to run parallelly. ", type=int, default=500000)
    args = parse.parse_args()

    input_las_file = args.i
    output_img_file = args.o
    method = args.method
    resolution = args.resolution
    search_length = 2*args.resolution
    if args.box_radius != -1:
        search_length = args.box_radius*2
    has_dsm = False
    if args.dsm is not None:
        has_dsm = True

    start = time.clock()
    print("Reading data...")
    # read point cloud
    inFile = laspy.file.File(input_las_file, mode='r')
    # x y z of each point
    xyz_total = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
    classification = inFile.classification
    geoTransform = (inFile.x.min(), resolution, 0, inFile.y.max(), 0, -resolution)
    if has_dsm:
        xyz = xyz_total
    else:
        xyz = xyz_total[classification == 2]
    point_number = len(xyz)
    print("Total points:", point_number)
    # offset: relative to the left and bottom corner.
    # computing the xy bounding box of the whole terrain, and number of cells according to resolution
    min_x, min_y, width, height, num_w, num_h = compute_bounding_box(inFile, resolution)
    # height value are no need to offset
    delta_xyz = xyz - np.array([min_x, min_y, 0])
    # Radius fill
    if args.fill_radius is not None:
        print("Radius filling...: radius =", args.fill_radius)
        NUM = args.fill_num
        newXY = map(lambda x: [args.fill_radius*math.cos(x/float(NUM)*2*math.pi),
                                args.fill_radius * math.sin(x / float(NUM) * 2*math.pi)], range(0, NUM))
        rows,cols = delta_xyz.shape
        tmp_point = np.zeros((rows*NUM, cols))
        tmp_classification = np.ones((rows*NUM,))
        index = 0
        for i in range (0, rows):
            for xy in newXY:
                tmp_point[index] = np.array([xy[0] + delta_xyz[i][0], xy[1]+delta_xyz[i][1], delta_xyz[i][2]])
                if classification[i] == 2:
                    tmp_classification[index] = 2
                index += 1
        delta_xyz = np.vstack((delta_xyz, tmp_point))
        classification = np.hstack((classification, tmp_classification))

        print("Updated points: ", len(delta_xyz))

    # delta_xy = xyz[:, 0:2] - np.array([min_x, min_y])
    print("Start to calculate...")

    # prepare for parallel computing
    # segment the array into multiple segmentation by define a maximum size of each part
    seg_size = args.seg_size  # 500000 points for each core, parallel
    seg_num = int(math.ceil(len(delta_xyz) / float(seg_size)))
    # define a memmap for output
    folder = tempfile.mkdtemp()
    dem_out_name = os.path.join(folder, 'dem')
    dem_out_num_name = os.path.join(folder, 'dem_num')
    dsm_out_name = os.path.join(folder, 'dsm')
    # this stores the final estimated DEM
    try:
        print("DEM size: ", "Width: ", num_w," Height: ", num_h)
        print("DEM resolution:", resolution)
        output_dem = np.memmap(dem_out_name, dtype=float, shape=(num_h, num_w), mode='w+')
        output_dem_num = np.memmap(dem_out_num_name, dtype=int, shape=(num_h, num_w), mode='w+')
        if has_dsm:
            output_dsm = np.memmap(dsm_out_name, dtype=float, shape=(num_h, num_w), mode='w+')
            joblib.Parallel(n_jobs=joblib.cpu_count(), max_nbytes=1e4)(joblib.delayed(sub_fun_dsm_dem)(delta_xyz, classification, output_dem, output_dem_num, output_dsm, i,
                                                                num_w, num_h, resolution, search_length, seg_size, method)
                                               for i in range(0, seg_num))
            interpolate(output_dsm)
            saveToHdr(output_dsm, args.dsm, geoTransform)
        else:
            joblib.Parallel(n_jobs=joblib.cpu_count(), max_nbytes=1e4)(joblib.delayed(sub_fun_dem)(delta_xyz, output_dem,output_dem_num, i,
                                                                num_w, num_h, resolution, search_length, seg_size,
                                                                method)
                                               for i in range(0, seg_num))
        output_dem_num[output_dem_num == 0] = 1
        output_dem = output_dem / output_dem_num
        interpolate(output_dem)
        saveToHdr(output_dem, output_img_file,geoTransform)

        # chm
        if args.chm is not None and has_dsm:
            chm = output_dsm - output_dem
            chm[chm<0] = 0
            if args.fillholeofchm is not None:
                print("Filling holes with  ")
                fillHoleofchm(chm, args.fillholeofchm)
            saveToHdr(chm, args.chm, geoTransform)
        if has_dsm:
            del output_dsm

        del output_dem
        del output_dem_num
        print("Done.")
    finally:
        try:
            shutil.rmtree(folder)
        except OSError:
            print("Failed to delete: " + folder)

    end = time.clock()
    print("Time: ", "%.3fs" % (end - start))