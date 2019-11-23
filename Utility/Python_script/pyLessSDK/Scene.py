# coding: utf-8
import json
from Landscape import Landscape
from Sensor import SensorOrthographic
from Illumination import Illumination
from Observation import ObservationOrthographic
from AdvancedParams import AdvancedParams


class Scene(object):
    def __init__(self):
        self.__sensor = SensorOrthographic()
        self.__landscape = Landscape()
        self.__illumination = Illumination()
        self.__observation = ObservationOrthographic()
        self.__advanced_params = AdvancedParams()

    def set_sensor(self, sensor):
        self.__sensor = sensor

    def get_sensor(self):
        return self.__sensor

    def set_landscape(self, landscape):
        self.__landscape = landscape

    def get_landscape(self):
        return self.__landscape

    def set_illumination(self, illumination):
        self.__illumination = illumination

    def get_illumination(self):
        return self.__illumination

    def set_observation(self, observation):
        self.__observation = observation

    def get_observation(self):
        return self.__observation

    def set_advanced_params(self, advanced_params):
        self.__advanced_params = advanced_params

    def get_advanced_params(self):
        return self.__advanced_params

    def to_json_object(self, sim):
        json_object = {"Advanced": self.__advanced_params.to_json_object(),
                       "illumination": self.__illumination.to_json_object(),
                       "observation": self.__observation.to_json_object(),
                       "sensor": self.__sensor.to_json_object(),
                       "scene": self.__landscape.to_json_object(sim)}
        return json_object

    def write_scene(self, json_file_path):
        f_out = open(json_file_path, "w")
        json.dump(self.to_json_object(), f_out, indent=2)
        f_out.close()
