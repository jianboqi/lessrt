"""
Convert raster to obj
author: Jianbo Qi
This is for LESS
2017.5.24
"""

import argparse
from osgeo import gdal
import numpy as np
import math
# import mahotas


# approximate the terrain with 256*256 meshes for 3D display
def approximate_terrain_with_mesh(rasterfile, dist_obj_file, xExtend=-1, zExtend=-1):
    dataset = gdal.Open(rasterfile)
    band = dataset.GetRasterBand(1)
    XSize = band.XSize  # width
    YSize = band.YSize  # height
    dst_w, dst_h = XSize, YSize

    if xExtend == -1 or zExtend == -1:
        transform = dataset.GetGeoTransform()
        if not transform is None:
            pixel_x = abs(transform[1])
            pixel_y = abs(transform[5])
        else:
            print("no geo transform.")
            return
        xExtend = XSize * pixel_x
        zExtend = YSize * pixel_y
    else:
        pixel_x = xExtend/float(XSize)
        pixel_y = zExtend/float(YSize)

    while dst_w > 256 and dst_h>256:
        dst_w = max(dst_w/2,2)
        dst_h = max(dst_h/2,2)

    dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
    dataarr = dataarr - dataarr.min()

    dst_w = int(dst_w)
    dst_h = int(dst_h)

    scale_x = XSize/float(dst_w-1)
    scale_y = YSize/float(dst_h-1)
    f = open(dist_obj_file,'w')
    for row in range(0, int(dst_h)):
        origin_row = min(int(scale_y*row), YSize-1)
        for col in range(0, int(dst_w)):
            origin_col = min(int(scale_x * col), XSize - 1)
            altitude = dataarr[origin_row][origin_col]
            z = zExtend * 0.5 - origin_row * pixel_y
            x = xExtend * 0.5 - origin_col * pixel_x
            y = altitude
            vstr = "v " + str(x) + " " + str(y) + " " + str(z) + "\n"
            f.write(vstr)

    for row in range(0, int(dst_h-1)):
        for col in range(0, int(dst_w-1)):
            index_left_upper = dst_w*row+col+1
            index_right_upper = dst_w * row + col + 2
            index_left_down = dst_w * (1+row) + col + 1
            index_right_down = dst_w * (1+row) + col + 2
            vstr = "f " + str(index_left_upper) + " " +\
                   str(index_left_down) + " " +\
                   str(index_right_down) + " " +\
                   str(index_right_upper)+ "\n"
            f.write(vstr)
    f.close()


# resize image using pixel agraggate
# this function is not efficent, it is depressed.
def resize_img(dataarr,dst_w,dst_h,o_resolution_x, o_resolution_y):
    size = dataarr.shape
    origin_width = size[1]
    origin_height = size[0]
    origin_res_X = o_resolution_x
    origin_res_Y = o_resolution_y
    adjusted_res_X = origin_res_X*origin_width/float(dst_w)
    adjusted_res_Y = origin_res_X*origin_height/float(dst_h)

    # scale = float(max(dst_w, dst_h))/float(max(origin_width, origin_height))
    # print scale
    # resized_img = mahotas.imresize(dataarr, scale,2)
    # return resized_img, adjusted_res_X, adjusted_res_X
    result = np.zeros((dst_h, dst_w))
    for i in range(0, dst_w):
        print(i)
        pre_coord_X = i* adjusted_res_X
        pre_int_pos_X = int(math.ceil(pre_coord_X / origin_res_X))
        pre_x_factor = (pre_int_pos_X * origin_res_X - pre_coord_X) / origin_res_X
        next_coord_X = (i+1) * adjusted_res_X
        next_int_pos_X = int(math.ceil(next_coord_X / origin_res_X - 0.00000000001))
        next_x_factor = (next_coord_X - (next_int_pos_X - 1) * origin_res_X) / origin_res_X

        for j in range(0, dst_h):
            pre_coord_Y = j * adjusted_res_Y
            pre_int_pos_Y = int(math.ceil(pre_coord_Y / origin_res_Y))
            pre_y_factor = (pre_int_pos_Y * origin_res_Y - pre_coord_Y) / origin_res_Y
            next_coord_Y = (j+1) * adjusted_res_Y
            next_int_pos_Y = int(math.ceil(next_coord_Y / origin_res_Y - 0.00000000001))
            next_y_factor = (next_coord_Y - (next_int_pos_Y - 1) * origin_res_Y) / origin_res_Y
            total = 0
            complete_pixels = dataarr[pre_int_pos_Y:next_int_pos_Y-1, pre_int_pos_X:next_int_pos_X-1]
            total += complete_pixels.mean()#(complete_pixels*origin_res_X*origin_res_Y).sum()

            if pre_int_pos_Y > 0:
                complete_pixels = dataarr[pre_int_pos_Y-1, pre_int_pos_X:next_int_pos_X-1]
                total = total + complete_pixels.sum() * origin_res_X * origin_res_Y * pre_y_factor

            complete_pixels = dataarr[next_int_pos_Y-1, pre_int_pos_X :next_int_pos_X-1]
            total = total + complete_pixels.sum() * origin_res_X * origin_res_Y * next_y_factor

            if pre_int_pos_X > 0:
                complete_pixels = dataarr[pre_int_pos_Y:next_int_pos_Y-1, pre_int_pos_X-1]
                total = total + dataarr.sum() * origin_res_X * origin_res_Y * pre_x_factor

            complete_pixels = dataarr[pre_int_pos_Y:next_int_pos_Y-1, next_int_pos_X-1]
            total = total + complete_pixels.sum() * origin_res_X * origin_res_Y * next_x_factor

            if pre_int_pos_Y > 0 and pre_int_pos_X > 0:
                total = total + pre_x_factor * pre_y_factor * origin_res_X * origin_res_Y * dataarr[pre_int_pos_Y-1, pre_int_pos_X-1]

            if pre_int_pos_Y > 0:
                total = total + next_x_factor * pre_y_factor * origin_res_X * origin_res_Y * dataarr[pre_int_pos_Y, next_int_pos_X-1]

            if pre_int_pos_X > 0:
                total = total + pre_x_factor * next_y_factor * origin_res_X * origin_res_Y * dataarr[next_int_pos_Y-1, pre_int_pos_X]

            total = total + next_x_factor * next_y_factor * origin_res_X * origin_res_Y * dataarr[next_int_pos_Y-1, next_int_pos_X-1]

            total = total/float(adjusted_res_X*adjusted_res_Y)
            result[j][i] = total
    return result,adjusted_res_X,adjusted_res_X


