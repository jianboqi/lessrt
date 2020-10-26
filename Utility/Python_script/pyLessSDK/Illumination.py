# coding: utf-8
from Element import Element


class Illumination(Element):
    def __init__(self):
        super().__init__()
        self.atmosphere_percentage = "0.0,0.0"
        self.ats_type = "SKY_TO_TOTAL"

        self.sun_azimuth = 90
        self.sun_zenith = 45

        self.sun_calculator = False

    def set_ats_percentage(self, ats_percentage):
        self.atmosphere_percentage = ats_percentage

    def init_illumination_from_json(self, json_object):
        self.atmosphere_percentage = json_object["illumination"]["atmosphere"]["percentage"]
        self.ats_type = json_object["illumination"]["atmosphere"]["ats_type"]
        self.sun_azimuth = json_object["illumination"]["sun"]["sun_azimuth"]
        self.sun_zenith = json_object["illumination"]["sun"]["sun_zenith"]
        self.sun_calculator = json_object["illumination"]["sun_calculator"]
        return self

    def to_json_object(self):
        if not self.get_sim().get_scene().get_sensor().thermal_radiation:
            json_object = {"atmosphere": {"percentage": self.atmosphere_percentage,
                                          "ats_type": self.ats_type},
                           "sun": {"sun_azimuth": self.sun_azimuth,
                                   "sun_zenith": self.sun_zenith},
                           "sun_calculator": self.sun_calculator}
        else:
            json_object = {"atmosphere": {"percentage": self.atmosphere_percentage,
                                          "ats_type": self.ats_type,
                                          "AtsTemperature": self.ats_temperature},
                           "sun": {"sun_azimuth": self.sun_azimuth,
                                   "sun_zenith": self.sun_zenith},
                           "sun_calculator": self.sun_calculator}
        return json_object
