#coding: utf-8

import argparse
import OpenEXR
from Constant import *
import numpy as np
import array, Imath
import shutil


# create land albedo map from input albedo map
def createLandAlbedoMap(band_num, landAlbedoRasterFile, out_exr_file):
    band_start = const.get_value("NO_BAND_WIDTH_MODE_BAND_START")
    band_end = const.get_value("NO_BAND_WIDTH_MODE_BAND_END")
    wavelengths = np.linspace(band_start, band_end, band_num + 1)

    import gdal
    dataset = gdal.Open(landAlbedoRasterFile)
    imgXsize = dataset.RasterXSize
    imgYSize = dataset.RasterYSize

    band_dict = dict()
    half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
    chaneldict = dict()
    for i in range(0, band_num):
        start = wavelengths[i]
        end = wavelengths[i + 1]
        band_name = "%.2f" % start + "-" + "%.2fnm" % end
        band = dataset.GetRasterBand(i+1)
        singleband = band.ReadAsArray(0, 0, imgXsize, imgYSize)
        singleband = np.fliplr(singleband)
        singleband = np.reshape(singleband, (imgXsize * imgYSize))
        radiance_str = array.array('f', singleband).tostring()  # generate arr
        band_dict[band_name] = radiance_str
        chaneldict[band_name] = half_chan
    header = OpenEXR.Header(imgXsize, imgYSize)
    header["channels"] = chaneldict
    out = OpenEXR.OutputFile(out_exr_file, header)
    out.writePixels(band_dict)

def get_nearest_theta_phi(theta, phi, theta_phi):
    arrlen = len(theta_phi)
    nearest_pos = min(range(arrlen), key=lambda i:(theta_phi[i][0]-theta)*(theta_phi[i][0]-theta) +
                                                  (theta_phi[i][1]-phi)* (theta_phi[i][1]-phi))
    return nearest_pos

def createLandcoverMap(landcoverRasterFile,out_exr_file, opticalFile, opticalTable, band_num):
    band_start = const.get_value("NO_BAND_WIDTH_MODE_BAND_START")
    band_end = const.get_value("NO_BAND_WIDTH_MODE_BAND_END")
    wavelengths = np.linspace(band_start, band_end, band_num + 1)
    # optical map
    f = open(opticalFile,'r')
    typeDict = dict()
    for line in f:
        arr = line.split(" ")
        tmp = opticalTable[arr[1].replace("\n","")].split(";")[0].split(",")
        optical = list(map(lambda x: float(x), tmp))
        typeDict[int(arr[0])] = optical
    import gdal
    dataset = gdal.Open(landcoverRasterFile)
    band = dataset.GetRasterBand(1)
    dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
    lc_map = np.zeros((band.YSize, band.XSize, band_num))
    for i in range(0, band.YSize):
        for j in range(0, band.XSize):
            lc_map[i, band.XSize - j - 1, :] = typeDict[dataarr[i][j]]
            # write this into exr file
    band_dict = dict()
    half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
    chaneldict = dict()
    for i in range(0, band_num):
        start = wavelengths[i]
        end = wavelengths[i + 1]
        band_name = "%.2f" % start + "-" + "%.2fnm" % end
        singleband = lc_map[:, :, i]
        singleband = np.reshape(singleband, (band.XSize * band.YSize))
        radiance_str = array.array('f', singleband).tostring()  # generate arr
        band_dict[band_name] = radiance_str
        chaneldict[band_name] = half_chan
    header = OpenEXR.Header(band.XSize, band.YSize)
    header["channels"] = chaneldict
    # if not isinstance(out_exr_file, str):
    #     # writing to a temperal place, since OpenEXR do not support unicode
    #     tmpExrPath = os.path.join(os.path.expanduser('~'), "_tmp_lc.exr")
    #     out = OpenEXR.OutputFile(tmpExrPath, header)
    #     out.writePixels(band_dict)
    #     out = None
    #     # copy back
    #     shutil.move(tmpExrPath, out_exr_file)
    # else:
    out = OpenEXR.OutputFile(out_exr_file, header)
    out.writePixels(band_dict)
    out = None