parser = argparse.ArgumentParser()
parser.add_argument("-i", help="Input Raster file (ENVI or tiff", required=True)
parser.add_argument("-o", help="Output OBJ file.")
parser.add_argument("-X", help="xExtend.", type=float, default=-1)
parser.add_argument("-Z", help="zExtend.", type=float, default=-1)
args = parser.parse_args()

rasterfile = args.i
dist_obj_file = args.o

approximate_terrain_with_mesh(rasterfile, dist_obj_file, args.X, args.Z)


# The following code is convert DEM to obj file pixel by pixel.
# When there is empty pixels, this can avoid them. by it is low performance for large DEM files

# dataset = gdal.Open(rasterfile)
# band = dataset.GetRasterBand(1)
# transform = dataset.GetGeoTransform()
# if not transform is None:
#     pixel_x = abs(transform[1])
#     pixel_y = abs(transform[5])
# else:
#     print "no geo transform."
# XSize = band.XSize  # width
# YSize = band.YSize  # height
# xExtend = XSize * pixel_x
# zExtend = YSize * pixel_y
# # save to openexr file
#
# dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
# dataarr = dataarr - dataarr.min()
#
# vertex_list = []
# facet_list = []
# height_list = []
# vertex_dict = dict()
# index = 0
# for i in range(0, YSize):
#     for j in range(0, XSize):
#         pixel_value = dataarr[i][j]
#         facet = []
#         if pixel_value > 0:  # record the vertex
#             left_up_corner = [i, j]
#             str_index = str(i)+"_"+str(j)
#             if str_index not in vertex_dict:
#                 vertex_list.append(left_up_corner)
#                 index += 1
#                 vertex_dict[str_index] = index
#                 facet.append(index)
#                 height = pixel_value
#                 height_list.append(height)
#             else:
#                 facet.append(vertex_dict[str_index])
#
#             right_up_corner = [i, j+1]
#             str_index = str(i) + "_" + str(j+1)
#             if str_index not in vertex_dict:
#                 vertex_list.append(right_up_corner)
#                 index += 1
#                 vertex_dict[str_index] = index
#                 facet.append(index)
#                 height = dataarr[i][j + 1] if j < XSize - 1 and dataarr[i][j + 1] > 0 else pixel_value
#                 height_list.append(height)
#             else:
#                 facet.append(vertex_dict[str_index])
#
#             right_down_corner = [i + 1, j + 1]
#             str_index = str(i+1) + "_" + str(j + 1)
#             if str_index not in vertex_dict:
#                 vertex_list.append(right_down_corner)
#                 index += 1
#                 vertex_dict[str_index] = index
#                 facet.append(index)
#                 height = dataarr[i + 1][j + 1] if i < YSize - 1 and j < XSize - 1 and dataarr[i + 1][
#                                                                                           j + 1] > 0 else pixel_value
#                 height_list.append(height)
#             else:
#                 facet.append(vertex_dict[str_index])
#
#             left_down_corner = [i+1, j]
#             str_index = str(i + 1) + "_" + str(j)
#             if str_index not in vertex_dict:
#                 vertex_list.append(left_down_corner)
#                 index += 1
#                 vertex_dict[str_index] = index
#                 facet.append(index)
#                 height = dataarr[i + 1][j] if i < YSize - 1 and dataarr[i + 1][j] > 0 else pixel_value
#                 height_list.append(height)
#             else:
#                 facet.append(vertex_dict[str_index])
#             facet_list.append(facet)
#
# f = open(dist_obj_file, 'w')
# for i in range(0, len(vertex_list)):
#     z = zExtend*0.5 - vertex_list[i][0] * pixel_y
#     x = xExtend*0.5 - vertex_list[i][1] * pixel_x
#     y = height_list[i]
#     vstr = "v " + str(x) + " " + str(y) + " " + str(z) + "\n"
#     f.write(vstr)
#
# for i in range(0, len(facet_list)):
#     fstr = "f " + str(facet_list[i][3]) + " " + str(facet_list[i][2]) + " " + str(facet_list[i][1]) + " " + str(facet_list[i][0]) + "\n"
#     f.write(fstr)
# f.close()
#