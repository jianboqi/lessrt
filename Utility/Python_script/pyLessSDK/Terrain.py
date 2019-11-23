# coding: utf-8
from Element import Element


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
        self.optical = "dark_soil_mollisol"

    def init_terrain_from_json(self, json_object):
        self.terr_BRDF_Type = json_object["scene"]["terrain"]["terrBRDFType"]
        self.optical_scale = json_object["scene"]["terrain"]["optical_scale"]
        self.extent_height = json_object["scene"]["terrain"]["extent_height"]
        self.extent_width = json_object["scene"]["terrain"]["extent_width"]
        self.terr_file = json_object["scene"]["terrain"]["terr_file"]
        self.terrain_type = json_object["scene"]["terrain"]["terrain_type"]
        self.optical = json_object["scene"]["terrain"]["optical"]
        return self

    def to_json_object(self):
        if not self.get_sim().get_scene().get_sensor().thermal_radiation:
            json_obj = {"terrBRDFType": self.terr_BRDF_Type,
                        "optical_scale": self.optical_scale,
                        "extent_height": self.extent_height,
                        "terr_file": self.terr_file,
                        "terrain_type": self.terrain_type,
                        "optical": self.optical,
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
