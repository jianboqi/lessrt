# extract landcover types from single band image
import argparse
import gdal
import numpy as np

def extractLandcover(inputfile):
    dataset = gdal.Open(inputfile)
    band = dataset.GetRasterBand(1)
    arr = band.ReadAsArray(0, 0, band.XSize,band.YSize)
    types = np.unique(arr)
    typestr = ""
    for i in types:
        print("LandCoverTypes:" + str(i))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input image file.",required=True)
    args = parser.parse_args()
    extractLandcover(args.i)