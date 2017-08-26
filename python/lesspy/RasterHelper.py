#coding:utf-8

from osgeo import gdal
import numpy as np
import OpenEXR
import array, Imath
import shutil
import os
from Loger import log

class RasterHelper:
    @staticmethod
    def read_dem_as_array(dem_path):
        dataset = gdal.Open(dem_path)
        band = dataset.GetRasterBand(1)
        return band.XSize, band.YSize, band.ReadAsArray(0, 0, band.XSize, band.YSize)

    @staticmethod
    def read_as_array(dem_path, band):
        dataset = gdal.Open(dem_path)
        band = dataset.GetRasterBand(band)
        return band.XSize, band.YSize, band.ReadAsArray(0, 0, band.XSize, band.YSize)

    @staticmethod
    def getMaxHeightDiff(dem_path):
        dataset = gdal.Open(dem_path)
        band = dataset.GetRasterBand(1)
        dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
        return dataarr.max()-dataarr.min()

    @staticmethod
    def convert_dem_to_mip_monochromatic_chanel(dem_path, mip_path):
        dataset = gdal.Open(dem_path)
        band = dataset.GetRasterBand(1)
        # save to openexr file
        XSize = band.XSize
        YSize = band.YSize
        dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
        dataarr = np.fliplr(dataarr)
        dataarr = np.reshape(dataarr, (XSize * YSize))
        dataarr = dataarr - dataarr.min()
        heightStr = array.array('f', dataarr).tostring()

        data_dict = dict()
        half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
        chaneldict = dict()
        data_dict["y"] = heightStr
        chaneldict["y"] = half_chan
        header = OpenEXR.Header(band.XSize, band.YSize)
        header["channels"] = chaneldict
        out = OpenEXR.OutputFile(mip_path, header)
        out.writePixels(data_dict)
    #
    # 该方法已经被弃用， 因为"G"写的exr是rgb格式，在导入less中之后会自动拉伸，比例因子大约在1.4
    # 但是不准确，应该输入luminance格式的但波段文件。即上面的方法
    # @staticmethod
    # def convert_dem_to_mip(dem_path,mip_path):
    #     dataset = gdal.Open(dem_path)
    #     band = dataset.GetRasterBand(1)
    #     # save to openexr file
    #     XSize = band.XSize
    #     YSize = band.YSize
    #     dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)
    #     dataarr = np.fliplr(dataarr)
    #     dataarr = np.reshape(dataarr, (XSize * YSize))
    #     dataarr = dataarr - dataarr.min()
    #     heightStr = array.array('f', dataarr).tostring()
    #     # handling unicode path
    #     if not isinstance(mip_path,str):
    #         # writing to a temperal place, since OpenEXR do not support unicode
    #         tmpExrPath = os.path.join(os.path.expanduser('~'),"_tmp.exr")
    #         out = OpenEXR.OutputFile(tmpExrPath, OpenEXR.Header(XSize, YSize))
    #         out.writePixels({"G": heightStr})
    #         out = None
    #         # copy back
    #         shutil.move(tmpExrPath, mip_path)
    #     else:
    #         out = OpenEXR.OutputFile(mip_path, OpenEXR.Header(XSize, YSize))
    #         out.writePixels({"G": heightStr})
    #         out = None

    @staticmethod
    def saveToHdr_no_transform(npArray, dstFilePath, wlist, output_format):
        dshape = npArray.shape
        if len(dshape) == 3:
            bandnum = dshape[2]
        else:
            bandnum = 1
        # 从hdrHeaderPath中提取投影信息
        if output_format == "ENVI":
            format = "ENVI"
        else:
            format = "GTiff"
            dstFilePath += ".tif"
        driver = gdal.GetDriverByName(format)
        dst_ds = driver.Create(dstFilePath, dshape[1], dshape[0], bandnum, gdal.GDT_Float32)
        #     npArray = linear_stretch_3d(npArray)
        if bandnum > 1:
            for i in range(1, bandnum + 1):
                dst_ds.GetRasterBand(i).WriteArray(npArray[:, :, i - 1])
        else:
            dst_ds.GetRasterBand(1).WriteArray(npArray)
        dst_ds = None

        if output_format == "ENVI" and len(wlist) >0:
            # wirte wavelength
            f = open(dstFilePath+".hdr",'r')
            text = f.read()
            f.close()
            wstr = "\nwavelength = {"
            for i in range(0,len(wlist)):
                wstr += wlist[i].split(":")[0] + ","
            wstr = wstr[0:len(wstr)-1] + "}"
            f = open(dstFilePath+".hdr",'w')
            text = text + wstr
            f.write(text)
            f.close()


    @staticmethod
    def readAsArr(filepath):
        data_set = gdal.Open(filepath)
        band = data_set.GetRasterBand(1)
        arr = band.ReadAsArray(0,0,band.XSize, band.YSize)
        return arr



    @staticmethod
    def saveToHdr(npArray, hdrHeaderPath, dstFilePath, width, height, spatialResolution):
        # 从hdrHeaderPath中提取投影信息
        dataset = gdal.Open(hdrHeaderPath)
        geotransform = dataset.GetGeoTransform()
        projection = dataset.GetProjection()
        geoTrans = [geotransform[0], spatialResolution, geotransform[2], geotransform[3], geotransform[4],
                    -spatialResolution]
        if dataset is None:
            log("Header File not found!")
            return
        format = "ENVI"
        driver = gdal.GetDriverByName(format)
        dst_ds = driver.Create(dstFilePath, width, height, 65, gdal.GDT_Float32)
        dst_ds.SetGeoTransform(geoTrans)
        dst_ds.SetProjection(projection)
        #     npArray = linear_stretch_3d(npArray)
        for i in range(1, 65 + 1):
            dst_ds.GetRasterBand(i).WriteArray(npArray[:, :, i - 1])
        dst_ds = None

    #写obj文件时注意，格式根据mitsuba的来
    @staticmethod
    def Raster2Ojb(rasterfile, dist_obj_file, offset_to_lowerest_pos=True):

        if os.path.exists(dist_obj_file):
            return

        dataset = gdal.Open(rasterfile)
        band = dataset.GetRasterBand(1)
        transform = dataset.GetGeoTransform()
        if not transform is None:
            pixel_x = abs(transform[1])
            pixel_y = abs(transform[5])
        else:
            log("no geo transform.")
        XSize = band.XSize
        YSize = band.YSize
        xExtend = XSize*pixel_x
        yExtend = YSize*pixel_y
        # save to openexr file

        dataarr = band.ReadAsArray(0, 0, band.XSize, band.YSize)

        if offset_to_lowerest_pos:
            dataarr = dataarr - dataarr.min()
        f = open(dist_obj_file,'w')
        for i in range(0, YSize+1):
            for j in range(0,  XSize+1):
                x = " %.4f " % (0.5 * xExtend - j * pixel_x)
                z = " %.4f " % (0.5 * yExtend - i * pixel_y)
                if i < YSize and j < XSize:
                    datavalue = " %.4f"% (dataarr[i][j])
                else:
                    datavalue = " %.4f"% (dataarr[i-1][j-1])

                fstr = "v " + x + datavalue + z + "\n"
                f.write(fstr)

        for i in range(0, YSize):
            for j in range(0, XSize):
                p1 = i*(XSize+1) + j+1
                p2 = (i+1)*(XSize+1) + j+1
                p3 = (i+1)*(XSize+1) +j+1+1
                p4 = i*(XSize+1) + j+ 1+1
                fstr = "f " + str(p1) + " " + str(p2) + " " + str(p3) + " " + str(p4)+"\n"
                f.write(fstr)
        f.close()




