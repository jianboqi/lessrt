#coding:utf-8
import sqlite3

from Constant import *
from FileHelper import *

# class LambertianDB:
#
#     # 将两个数组联合成一个字符串 但是只取lambda_from, lambda_to
#     @staticmethod
#     def combine_w_s_from_to(w, s,lambda_from, lambda_to,factor):
#         length = len(w)
#         combined_str = ""
#         for i in range(0, length):
#             if float(w[i]) >= lambda_from and float(w[i])<=lambda_to:
#                 combined_str += w[i] + ":" + "%.4f"%(float(s[i])*factor)
#                 if i < length - 1:
#                     combined_str += ","
#         return combined_str[:-1]
#
#     # 将两个数组联合成一个字符串
#     @staticmethod
#     def combine_w_s(w,s,factor):
#         length = len(w)
#         combined_str = ""
#         for i in range(0,length):
#             combined_str += str(w[i]) + ":" + "%.4f"%(float(s[i])*factor)
#             if i<length-1:
#                 combined_str += ","
#         return combined_str
#
#
#     # 根据名称读取对于的光谱
#     # 返回为一个二位数组
#     @staticmethod
#     def read_spectral_to_string(obj_name,factor=1):
#         currdir = os.path.split(os.path.realpath(__file__))[0]
#         cx = sqlite3.connect(combine_file_path(currdir, lambertiandb_path))
#         cu = cx.cursor()
#         cu.execute("select Wavelength,Front_ref,Back_ref,Transmittance\
#                   from Lambertian where Name=\"" + obj_name + "\"")
#         re = cu.fetchall()
#         result_str={}
#         wavelengths_arr = re[0][0].split(",")
#         if re[0][1] is not None:
#             front_ref = re[0][1].split(",")
#             result_str[Front_ref] = LambertianDB.combine_w_s(wavelengths_arr, front_ref,factor)
#         if re[0][2] is not None:
#             back_ref_arr = re[0][2].split(",")
#             result_str[Back_ref] = LambertianDB.combine_w_s(wavelengths_arr, back_ref_arr,factor)
#         if re[0][3] is not None:
#             transmittance_arr = re[0][3].split(",")
#             result_str[Transmittance] = LambertianDB.combine_w_s(wavelengths_arr, transmittance_arr,factor)
#         cu.close()
#         cx.close()
#         return result_str
#
#         # 根据名称读取对于的光谱
#         # 返回为一个二位数组
#     @staticmethod
#     def read_spectral_to_string_from_to(obj_name,lambda_from, lambda_to,factor=1):
#         currdir = os.path.split(os.path.realpath(__file__))[0]
#         cx = sqlite3.connect(combine_file_path(currdir, lambertiandb_path))
#         cu = cx.cursor()
#         cu.execute(
#             "select Wavelength,Front_ref,Back_ref,Transmittance from Lambertian where Name=\"" + obj_name + "\"")
#         re = cu.fetchall()
#         result_str = {}
#         wavelengths = re[0][0].split(",")
#         if re[0][1] is not None:
#             front_ref_arr = re[0][1].split(",")
#             result_str[Front_ref] = LambertianDB.combine_w_s_from_to(wavelengths, front_ref_arr,lambda_from,lambda_to,factor)
#         if re[0][2] is not None:
#             back_ref_arr = re[0][2].split(",")
#             result_str[Back_ref] = LambertianDB.combine_w_s_from_to(wavelengths, back_ref_arr,lambda_from,lambda_to,factor)
#         if re[0][3] is not None:
#             transmittance_arr = re[0][3].split(",")
#             result_str[Transmittance] = LambertianDB.combine_w_s_from_to(wavelengths, \
#                     transmittance_arr, lambda_from, lambda_to,factor)
#         cu.close()
#         cx.close()
#         return result_str
#
#     @staticmethod
#     def getRef_at_point(wavelength, w_arr, refs):
#         len_sun_spectral = len(w_arr)
#         nearest_pos = min(range(len_sun_spectral), \
#                           key=lambda i: abs(w_arr[i] - wavelength))
#         # scale the irradiance, since the irradiance at a point per nm is to small
#         return refs[nearest_pos]
#
#     #extending bands to maximum length
#     @staticmethod
#     def extend_ref(bandlist):
#         bandstr = ""
#         for i in range(0, NO_BAND_WIDTH_MODE_BAND_NUM):
#             if i < len(bandlist):
#                 bandstr += bandlist[i] + ","
#             else:
#                 bandstr += "0,"
#         return bandstr[0:len(bandstr) - 1]
#
#     @staticmethod
#     def extend_ref_trans(bandstr):
#         op = dict()
#         arr_r_t = bandstr.split(";")
#         arr = arr_r_t[0].split(",")
#         op[Front_ref] = LambertianDB.extend_ref(arr)
#         arr = arr_r_t[1].split(",")
#         op[Back_ref] = LambertianDB.extend_ref(arr)
#         arr = arr_r_t[2].split(",")
#         op[Transmittance] = LambertianDB.extend_ref(arr)
#         return op
#
#
#     @staticmethod
#     def combine_ref(bandlist,w_arr,refs,factor):
#         bandstr = ""
#         for i in range(0, NO_BAND_WIDTH_MODE_BAND_NUM):
#             if i < len(bandlist):
#                 bandstr += "%.5f"% (factor*LambertianDB.getRef_at_point(bandlist[i],w_arr,refs))+","
#             else:
#                 bandstr += "0,"
#         return bandstr[0:len(bandstr)-1]
#     @staticmethod
#     def read_Specific_band(bandlist,obj_name,factor=1):
#         currdir = os.path.split(os.path.realpath(__file__))[0]
#         cx = sqlite3.connect(combine_file_path(currdir, lambertiandb_path))
#         cu = cx.cursor()
#         cu.execute("select Wavelength,Front_ref,Back_ref,Transmittance\
#                           from Lambertian where Name=\"" + obj_name + "\"")
#         re = cu.fetchall()
#         result_str = {}
#         wavelengths_arr = map(lambda x:float(x), re[0][0].split(","))
#
#         if re[0][1] is not None:
#             front_ref = map(lambda x:float(x),re[0][1].split(","))
#             result_str[Front_ref] = LambertianDB.combine_ref(bandlist, wavelengths_arr, front_ref, factor)
#         if re[0][2] is not None:
#             back_ref_arr = map(lambda x:float(x),re[0][2].split(","))
#             result_str[Back_ref] = LambertianDB.combine_ref(bandlist, wavelengths_arr, back_ref_arr, factor)
#         if re[0][3] is not None:
#             transmittance_arr = map(lambda x:float(x),re[0][3].split(","))
#             result_str[Transmittance] = LambertianDB.combine_ref(bandlist, wavelengths_arr, transmittance_arr, factor)
#         cu.close()
#         cx.close()
#         return result_str


