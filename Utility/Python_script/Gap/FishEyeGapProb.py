# coding: utf-8
###################
# author: Jianbo QI
# Date: 2019-6-29
###################
# Calculate directional Gap probability from fisheye image products
# produced by LESS Model
##################
# Usage:
# [Path to where LESS is installed]/app/bin/python/python.exe FishEyeGapProb.py
# -i [path to image file] -o [path to output file]
# Please note: [path to image file] can be either: (1) path1 path2 path3; or (2) path*
##################

import argparse
import glob
import time
import math
from osgeo import gdal
import sys
import numpy as np

def generation_discrete_directions(num_of_directions):
    accumulated_zenith_angle = []
    accumulated_azimuth_angle = []
    r_i1 = 2 * math.sin(0.25 * math.pi)
    theta_i1 = 0.5 * math.pi
    k_i1 = num_of_directions

    theta = 0
    k = 0
    r = 0

    while True:
        accumulated_zenith_angle.insert(0, theta_i1)
        theta = theta_i1 - 2*math.sin(0.5*theta_i1)*math.sqrt(math.pi / float(k_i1))
        r = 2 * math.sin(0.5 * theta)
        k = int(k_i1 * (r / r_i1) * (r / r_i1))
        r = r_i1 * math.sqrt(k / float(k_i1))
        theta = 2 * math.asin(0.5 * r)

        numOfDirectionInSector = k_i1 - k
        aziInterval = 2 * math.pi / float(numOfDirectionInSector)
        azi_each_sector = []
        for i in range(0, numOfDirectionInSector):
            azimutStart = i*aziInterval
            azimutEnd = (i+1)*aziInterval
            solidAngle = math.pi * (r_i1 * r_i1 - r * r) / float(numOfDirectionInSector)
            azi_each_sector.append(azimutEnd)
        accumulated_azimuth_angle.insert(0, azi_each_sector)
        k_i1 = k
        r_i1 = r
        theta_i1 = theta
        if theta <= 0:
            break
    return accumulated_zenith_angle, accumulated_azimuth_angle


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", nargs="*", help="Input image file (ENVI standard format or tif)", required=True)
    parse.add_argument("-n", nargs="*", help="Number of directions", type=int, default=400)
    parse.add_argument("-o", help="Results stored in txt format", type=str, default="gaps.txt")
    args = parse.parse_args()

    start = time.perf_counter()  # start to record the time

    # Get all the input image files
    input_files = []
    for input_file in args.i:
        input_files += glob.glob(input_file)

    accumulated_zenith_angle, accumulated_azimuth_angle = generation_discrete_directions(args.n)
    gaps = []
    nums = []
    results = []
    for i in range(len(accumulated_zenith_angle)):
        gaps.append([0 for j in range(len(accumulated_azimuth_angle[i]))])
        nums.append([0 for j in range(len(accumulated_azimuth_angle[i]))])
        results.append([0 for j in range(len(accumulated_azimuth_angle[i]))])

    f_out = open(args.o, 'w')
    for input_file in input_files:
        ds = gdal.Open(input_file)
        if ds is not None:
            f_out.write(input_file+"\n")
            band = ds.GetRasterBand(1)
            band_data = band.ReadAsArray(0, 0, band.XSize, band.YSize)
            band_data = band_data > -1
            res_inv_x = 1.0/float(band.XSize)
            res_inv_y = 1.0/float(band.YSize)
            coords_cols, coords_rows = np.meshgrid(np.arange(band.XSize), np.arange(band.YSize))
            coords_x, coords_y = coords_cols*res_inv_x, coords_rows*res_inv_y
            dist = np.sqrt((coords_x - 0.5) * (coords_x - 0.5) + (coords_y - 0.5) * (coords_y - 0.5))
            SQRT_TWO = 1.414213562
            theta = 2 * np.arcsin(SQRT_TWO * dist)
            phi = np.arctan2(0.5 - coords_y, coords_x - 0.5)
            phi = 0.5*np.pi-phi
            phi[phi < 0] = phi[phi < 0] + 2*np.pi

            for row in range(band.YSize):
                for col in range(band.XSize):
                    pixel_val = band_data[row][col]
                    theta_val = theta[row][col]
                    phi_val = phi[row][col]
                    thetaIndex = 0
                    if theta_val <= 0.5*np.pi:
                        for i in range(len(accumulated_zenith_angle)):
                            if theta_val <= accumulated_zenith_angle[i]:
                                thetaIndex = i
                                break
                        aziInterval = np.pi * 2 / float(len(accumulated_azimuth_angle[thetaIndex]))
                        aziIndex = int(phi_val / aziInterval)
                        if (0 <= thetaIndex < len(accumulated_zenith_angle)) \
                                and (0 <= aziIndex < len(gaps[thetaIndex])):
                            gaps[thetaIndex][aziIndex] += pixel_val
                            nums[thetaIndex][aziIndex] += 1
            for i in range(len(gaps)):
                for j in range(len(gaps[i])):
                    results[i][j] = 1-float(gaps[i][j])/float(nums[i][j])

            # output results
            accumulated_zenith_angle.insert(0, 0)
            for i in range(len(gaps)):
                accumulated_azimuth_angle[i].insert(0, 0)
            for i in range(1, len(accumulated_zenith_angle)):
                for j in range(1, len(accumulated_azimuth_angle[i-1])):
                    f_out.write("%.2f %.2f " % (accumulated_zenith_angle[i-1]/np.pi*180,
                                                accumulated_zenith_angle[i]/np.pi*180))
                    f_out.write("%.2f %.2f " % (accumulated_azimuth_angle[i - 1][j-1]/np.pi*180,
                                                accumulated_azimuth_angle[i-1][j]/np.pi*180))
                    f_out.write("%.3f\n" % results[i-1][j-1])
            f_out.close()