# just for test
def createLandcoverMap_trans(landcoverRasterFile,out_exr_file, opticalFile, opticalTable, band_num):
    band_start = const.get_value("NO_BAND_WIDTH_MODE_BAND_START")
    band_end = const.get_value("NO_BAND_WIDTH_MODE_BAND_END")
    wavelengths = np.linspace(band_start, band_end, band_num + 1)
    # optical map
    f = open(opticalFile,'r')
    typeDict = dict()
    for line in f:
        arr = line.split(" ")
        tmp = opticalTable[arr[1].replace("\n","")].split(";")[2].split(",")
        optical = list(map(lambda x: float(x), tmp))
        typeDict[int(arr[0])] = optical
    import gdal
    dataset = gdal.Open(landcoverRasterFile)
    band = dataset.GetRasterBand(1)
    dataarr = band.ReadAsArray(0,0, band.XSize, band.YSize)
    lc_map = np.zeros((band.YSize, band.XSize, band_num))
    for i in range(0, band.YSize):
        for j in range(0, band.XSize):
            lc_map[i, band.XSize - j - 1, :] = typeDict[dataarr[i][j]]
            # write this into exr file
    band_dict = dict()
    half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
    chaneldict = dict()
    for i in range(0, band_num):
        start = wavelengths[i]
        end = wavelengths[i + 1]
        band_name = "%.2f" % start + "-" + "%.2fnm" % end
        singleband = lc_map[:, :, i]
        singleband = np.reshape(singleband, (band.XSize * band.YSize))
        radiance_str = array.array('f', singleband).tostring()  # generate arr
        band_dict[band_name] = radiance_str
        chaneldict[band_name] = half_chan
    header = OpenEXR.Header(band.XSize, band.YSize)
    header["channels"] = chaneldict
    # if not isinstance(out_exr_file, str):
    #     # writing to a temperal place, since OpenEXR do not support unicode
    #     tmpExrPath = os.path.join(os.path.expanduser('~'), "_tmp_lc.exr")
    #     out = OpenEXR.OutputFile(tmpExrPath, header)
    #     out.writePixels(band_dict)
    #     out = None
    #     # copy back
    #     shutil.move(tmpExrPath, out_exr_file)
    # else:
    out = OpenEXR.OutputFile(out_exr_file, header)
    out.writePixels(band_dict)
    out = None

def create_isotropic_diffuse_sky(input_spectral_radiance, output_file, band_num):
    """
    input the spectral radiance
    """
    band_start = const.get_value("NO_BAND_WIDTH_MODE_BAND_START")
    band_end = const.get_value("NO_BAND_WIDTH_MODE_BAND_END")
    # band_num = const.get_value("NO_BAND_WIDTH_MODE_BAND_NUM")
    resolution_width = const.get_value("env_map_resolution")
    resolution_height = int(resolution_width / 2)
    wavelengths = np.linspace(band_start, band_end, band_num + 1)

    radiance_map = np.zeros((resolution_height, resolution_width, band_num))
    for i in range(0, resolution_height / 2):
        for j in range(0, resolution_width):
            radiance_map[i, j, :] = input_spectral_radiance

    # write this into exr file
    band_dict = dict()
    half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
    chaneldict = dict()
    for i in range(0, band_num):
        start = wavelengths[i]
        end = wavelengths[i + 1]
        band_name = "%.2f" % start + "-" + "%.2fnm" % end
        singleband = radiance_map[:, :, i]
        singleband = np.reshape(singleband, (resolution_width * resolution_height))
        radiance_str = array.array('f', singleband).tostring()  # generate arr
        band_dict[band_name] = radiance_str
        chaneldict[band_name] = half_chan
    header = OpenEXR.Header(resolution_width, resolution_height)
    header["channels"] = chaneldict
    if not isinstance(output_file, str):
        # writing to a temperal place, since OpenEXR do not support unicode
        tmpExrPath = os.path.join(os.path.expanduser('~'), "_tmp_sky.exr")
        out = OpenEXR.OutputFile(tmpExrPath, header)
        out.writePixels(band_dict)
        out = None
        # copy back
        shutil.move(tmpExrPath, output_file)
    else:
        out = OpenEXR.OutputFile(output_file, header)
        out.writePixels(band_dict)
        out = None

