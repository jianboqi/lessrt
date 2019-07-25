# coding: utf-8
###################
# author: Jianbo QI
# Date: 2019-6-29
###################
# Calculate directional Gap probability from four components image products
# produced by LESS Model
##################
# Usage:
# [Path to where LESS is installed]/app/bin/python/python.exe DirectionalGapProb.py
# -i [path to image file] -o [path to output file]
# Please note: [path to image file] can be either: (1) path1 path2 path3; or (2) path*
#################

import argparse
import glob
import time
from osgeo import gdal
import sys


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", nargs="*", help="Input image file (ENVI standard format or tif)", required=True)
    parse.add_argument("-o", help="Results stored in txt format",
                       required=True, type=str, default="gap.txt")
    args = parse.parse_args()

    start = time.perf_counter()  # start to record the time

    # Get all the input image files
    input_files = []
    for input_file in args.i:
        input_files += glob.glob(input_file)

    # Processing all the input image files
    f_out = open(args.o, 'w')
    for input_file in input_files:
        ds = gdal.Open(input_file)
        if ds is not None:
            band_num = ds.RasterCount
            if band_num < 5:
                print(" -ERROR: Please set the number of bands larger than 5")
                sys.exit(0)
            band2 = ds.GetRasterBand(2)
            band2 = band2.ReadAsArray(0, 0, band2.XSize, band2.YSize)
            band4 = ds.GetRasterBand(4)
            band4 = band4.ReadAsArray(0, 0, band4.XSize, band4.YSize)
            band = band2 + band4
            band = band[((band >= 0) & (band <= 1))]
            mean_value = band.mean()
            f_out.write("%s %.4f\n" % (input_file, mean_value))
        else:
            print(" - ERROR: Can not open file: ", input_file)
            sys.exit(0)
    f_out.close()

    end = time.process_time()  # end
    print(" - Time: ", "%.3fs" % (end - start))




