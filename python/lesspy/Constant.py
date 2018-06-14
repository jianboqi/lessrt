#coding:utf-8

import os,sys
import json
from Loger import log
class Const:
    def __init__(self):
        currdir = os.path.split(os.path.realpath(__file__))[0]
        const_file = currdir + os.sep+"const.conf"
        if not os.path.exists(const_file):
            log("const config file does not exist.")
            sys.exitfunc()
        else:
            f = open(const_file, "r")
            self.const = json.load(f)
            f.close()

    def get_value(self, key):
        if key in self.const.keys():
            return self.const[key]

const = Const()

#数据库相关
lambertiandb_path = const.get_value("lambertiandb_path")
sun_toa_db = const.get_value("sun_toa_db")
Wavelength = const.get_value("Wavelength")
Front_ref = const.get_value("Front_ref")
Back_ref = const.get_value("Back_ref")
Transmittance = const.get_value("Transmittance")

# 文件
#cfg_file_path = "./input.conf"
input_dir = const.get_value("input_dir")
output_dir = const.get_value("output_dir")
config_file = const.get_value("config_file")
tmp_scene_file_dir = const.get_value("tmp_scene_file_dir")
main_scene_xml_file = const.get_value("main_scene_xml_file")
terr_scene_file = const.get_value("terr_scene_file")
forest_scene_file = const.get_value("forest_scene_file")
atmosphere_scene_file = const.get_value("atmosphere_scene_file")
object_scene_file = const.get_value("object_scene_file")
NUM_EACH_FOREST_FILE = const.get_value("NUM_EACH_FOREST_FILE")
session_file = const.get_value("session_file")
template_input = const.get_value("template_input")
rgb_img_prefix = const.get_value("rgb_img_prefix")
spectral_img_prefix = const.get_value("spectral_img_prefix")
photon_tracing_img_prefix = const.get_value("photon_tracing_img_prefix")
seq_file_prefix = const.get_value("seq_file_prefix")
multi_file_prefix = const.get_value("multiangle_file_prefix")
irradiance_file = const.get_value("IRRADIANCE_FILE")
less_identifier = const.get_value("less_identifier")
batch_conf = const.get_value("Batch_conf")
BATCH_INFO_FILE = const.get_value("batch_info_file")
spectral_info_file = const.get_value("spectral_info_file")

#advanced no use for user
current_rt_program = const.get_value("current_rt_program")
# NO_BAND_WIDTH_MODE_BAND_NUM=const.get_value("NO_BAND_WIDTH_MODE_BAND_NUM")
# NO_BAND_WIDTH_MODE_BIN_WIDTH = const.get_value("NO_BAND_WIDTH_MODE_BIN_WIDTH")
LESS_BAND_START = str(const.get_value("NO_BAND_WIDTH_MODE_BAND_START"))
LESS_BAND_END = str(const.get_value("NO_BAND_WIDTH_MODE_BAND_END"))

output_format = const.get_value("output_format")

batch_folder = const.get_value("Batch_folder")
batch_List_name = const.get_value("Batch_LIST_NAME")
imported_landcover_raster_name = const.get_value("imported_landcover_raster_name")

obj_bounding_box_file = const.get_value("obj_bounding_box_file")

hide_objects_file = const.get_value("hide_objects_file")