# just for test, support different values for different maps.
def create_class_map_reflectance(output_file):
    band_start = const.get_value("NO_BAND_WIDTH_MODE_BAND_START")
    band_end = const.get_value("NO_BAND_WIDTH_MODE_BAND_END")
    resolution_width = 2
    resolution_height = 2
    band_num = 5
    wavelengths = np.linspace(band_start, band_end, band_num + 1)
    radiance_map = np.zeros((resolution_height, resolution_width, band_num))
    for i in range(0, resolution_height / 2):  # upper
        for j in range(0, resolution_width):
            radiance_map[i, j, :] = [0.5, 0.4, 0.3,0.2,0.1]

    # for i in range(0, resolution_height / 2):  # upper
    #     for j in range(0, resolution_width / 2):
    #         radiance_map[i, j, :] = [0.1, 0.15, 0.18,0.3,0.8]



    for i in range(resolution_height / 2, resolution_height):  # down
        for j in range(0, resolution_width):
            radiance_map[i, j, :] = [0.2, 0.1, 0.05, 0.04,0.03]

    # for i in range(70, 90):  # upper
    #     for j in range(0, 10):
    #         radiance_map[i, resolution_width - j - 1, :] = [0.5, 0.15, 0.18, 0.3, 0.8]

            # write this into exr file
    band_dict = dict()
    half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
    chaneldict = dict()
    for i in range(0, band_num):
        start = wavelengths[i]
        end = wavelengths[i + 1]
        band_name = "%.2f" % start + "-" + "%.2fnm" % end
        singleband = radiance_map[:, :, i]
        singleband = np.reshape(singleband, (resolution_width * resolution_height))
        radiance_str = array.array('f', singleband).tostring()  # generate arr
        band_dict[band_name] = radiance_str
        chaneldict[band_name] = half_chan
    header = OpenEXR.Header(resolution_width, resolution_height)
    header["channels"] = chaneldict
    if not isinstance(output_file, str):
        # writing to a temperal place, since OpenEXR do not support unicode
        tmpExrPath = os.path.join(os.path.expanduser('~'), "_tmp_sky.exr")
        out = OpenEXR.OutputFile(tmpExrPath, header)
        out.writePixels(band_dict)
        out = None
        # copy back
        shutil.move(tmpExrPath, output_file)
    else:
        out = OpenEXR.OutputFile(output_file, header)
        out.writePixels(band_dict)
        out = None



def create_envmap_fun(input, output):
    band_start = const.get_value("NO_BAND_WIDTH_MODE_BAND_START")
    band_end = const.get_value("NO_BAND_WIDTH_MODE_BAND_END")
    band_num = const.get_value("NO_BAND_WIDTH_MODE_BAND_NUM")
    resolution_width = const.get_value("env_map_resolution")
    resolution_height = int(resolution_width / 2)

    # golden = OpenEXR.InputFile(out_file)
    # b1 = golden.channel("400.0-404.0nm")
    # print OpenEXR.InputFile(out_file).header()
    #
    # sys.exit(0)

    # read data
    f = open(input, 'r')
    theta_phi = []
    band_data = []
    for line in f:
        arr = line.split(" ")
        theta = float(line[0])
        phi = float(line[1])
        theta_phi.append([theta, phi])
        if len(arr[2:]) != band_num:
            log("band number does not equal.")
            sys.exit(0)
        band_data.append(list(map(lambda x: float(x), arr[2:])))
    # band_data = map(list, zip(*band_data))  # [[band1_p1,band1_p2,...],[band2_p1,band2_p2,...]]
    wavelengths = np.linspace(band_start, band_end, band_num + 1)

    radiance_map = np.zeros((resolution_height, resolution_width, band_num))
    factor_y = 180 / resolution_height  # lat for each pixel
    factor_x = 2 * 180 / resolution_width  # lon for each pixel
    for i in range(0, resolution_height / 2):
        c_theta = i * factor_y
        for j in range(0, resolution_width):
            c_phi = (j + 0.5) * factor_x
            nearest_pos = get_nearest_theta_phi(c_theta, c_phi, theta_phi)
            radiance_map[i, j, :] = band_data[nearest_pos]

    # write this into exr file
    band_dict = dict()
    half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
    chaneldict = dict()
    for i in range(0, band_num):
        start = wavelengths[i]
        end = wavelengths[i + 1]
        band_name = "%.2f" % start + "-" + "%.2fnm" % end
        singleband = radiance_map[:, :, i]
        singleband = np.reshape(singleband, (resolution_width * resolution_height))
        radiance_str = array.array('f', singleband).tostring()  # generate arr
        band_dict[band_name] = radiance_str
        chaneldict[band_name] = half_chan
    header = OpenEXR.Header(resolution_width, resolution_height)
    header["channels"] = chaneldict
    out = OpenEXR.OutputFile(output, header)
    out.writePixels(band_dict)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-i", help="Directional radiance file.", required=True)
    # parser.add_argument("-o", help="Generated environment map (*.exr).", required=True)
    # args = parser.parse_args()
    #
    # input_file = args.i  # theta phi band1_radiance band2_radiance,...
    # out_file = args.o
    #
    # create_envmap_fun(input_file, out_file)
    create_class_map_reflectance(r"E:\Coding\Mitsuba\simulations\texture\Parameters\_scenefile\terrref.exr")


