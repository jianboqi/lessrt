# coding: utf-8
from Element import Element
import sys
import os
import shutil


class BRDF_TYPE:
    LAMBERTIAN = "Lambertian"
    LAND_ALBEDO_MAP = "Land Albedo Map"
    SOILSPECT = "Soilspect"


class Terrain(Element):
    def __init__(self):
        super().__init__()
        # terrain
        self.terr_BRDF_Type = "Lambertian"
        self.optical_scale = 1
        self.extent_height = 100
        self.extent_width = 100
        self.terr_file = ""
        self.terrain_type = "PLANE"

        # conditional properties
        self.optical = "dark_soil_mollisol"
        self.landalbedo = ""
        self.soilSpectParams = dict()

    def set_terr_brdf_type(self, brdf_type):
        self.terr_BRDF_Type = brdf_type

    def get_optical(self):
        if self.terr_BRDF_Type != BRDF_TYPE.LAMBERTIAN:
            print("Terrain Type: ", self.terr_BRDF_Type, "does not have property \"optical\"")
            sys.exit()
        return self.optical

    def set_optical(self, optical_name):
        if self.terr_BRDF_Type != BRDF_TYPE.LAMBERTIAN:
            print("Terrain Type: ", self.terr_BRDF_Type, "does not have property \"optical\"")
            sys.exit()
        self.optical = optical_name

    def get_landalbedo_file(self):
        if self.terr_BRDF_Type != BRDF_TYPE.LAND_ALBEDO_MAP:
            print("Terrain Type: ", self.terr_BRDF_Type, "does not have property \"Land Albedo Map\"")
            sys.exit()
        return self.landalbedo

    def set_landalbedo_file(self, landalbedo_file):  # 需要复制文件
        if self.terr_BRDF_Type != BRDF_TYPE.LAND_ALBEDO_MAP:
            print("Terrain Type: ", self.terr_BRDF_Type, "does not have property \"Land Albedo Map\"")
            sys.exit()
        filename = os.path.basename(landalbedo_file)
        dist_albedomap = os.path.join(self.get_sim().get_sim_dir(), "Parameters", filename)
        if dist_albedomap != landalbedo_file:
            shutil.copy(landalbedo_file, dist_albedomap)
        landalbedo_file_header = landalbedo_file + ".hdr"
        dist_albedomap_header = dist_albedomap+".hdr"
        if os.path.exists(landalbedo_file_header) and landalbedo_file_header != dist_albedomap_header:
            shutil.copy(landalbedo_file_header, dist_albedomap+".hdr")
        self.landalbedo = filename

    def init_terrain_from_json(self, json_object):
        self.terr_BRDF_Type = json_object["scene"]["terrain"]["terrBRDFType"]
        self.optical_scale = json_object["scene"]["terrain"]["optical_scale"]
        self.extent_height = json_object["scene"]["terrain"]["extent_height"]
        self.extent_width = json_object["scene"]["terrain"]["extent_width"]
        self.terr_file = json_object["scene"]["terrain"]["terr_file"]
        self.terrain_type = json_object["scene"]["terrain"]["terrain_type"]

        if self.terr_BRDF_Type == "Lambertian":
            if "optical" in json_object["scene"]["terrain"]:
                self.optical = json_object["scene"]["terrain"]["optical"]
        elif self.terr_BRDF_Type == "Land Albedo Map":
            if "landalbedo" in json_object["scene"]["terrain"]:
                self.landalbedo = json_object["scene"]["terrain"]["landalbedo"]
        elif self.terr_BRDF_Type == "Soilspect":
            if "soilSpectParams" in json_object["scene"]["terrain"]:
                if "c3" in json_object["scene"]["terrain"]["soilSpectParams"]:
                    self.soilSpectParams["c3"] = json_object["scene"]["terrain"]["soilSpectParams"]["c3"]
                if "c4" in json_object["scene"]["terrain"]["soilSpectParams"]:
                    self.soilSpectParams["c4"] = json_object["scene"]["terrain"]["soilSpectParams"]["c4"]
                if "h1" in json_object["scene"]["terrain"]["soilSpectParams"]:
                    self.soilSpectParams["h1"] = json_object["scene"]["terrain"]["soilSpectParams"]["h1"]
                if "h2" in json_object["scene"]["terrain"]["soilSpectParams"]:
                    self.soilSpectParams["h2"] = json_object["scene"]["terrain"]["soilSpectParams"]["h2"]
                if "c1" in json_object["scene"]["terrain"]["soilSpectParams"]:
                    self.soilSpectParams["c1"] = json_object["scene"]["terrain"]["soilSpectParams"]["c1"]
                if "albedo" in json_object["scene"]["terrain"]["soilSpectParams"]:
                    self.soilSpectParams["albedo"] = json_object["scene"]["terrain"]["soilSpectParams"]["albedo"]
                if "c2" in json_object["scene"]["terrain"]["soilSpectParams"]:
                    self.soilSpectParams["c2"] = json_object["scene"]["terrain"]["soilSpectParams"]["c2"]
        return self

    def to_json_object(self):
        json_obj = ""
        if not self.get_sim().get_scene().get_sensor().thermal_radiation:
            if self.terr_BRDF_Type == "Lambertian":
                json_obj = {"terrBRDFType": self.terr_BRDF_Type,
                            "optical_scale": self.optical_scale,
                            "extent_height": self.extent_height,
                            "terr_file": self.terr_file,
                            "terrain_type": self.terrain_type,
                            "optical": self.optical,
                            "extent_width": self.extent_width}
            elif self.terr_BRDF_Type == "Land Albedo Map":
                json_obj = {"terrBRDFType": self.terr_BRDF_Type,
                            "optical_scale": self.optical_scale,
                            "extent_height": self.extent_height,
                            "terr_file": self.terr_file,
                            "terrain_type": self.terrain_type,
                            "landalbedo": self.landalbedo,
                            "extent_width": self.extent_width}
            elif self.terr_BRDF_Type == "Soilspect":
                json_obj = {"terrBRDFType": self.terr_BRDF_Type,
                            "optical_scale": self.optical_scale,
                            "extent_height": self.extent_height,
                            "terr_file": self.terr_file,
                            "terrain_type": self.terrain_type,
                            "soilSpectParams": self.soilSpectParams,
                            "extent_width": self.extent_width}

        else:
            json_obj = {"terrBRDFType": self.terr_BRDF_Type,
                        "optical_scale": self.optical_scale,
                        "extent_height": self.extent_height,
                        "terr_file": self.terr_file,
                        "temperature": self.temperature,
                        "terrain_type": self.terrain_type,
                        "optical": self.optical,
                        "extent_width": self.extent_width}
        return json_obj
