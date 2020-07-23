# coding: utf-8
# Author: Jianbo Qi
# Date: 2020/7/6
import os
import shutil
import gdal
import math
import sys


class PostProcessing:
    @staticmethod
    def readIrr(irrFilePath):
        # read irrfile
        f = open(irrFilePath)
        index = 0
        sunirr = []
        skyirr = None
        for line in f:
            if index == 1:
                arr = line.replace("\n", "").strip().split(" ")
                sunirr = list(map(lambda x: float(x), arr[1:]))
            if index == 2:
                arr = line.replace("\n", "").strip().split(" ")
                skyirr = list(map(lambda x: float(x), arr[1:]))
            index = index + 1

        if skyirr is not None:
            sunirr = list(map(lambda x, y: x + y, sunirr, skyirr))
        f.close()
        return sunirr

    @staticmethod
    def brf_single_img_processing(radianceFilePath, sunirr, outFilePath):
        dataset = gdal.Open(radianceFilePath)
        band_num = dataset.RasterCount
        XSize, YSize = dataset.RasterXSize, dataset.RasterYSize

        format = "ENVI"
        driver = gdal.GetDriverByName(format)
        dst_ds = driver.Create(outFilePath, XSize, YSize, band_num, gdal.GDT_Float32)
        meanBRFs = []
        for i in range(0, band_num):
            band = dataset.GetRasterBand(i + 1)
            dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
            dataarr = dataarr / sunirr[i] * math.pi
            dst_ds.GetRasterBand(i + 1).WriteArray(dataarr)
            tmp = dataarr[dataarr >= 0]
            meanBRF = tmp.mean()
            meanBRFs.append(meanBRF)
        dst_ds = None
        # processing header
        shutil.copy(radianceFilePath + ".hdr", outFilePath + ".hdr")

        return meanBRFs

    @staticmethod
    def radiance2brf(sim_dir, input_radiace_file="", output_brf_file=""):
        if input_radiace_file != "" and output_brf_file != "":
            sunirr = PostProcessing.readIrr(os.path.join(sim_dir, "Results", "Irradiance.txt"))
            if input_radiace_file == "" or output_brf_file == "":
                return
            else:
                if os.path.exists(input_radiace_file):
                    meanBRFs = PostProcessing.brf_single_img_processing(input_radiace_file, sunirr, output_brf_file)
        elif input_radiace_file == "" and output_brf_file == "":
            spectral_info_path = os.path.join(sim_dir, "Results", "spectral.txt")
            if os.path.exists(spectral_info_path):
                fs = open(spectral_info_path, "r")
                f = open(os.path.join(sim_dir, "Results", "spectral_BRF.txt"), 'w')
                sunirr = PostProcessing.readIrr(os.path.join(sim_dir, "Results", "Irradiance.txt"))
                for line in fs:
                    radiance_path = os.path.join(sim_dir, "Results", line)
                    if os.path.exists(radiance_path):
                        print("INFO: Processing Image: " + line)
                        output_file = radiance_path + "_BRF"
                        meanBRFs = PostProcessing.brf_single_img_processing(radiance_path, sunirr,
                                                                            output_file)  # mean BRF for each band
                        f.write(line + " ")
                        for i in range(0, len(meanBRFs)):
                            f.write("%.5f " % meanBRFs[i])
                        f.write("\n")
                f.close()
        else:
            print("Error: input or output file is not specified.")
            sys.exit()
