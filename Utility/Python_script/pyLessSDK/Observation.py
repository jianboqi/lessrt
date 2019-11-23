# coding: utf-8
from Element import Element


class ObservationOrthographic(Element):
    def __init__(self):
        super().__init__()
        self.obs_azimuth = 180
        self.obs_zenith = 0
        self.obs_R = 3000

    def init_obs_from_json(self, json_object):
        self.obs_azimuth = json_object["observation"]["obs_azimuth"]
        self.obs_zenith = json_object["observation"]["obs_zenith"]
        self.obs_R = json_object["observation"]["obs_R"]
        return self

    def to_json_object(self):
        json_object = {"obs_azimuth": self.obs_azimuth,
                       "obs_R": self.obs_R,
                       "obs_zenith": self.obs_zenith}
        return json_object


class ObservationPerspective(Element):
    def __init__(self):
        super().__init__()
        self.obs_o_x = 50
        self.obs_o_y = 50
        self.obs_o_z = 20
        self.obs_t_x = 50
        self.obs_t_y = 50
        self.obs_t_z = 0
        self.relative_height = False

    def init_obs_from_json(self, json_object):
        self.obs_o_x = json_object["observation"]["obs_o_x"]
        self.obs_o_y = json_object["observation"]["obs_o_y"]
        self.obs_o_z = json_object["observation"]["obs_o_z"]
        self.obs_t_x = json_object["observation"]["obs_t_x"]
        self.obs_t_y = json_object["observation"]["obs_t_y"]
        self.obs_t_z = json_object["observation"]["obs_t_z"]
        self.relative_height = json_object["observation"]["relative_height"]
        return self

    def to_json_object(self):
        json_object = {"obs_t_z": self.obs_t_z,
                       "obs_o_x": self.obs_o_x,
                       "obs_o_y": self.obs_o_y,
                       "obs_o_z": self.obs_o_z,
                       "relative_height": self.relative_height,
                       "obs_t_x": self.obs_t_x,
                       "obs_t_y": self.obs_t_y}
        return json_object


class ObservationFisheye(ObservationPerspective):
    def __init__(self):
        super().__init__()

