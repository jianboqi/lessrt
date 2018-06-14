# coding: utf-8

import numpy as np
import math
import os,sys
import argparse

def read_single_layer_file(rami_path, obj_path, leaf_radius=0.05):
    fref = open(rami_path, 'r')
    s = np.pi * leaf_radius * leaf_radius
    fptop = open(obj_path, 'w')
    print("componentName:" + obj_path)
    r = math.sqrt(s)
    p0 = np.array([[r, r, 0], [r, -r, 0], [-r, -r, 0], [-r, r, 0]])
    topcount = 0
    for line in fref:
        leaf = line.split(' ')
        D = [float(x) for x in leaf[4:7]]
        v = math.sqrt(D[1] * D[1] + D[2] * D[2])
        Rx = np.array([[1, 0, 0], [0, D[2] / v, -D[1] / v], [0, D[1] / v, D[2] / v]])
        Ry = np.array([[v, 0, -D[0]], [0, 1, 0], [D[0], 0, v]])
        R = np.dot(Ry, Rx)
        p = np.dot(p0, R)
        c = [float(x) for x in leaf[1:4]]
        topcount += 1
        for k in range(0, 4):
            fptop.write(
                "v " + "%.6f" % (p[k, 0] / 2.0 + c[0]) + " " + "%.6f" % (p[k, 2] / 2.0 + c[2]) + " " + "%.6f" % (
                    p[k, 1] / 2.0 + c[1]) + "\n")

    for i in range(0, topcount):
        fptop.write("f " + str(i * 4 + 1) + " " + str(i * 4 + 2) + " " + str(i * 4 + 3) + " " + str(i * 4 + 4) + "\n")
    fptop.close()


def read_double_layer_file(first_layer_name, rami_path, obj_path, leaf_radius=0.05):

    fref = open(rami_path, 'r')
    s = np.pi * leaf_radius * leaf_radius
    r = math.sqrt(s)
    p0 = np.array([[r, r, 0], [r, -r, 0], [-r, -r, 0], [-r, r, 0]])

    fptop = open(first_layer_name + "_" + obj_path, 'w')
    print("componentName:"+first_layer_name + "_" + obj_path)
    sys.stdout.flush()
    topcount = 0
    pre_name = first_layer_name
    index = 0
    for line in fref:
        leaf = line.strip().split()
        layerName = leaf[0]
        if pre_name != layerName:
            for i in range(0, topcount):
                fptop.write(
                    "f " + str(i * 4 + 1) + " " + str(i * 4 + 2) + " " + str(i * 4 + 3) + " " + str(i * 4 + 4) + "\n")
            fptop.close()
            fptop = open(layerName + "_" + obj_path, 'w')
            print("componentName:"+layerName + "_" + obj_path)
            sys.stdout.flush()
            pre_name = layerName
            topcount = 0

        D = [float(x) for x in leaf[5:8]]
        v = math.sqrt(D[1] * D[1] + D[2] * D[2])
        if v == 0:
            v = 0.00000001
        Rx = np.array([[1, 0, 0], [0, D[2] / v, -D[1] / v], [0, D[1] / v, D[2] / v]])
        Ry = np.array([[v, 0, -D[0]], [0, 1, 0], [D[0], 0, v]])
        R = np.dot(Ry, Rx)
        p = np.dot(p0, R)
        c = [float(x) for x in leaf[2:5]]
        topcount += 1
        for k in range(0, 4):
            fptop.write(
                "v " + "%.6f" % (p[k, 0] / 2.0 + c[0]) + " " + "%.6f" % (p[k, 2] / 2.0 + c[2]) + " " + "%.6f" % (
                    p[k, 1] / 2.0 + c[1]) + "\n")

    for i in range(0, topcount):
        fptop.write(
            "f " + str(i * 4 + 1) + " " + str(i * 4 + 2) + " " + str(i * 4 + 3) + " " + str(i * 4 + 4) + "\n")
    fptop.close()


def rami2obj(rami_path, obj_path, leaf_radius=0.05):


    """
    convert RAMI scene file into .obj file
    Args:
        rami_path: the file path of rami file
        obj_path: generated obj file path
        leaf_radius:
    Returns:
        Number of converted leaves.
    """
    fref = open(rami_path,'r')

    first_line = fref.readline().strip()
    fref.close()
    arr = first_line.split()
    if len(arr) == 7:  # single layer
        leaf_radius = float(arr[0])
        read_single_layer_file(rami_path, obj_path, leaf_radius)
    if len(arr) == 8:  # double layer
        leaf_radius = float(arr[1])
        read_double_layer_file(arr[0], rami_path, obj_path, leaf_radius)




def runTaskFuncFromDir(srcDir, targetDir, func):
    """
        对srcDir中的每一个文件，执行函数func,结果放在targetDir中
    """
    inputfiles = os.listdir(srcDir)
    for inputfile in inputfiles:
        filepath = srcDir + os.sep + inputfile
        targetFilepath = targetDir + os.sep + inputfile + ".obj"
        func(filepath, targetFilepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input def file.")
    parser.add_argument("-o", help="Output obj file.")
    args = parser.parse_args()
    rami2obj(args.i, args.o)

