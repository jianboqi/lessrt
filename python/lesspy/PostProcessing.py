#coding:utf-8

# generate products, such as BRF

import argparse
import gdal
import math
from session import session
import os
import sys
import glob
from Constant import irradiance_file,BATCH_INFO_FILE,spectral_info_file,wavelength_file_for_thermal
from Loger import log
import shutil
from Utils import planck_invert
import argparse


def brf_single_img_processing(radianceFilePath, sunirr, outFilePath):
    dataset = gdal.Open(radianceFilePath)
    band_num = dataset.RasterCount
    XSize, YSize = dataset.RasterXSize,dataset.RasterYSize

    format = "ENVI"
    driver = gdal.GetDriverByName(format)
    dst_ds = driver.Create(outFilePath, XSize, YSize, band_num, gdal.GDT_Float32)
    meanBRFs = []
    for i in range(0, band_num):
        band = dataset.GetRasterBand(i+1)
        dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
        dataarr = dataarr/sunirr[i]*math.pi
        dst_ds.GetRasterBand(i + 1).WriteArray(dataarr)
        tmp = dataarr[dataarr>=0]
        meanBRF = tmp.mean()
        meanBRFs.append(meanBRF)
    dst_ds = None
    # processing header
    shutil.copy(radianceFilePath+".hdr", outFilePath+".hdr")

    return meanBRFs


# processing single image: calculate temperature,
def bt_single_img_processing(radianceFilePath, wavelengths):
    dataset = gdal.Open(radianceFilePath)
    band_num = dataset.RasterCount
    meanBTs = []
    for i in range(0, band_num):
        band = dataset.GetRasterBand(i + 1)
        dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
        tmp = dataarr[dataarr >= 0]
        meanRadiance = tmp.mean()
        meanBT = planck_invert(meanRadiance,wavelengths[i])
        meanBTs.append(meanBT)
    return meanBTs


# only contains one simulation
def readIrr(irrFilePath):
    # read irrfile
    f = open(irrFilePath)
    index = 0
    sunirr=[]
    skyirr = []
    for line in f:
        if index == 1:
            arr = line.replace("\n","").strip().split(" ")
            sunirr = list(map(lambda x:float(x), arr[1:]))
        if index == 2:
            arr = line.replace("\n","").strip().split(" ")
            skyirr = list(map(lambda x:float(x),arr[1:]))
        index = index + 1

    if skyirr != []:
        sunirr = list(map(lambda x,y:x+y,sunirr,skyirr))
    f.close()
    return sunirr


# e.g. samples_Irradiance.txt contains a seq of simulations
def read_irr_for_seq(seq_name):
    irr_map = dict() # [seq_name->[boa_band1, boa_band2,...]]
    f = open(os.path.join(session.get_output_dir(),seq_name+"_"+irradiance_file))
    current_seq = ""
    for line in f:
        if line.startswith(seq_name): #
            current_seq = line.strip()
            irr_map[current_seq] = []
        else:
            arr = line.replace("\n", "").strip().split(" ")
            irr = list(map(lambda x: float(x), arr[1:]))
            if len(irr_map[current_seq]) == 0:
                irr_map[current_seq] = irr
            else:
                irr_map[current_seq] = list(map(lambda x,y:x+y,irr,irr_map[current_seq]))
    return irr_map


parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type', help="Product Type.", type=str)
parser.add_argument('-f', '--file', help="info filename.", type=str)
args = parser.parse_args()
# processing thermal products
if args.type in ("T", "BT", "thermal"):
    # read wavelengths
    ft = open(os.path.join(session.get_output_dir(), wavelength_file_for_thermal))
    wavelengths = list(map(lambda x:float(x),ft.readline().split(",")))
    ft.close()
    seq_info_files = glob.glob(os.path.join(session.get_output_dir(), "*" + BATCH_INFO_FILE))
    for seq_file in seq_info_files:
        seq_name = os.path.splitext(os.path.basename(seq_file))[0].rsplit("_", 1)[0]
        log("INFO: Processing Batch: " + seq_name)
        f = open(seq_file)
        fbt = open(os.path.join(session.get_output_dir(), seq_name + "_BT.txt"), 'w')
        for line in f:
            arr = line.strip().split()
            radiance_file = arr[0]  # 实际上为当个模拟的名称
            radiance_path = os.path.join(session.get_output_dir(), radiance_file)
            meanBTs = bt_single_img_processing(radiance_path,wavelengths)
            fbt.write(radiance_file + " ")
            for i in range(0, len(meanBTs)):
                fbt.write("%.5f " % meanBTs[i])
            fbt.write("\n")
        fbt.close()
        f.close()

if args.type == "brf" or args.type == "BRF":
    # read sequence info file to process
    seq_info_files = glob.glob(os.path.join(session.get_output_dir(), "*"+BATCH_INFO_FILE))
    for seq_file in seq_info_files:
        seq_name = os.path.splitext(os.path.basename(seq_file))[0].rsplit("_", 1)[0]
        log("INFO: Processing Batch: " + seq_name)
        irr_map = read_irr_for_seq(seq_name)
        f = open(seq_file)
        fbrf = open(os.path.join(session.get_output_dir(), seq_name+"_BRF.txt"),'w')
        for line in f:
            arr = line.strip().split()
            radiance_file = arr[0]  # 实际上为当个模拟的名称
            sunirr = irr_map[radiance_file]
            radiance_path = os.path.join(session.get_output_dir(), radiance_file)
            out_BRF_File = os.path.join(session.get_output_dir(), radiance_file+"_BRF")
            meanBRFs = brf_single_img_processing(radiance_path, sunirr, out_BRF_File) # mean BRF for each band
            fbrf.write(radiance_file + " ")
            for i in range(0, len(meanBRFs)):
                fbrf.write("%.5f "%meanBRFs[i])
            fbrf.write("\n")
        fbrf.close()
        f.close()

    # processing Spectral Image
    spectral_info_path = os.path.join(session.get_output_dir(), spectral_info_file)
    if os.path.exists(spectral_info_path):
        fs = open(spectral_info_path, "r")
        f = open(os.path.join(session.get_output_dir(), "spectral_BRF.txt"), 'w')
        sunirr = readIrr(os.path.join(session.get_output_dir(), irradiance_file))
        for line in fs:
            radiance_path = os.path.join(session.get_output_dir(), line)
            if os.path.exists(radiance_path):
                log("INFO: Processing Image: " + line)
                output_file = radiance_path + "_BRF"
                meanBRFs = brf_single_img_processing(radiance_path, sunirr, output_file)  # mean BRF for each band
                f.write(line + " ")
                for i in range(0, len(meanBRFs)):
                    f.write("%.5f " % meanBRFs[i])
                f.write("\n")
        f.close()
    log("INFO: Finished.")
