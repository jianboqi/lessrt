"""
Convert raster to obj
author: Jianbo Qi
2017.5.24
This is for DART
"""

import argparse
from osgeo import gdal

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="Input Raster file (ENVI or tiff", required=True)
parser.add_argument("-o", help="Output OBJ file.")
args = parser.parse_args()

rasterfile = args.i
dist_obj_file = args.o


dataset = gdal.Open(rasterfile)
band = dataset.GetRasterBand(1)
transform = dataset.GetGeoTransform()
if not transform is None:
    pixel_x = abs(transform[1])
    pixel_y = abs(transform[5])
else:
    print "no geo transform."
XSize = band.XSize
YSize = band.YSize
xExtend = XSize * pixel_x
yExtend = YSize * pixel_y
# save to openexr file

dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
vertex_list = []
facet_list = []
height_list = []
vertex_dict = dict()
index = 0
for i in range(0, YSize):
    for j in range(0, XSize):
        pixel_value = dataarr[i][j]
        facet = []
        if pixel_value > 0:  # record the vertex
            left_up_corner = [i, j]
            str_index = str(i)+"_"+str(j)
            if str_index not in vertex_dict:
                vertex_list.append(left_up_corner)
                index += 1
                vertex_dict[str_index] = index
                facet.append(index)
                height = pixel_value
                height_list.append(height)
            else:
                facet.append(vertex_dict[str_index])

            right_up_corner = [i, j+1]
            str_index = str(i) + "_" + str(j+1)
            if str_index not in vertex_dict:
                vertex_list.append(right_up_corner)
                index += 1
                vertex_dict[str_index] = index
                facet.append(index)
                height = dataarr[i][j + 1] if j < XSize - 1 and dataarr[i][j + 1] > 0 else pixel_value
                height_list.append(height)
            else:
                facet.append(vertex_dict[str_index])

            right_down_corner = [i + 1, j + 1]
            str_index = str(i+1) + "_" + str(j + 1)
            if str_index not in vertex_dict:
                vertex_list.append(right_down_corner)
                index += 1
                vertex_dict[str_index] = index
                facet.append(index)
                height = dataarr[i + 1][j + 1] if i < YSize - 1 and j < XSize - 1 and dataarr[i + 1][
                                                                                          j + 1] > 0 else pixel_value
                height_list.append(height)
            else:
                facet.append(vertex_dict[str_index])

            left_down_corner = [i+1, j]
            str_index = str(i + 1) + "_" + str(j)
            if str_index not in vertex_dict:
                vertex_list.append(left_down_corner)
                index += 1
                vertex_dict[str_index] = index
                facet.append(index)
                height = dataarr[i + 1][j] if i < YSize - 1 and dataarr[i + 1][j] > 0 else pixel_value
                height_list.append(height)
            else:
                facet.append(vertex_dict[str_index])
            facet_list.append(facet)

f = open(dist_obj_file, 'w')
for i in range(0, len(vertex_list)):
    x = vertex_list[i][0] * pixel_y
    y = vertex_list[i][1] * pixel_x
    z = height_list[i]
    vstr = "v " + str(y) + " " + str(z) + " " + str(x) + "\n"
    f.write(vstr)

for i in range(0, len(facet_list)):
    fstr = "f " + str(facet_list[i][3]) + " " + str(facet_list[i][2]) + " " + str(facet_list[i][1]) + " " + str(facet_list[i][0]) + "\n"
    f.write(fstr)
f.close()
#
# for i in range(0, YSize):
#     for j in range(0, XSize):
#         if dataarr[i][j] > 0:
#             p1 = i * (XSize + 1) + j + 1
#             p2 = (i + 1) * (XSize + 1) + j + 1
#             p3 = (i + 1) * (XSize + 1) + j + 1 + 1
#             p4 = i * (XSize + 1) + j + 1 + 1
#             fstr = "f " + str(p1) + " " + str(p2) + " " + str(p3) + " " + str(p4) + "\n"
#             f.write(fstr)
# f.close()