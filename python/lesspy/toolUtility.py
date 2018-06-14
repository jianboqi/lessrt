#coding: utf-8
from session import *
from RasterHelper import *
import os
import math


def generate_brf_multiscene():
    # read BRF
    irradiance_file = "E:\Coding\Mitsuba\simulations\RAMI4new\output\Irradiance.txt"
    f = open(irradiance_file)
    lines = f.readlines()
    sun = map(lambda x: float(x), lines[0].replace("\n", "").strip().split(" ")[1:])
    sky = map(lambda x: float(x), lines[1].replace("\n", "").strip().split(" ")[1:])
    total = map(lambda x, y: x+y, sun, sky)
    outputdir = r"E:\Coding\Mitsuba\simulations\RAMI4new\output"
    outputdir = unicode(outputdir, "utf8")
    for filename in os.listdir(outputdir):
        filepath = outputdir+"\\"+filename
        if os.path.isfile(filepath):
            if filename.startswith("m_") and not filename.endswith(".hdr"):
                arr = filename.split("_")
                if arr[2] == "VA":
                    azimuth = arr[3]
                    zenith = arr[6]
                elif arr[2] == "VZ":
                    zenith = arr[3]
                    azimuth = arr[6]
                output = "VA "+str(azimuth) + " VZ " +str(zenith) + " "
                dataset = gdal.Open(filepath)
                for i in range(1, dataset.RasterCount+1):
                    band = dataset.GetRasterBand(i)
                    data_arr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
                    data_arr = data_arr[data_arr > 0]
                    data_arr = data_arr[data_arr < 7]
                    output += str(data_arr.mean() / float(total[i-1]) * math.pi) + " "
                print(output)

def generate_brf_seq():
    outputdir = session.get_output_dir()
    for filename in os.listdir(outputdir):
        filepath = outputdir+filename
        if os.path.isfile(filepath):
            if filename.startswith("Spectralseq_") and not filename.endswith(".hdr"):
                w,h,reddata = RasterHelper.read_as_array(filepath,1)
                w, h,nirdata = RasterHelper.read_as_array(filepath, 2)
                arr = filename.split("_")
                if arr[2] == "azimuth":
                    azimuth = arr[3]
                    zenith = arr[6]
                elif arr[2] == "zenith":
                    zenith = arr[3]
                    azimuth = arr[6]
                reddata = reddata[reddata>0]
                nirdata = nirdata[nirdata > 0]
                print(azimuth, zenith, reddata.mean(),nirdata.mean())

def generate_brf():
    outputdir = session.get_output_dir()
    f = open(combine_file_path(outputdir, "cmd.txt"), 'a')
    for filename in os.listdir(outputdir):
        filepath = combine_file_path(outputdir, filename)
        if os.path.isfile(filepath):
            if filename.startswith("spectral_") and not filename.endswith(".hdr") and not filename.endswith(".png") \
                    and not filename.endswith(".jpg"):
                w, h, red = RasterHelper.read_as_array(filepath, 1)
                w, h, nir = RasterHelper.read_as_array(filepath, 2)
                red = red[red > 0]
                nir = nir[nir > 0]
                print("RED, NIR: ", red.mean(), nir.mean())
                f.write(str(red.mean())+" "+str(nir.mean())+"\n");
    f.close()

if __name__ == "__main__":
    generate_brf_multiscene()