class sun_irradiance_db:

    ## with bandwidth
    @staticmethod
    def read_toa_with_bandwidth(wave_list_with_bandwidth):
        currdir = os.path.split(os.path.realpath(__file__))[0]
        cx = sqlite3.connect(combine_file_path(currdir, sun_toa_db))
        cu = cx.cursor()
        wlArr = wave_list_with_bandwidth.split(",")
        irr_list = []
        for wl in wlArr:
            wbarr = wl.split(":")
            w,b = float(wbarr[0]),float(wbarr[1])
            if b < 0.0001:
                b=1
            left = w - 0.5 * b
            right = w + 0.5 * b
            cu.execute("select wavelength, irradiance from TOASolar_2005_per_nm where "
                       "wavelength>=%.13f and wavelength<=%.13f"%(left, right))
            re = cu.fetchall()
            length = len(re)
            totalIrr = 0
            for i in range(0, length-2):
                upper = re[i][1]
                down = re[i+1][1]
                height = re[i+1][0]-re[i][0]
                area = (upper+down)*height*0.5
                totalIrr += area
            totalIrr += (re[0][0]-left)*re[0][1]
            totalIrr += (right - re[length-1][0])*re[length-1][1]
            irr_per_nm = totalIrr/float(b)
            irr_list.append(irr_per_nm)
        return irr_list

    @staticmethod
    def read_toa_with_bandwidth_SKYLs(wave_list_with_bandwidth, skyls):
        irr_list = sun_irradiance_db.read_toa_with_bandwidth(wave_list_with_bandwidth)
        sky_irr_list = map(lambda x, y: x*y, irr_list, skyls)
        sun_irr_list = map(lambda x, y: x*(1-y),irr_list, skyls)
        return sun_irr_list,sky_irr_list


    # @staticmethod
    # def combine_w_s_by_factor(w, s, factor):
    #     length = len(w)
    #     combined_str = ""
    #     for i in range(0, length):
    #         combined_str += str(w[i]) + ":" + "%.4f"%(float(s[i])*factor)
    #         if i < length - 1:
    #             combined_str += ","
    #     return combined_str
    #
    # @staticmethod
    # def read_sun_tos_to_list():
    #     currdir = os.path.split(os.path.realpath(__file__))[0]
    #     cx = sqlite3.connect(combine_file_path(currdir, sun_toa_db))
    #     cu = cx.cursor()
    #     cu.execute("select Wavelength, Irradiance from sunTOA where Name=\"sunTOA_400_1500\"")
    #     re = cu.fetchall()
    #     w_arr = map(lambda x:float(x),re[0][0].split(","))
    #     s_irr = map(lambda x:float(x),re[0][1].split(","))
    #     return w_arr,s_irr
    #
    #
    # @staticmethod
    # def read_sun_toa_to_string(factor):
    #     currdir = os.path.split(os.path.realpath(__file__))[0]
    #     cx = sqlite3.connect(combine_file_path(currdir, sun_toa_db))
    #     cu = cx.cursor()
    #     cu.execute("select Wavelength, Irradiance from sunTOA where Name=\"sunTOA_400_1500\"")
    #     re = cu.fetchall()
    #     w_arr = re[0][0].split(",")
    #     s_irr = re[0][1].split(",")
    #     irr_str = sun_irradiance_db.combine_w_s_by_factor(w_arr, s_irr, factor)
    #     return irr_str
    #
    # @staticmethod
    # def getIrr_at_point(wavelength,w_arr,i_arr):
    #     len_sun_spectral = len(w_arr)
    #     nearest_pos = min(range(len_sun_spectral), \
    #                       key=lambda i: abs(w_arr[i] - wavelength))
    #     #scale the irradiance, since the irradiance at a point per nm is to small
    #     return i_arr[nearest_pos]*NO_BAND_WIDTH_MODE_BIN_WIDTH
    #
    # @staticmethod
    # def read_Specific_band_factorarr(factor_arr, bandlist):
    #     w_arr,i_arr = sun_irradiance_db.read_sun_tos_to_list()
    #     bandstr = ""
    #     for i in range(0, NO_BAND_WIDTH_MODE_BAND_NUM):
    #         if i < len(bandlist):
    #             bandstr +=  "%.5f, "%(factor_arr[i]*sun_irradiance_db.getIrr_at_point(bandlist[i],w_arr,i_arr))
    #         else:
    #             bandstr += "0,"
    #     return bandstr[0:len(bandstr)-1]
    #
    # @staticmethod
    # def read_Specific_band(factor, bandlist):
    #     w_arr,i_arr = sun_irradiance_db.read_sun_tos_to_list()
    #     bandstr = ""
    #     for i in range(0,NO_BAND_WIDTH_MODE_BAND_NUM):
    #         if i < len(bandlist):
    #             bandstr +=  "%.5f, "%(factor*sun_irradiance_db.getIrr_at_point(bandlist[i],w_arr,i_arr))
    #         else:
    #             bandstr += "0,"
    #     return bandstr[0:len(bandstr)-1]

if __name__=="__main__":
    #print LambertianDB.read_spectral_to_string_from_to("birch_leaf_yellow",400,410)
    #print sun_irradiance_db.read_sun_toa_to_string()
    # obj_name = "birch_leaf_yellow"
    # cx = sqlite3.connect(lambertiandb_path)
    # cu = cx.cursor()
    # cu.execute("select Wavelength,Front_ref,Back_ref,Transmittance\
    #                   from Lambertian where Name=\"" + obj_name + "\"")
    # re = cu.fetchall()
    # log(obj_name)
    print sun_irradiance_db.read_toa_with_bandwidth_SKYLs("600:10,700:10",[0.2,0.1])
