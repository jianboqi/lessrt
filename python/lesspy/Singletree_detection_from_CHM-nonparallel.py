#coding: utf-8
import gdal
import mahotas
import math
import numpy as np
import random
import sys
import argparse
import joblib
import tempfile

def log(*args):
    outstr = ""
    for i in args:
        outstr += str(i)
    print outstr
    sys.stdout.flush()

def sub_fun():
    pass


# extract tree position from chm map using watershed transform.
#  the output is the tree position
#  coordinates of the tree position is either pixel value or real distance defined by real_coordinate
#  origin is left up corner, x increase from left to right, y increase from up to down.
# if output_path is provided (as file path), then the results will be written as assi file
# obj_num how many obj file are intend to use to generate forest scene
def getTreeLocAndHeight(chm_hdr_path,out_file, obj_list, subregion = 0, real_coordinate=True):
    idata_set = gdal.Open(chm_hdr_path)
    transform = idata_set.GetGeoTransform()
    if transform is None:
        log("ERROR: No geotransform found for file ", chm_hdr_path)
        return

    objList = obj_list.strip().split("*")
    obj_num = len(objList)

    pixel_size = abs(transform[1])

    band = idata_set.GetRasterBand(1)
    banddata = band.ReadAsArray(0, 0, band.XSize, band.YSize)
    width = band.XSize  # XSize是列数, YSize是行数
    height = band.YSize
    if(subregion == 0):
        subregion = max(width, height)
    num_width = int(math.ceil(width/float(subregion)))
    num_height = int(math.ceil(height/float(subregion)))
    result = []
    treeCount = 0
    for num_r in range(0, num_height): # row
        for num_c in range(0, num_width): #col
            log("INFO: Region: " + str(num_r) + " " + str(num_c))
            row_start = num_r*subregion
            row_end = min((num_r+1)*subregion, height)
            col_start = num_c*subregion
            col_end = min((num_c+1)*subregion, width)
            offset_x = num_c*subregion*pixel_size
            offset_y = num_r*subregion*pixel_size

            nuclear = banddata[row_start:row_end, col_start:col_end]
            threshed = (nuclear > 3)
            nuclear *= threshed
            bc = np.ones((3, 3))

            maxima = mahotas.morph.regmax(nuclear, Bc=bc)
            spots, n_spots = mahotas.label(maxima)

            surface = (nuclear.max() - nuclear)
            areas = mahotas.cwatershed(surface, spots)
            areas *= threshed
            area_max = areas.max()
            # seg_size = args.seg_size  # 500000 points for each core, parallel
            # seg_num = int(math.ceil(area_max / float(seg_size)))
            print area_max
            # 每棵树用不用的数值标记
            for i in range(1, areas.max()):
                if i % 1000 == 0:
                    log("INFO: Detected Trees: " + str(i))
                treepixel = np.where(areas == i)
                tmpmax = 0
                tx, ty = 0, 0
                tmp = 0
                # crown = math.sqrt(len(treepixel[0]) * pixel_size * pixel_size) * 2
                # tx,ty = sum(treepixel[0])/float(len(treepixel[0])),sum(treepixel[1])/float(len(treepixel[1]))
                for m in range(0, len(treepixel[0])):
                    tmp += 1
                    if nuclear[treepixel[0][m]][treepixel[1][m]] > tmpmax:
                        tmpmax = nuclear[treepixel[0][m]][treepixel[1][m]]
                        tx, ty = treepixel[0][m], treepixel[1][m]
                # maxHeight = nuclear[tx, ty]
                if real_coordinate:
                    x = offset_x + ty * pixel_size
                    y = offset_y + tx * pixel_size
                    result.append([random.randint(0, obj_num - 1), x, y])
                else:
                    result.append([random.randint(0, obj_num - 1), tx, ty])

    if out_file == "":
        from session import session
        import os
        out_file = os.path.join(session.get_input_dir(), "instances.txt")
    log("INFO: Total detected trees: ", treeCount)
    fw = open(out_file, 'w')
    for i in range(0,len(result)):
        outstr = objList[result[i][0]]+" "+str(result[i][1])+" "+str(result[i][2])
        fw.write(outstr+"\n")
    fw.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input CHM file.")
    parser.add_argument("-o", help="Output file.",default="")
    parser.add_argument("-l", help="Object list.")
    parser.add_argument("-seg_size", help="Tree number for each core. ", type=int, default=1000)
    args = parser.parse_args()
    getTreeLocAndHeight(args.i, args.o, args.l)