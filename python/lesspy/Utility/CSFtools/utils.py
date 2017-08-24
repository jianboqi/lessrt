"""
Some common function, such as file reading and writing
Author: Jianbo Qi
Date: 2017-1-15
"""
from osgeo import gdal

# writing arr to ENVI standard file format
def saveToHdr(npArray, dstFilePath, geoTransform=""):
    dshape = npArray.shape
    bandnum = 1
    format = "ENVI"
    driver = gdal.GetDriverByName(format)
    dst_ds = driver.Create(dstFilePath, dshape[1], dshape[0], bandnum, gdal.GDT_Float32)
    if not geoTransform == "":
        dst_ds.SetGeoTransform(geoTransform)
    #     npArray = linear_stretch_3d(npArray)
    dst_ds.GetRasterBand(1).WriteArray(npArray)
    dst_ds = None


# reading image to area
def read_file_to_arr(img_file):
    dataset = gdal.Open(img_file)
    band = dataset.GetRasterBand(1)
    geoTransform = dataset.GetGeoTransform()
    dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
    return band.XSize, band.YSize,geoTransform[1], dataarr


# only reading the data array
def read_img_to_arr_no_transform(img_file):
    data_set = gdal.Open(img_file)
    band = data_set.GetRasterBand(1)
    arr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
    return arr