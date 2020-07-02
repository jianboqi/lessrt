# coding: utf-8
from Element import Element


class SensorType:
    PERSPECTIVE = "perspective"
    ORTHOGRAPHIC = "orthographic"
    CIRCULARFISHEYE = "CircularFisheye"
    PHOTONTRACING = "PhotonTracing"


class SensorBasic(Element):
    def __init__(self):
        super().__init__()
        self.sensor_type = "Base Sensor"
        self.thermal_radiation = False
        self.record_only_direct = 200
        self.image_height = 100
        self.image_width = 100
        self.repetitive_scene = 100
        self.film_type = "spectrum"
        self.bands = "600:2,900:2"
        self.no_data_value = -1


class SensorOrthographic(SensorBasic):
    def __init__(self):
        super().__init__()

        self.has_four_components_product = False
        self.cover_whole_scene = False
        self.sample_per_pixel = 128
        self.sub_region_width = 100
        self.sub_region_height = 100

    def init_sensor_from_json(self, json_object):
        self.sensor_type = json_object["sensor"]["sensor_type"]
        self.thermal_radiation = json_object["sensor"]["thermal_radiation"]
        self.record_only_direct = json_object["sensor"]["record_only_direct"]
        self.image_height = json_object["sensor"]["image_height"]
        self.image_width = json_object["sensor"]["image_width"]
        self.repetitive_scene = json_object["sensor"]["RepetitiveScene"]
        self.has_four_components_product = json_object["sensor"]["hasFourComponentProduct"]
        self.film_type = json_object["sensor"]["film_type"]
        self.bands = json_object["sensor"]["bands"]
        self.no_data_value = json_object["sensor"]["NoDataValue"]

        self.cover_whole_scene = json_object["sensor"]["orthographic"]["cover_whole_scene"]
        self.sample_per_pixel = json_object["sensor"]["orthographic"]["sample_per_square_meter"]
        self.sub_region_width = json_object["sensor"]["orthographic"]["sub_region_width"]
        self.sub_region_height = json_object["sensor"]["orthographic"]["sub_region_height"]

        return self

    def to_json_object(self):
        json_object = {"thermal_radiation": self.thermal_radiation,
                       "record_only_direct": self.record_only_direct,
                       "image_height": self.image_height,
                       "RepetitiveScene": self.repetitive_scene,
                       "hasFourComponentProduct": self.has_four_components_product,
                       "film_type": self.film_type,
                       "orthographic": {
                          "cover_whole_scene": self.cover_whole_scene,
                          "sample_per_square_meter": self.sample_per_pixel,
                          "sub_region_width": self.sub_region_width,
                          "sub_region_height": self.sub_region_height
                        },
                       "image_width": self.image_width,
                       "bands": self.bands,
                       "sensor_type": self.sensor_type,
                       "NoDataValue": self.no_data_value}
        return json_object


class SensorPhotonTracing(SensorBasic):
    def __init__(self):
        super().__init__()
        self.cover_whole_scene = False
        self.sample_per_pixel = 128
        self.sub_region_width = 100
        self.sub_region_height = 100

        self.virtual_detector_directions = ""
        self.sun_ray_resolution = 0.02
        self.number_Of_directions = 150
        self.BRF_product = True
        self.up_down_product = False
        self.virtual_directions = ""
        self.fPAR_product = False

    def init_sensor_from_json(self, json_object):
        self.sensor_type = json_object["sensor"]["sensor_type"]
        self.thermal_radiation = json_object["sensor"]["thermal_radiation"]
        self.record_only_direct = json_object["sensor"]["record_only_direct"]
        self.image_height = json_object["sensor"]["image_height"]
        self.image_width = json_object["sensor"]["image_width"]
        self.repetitive_scene = json_object["sensor"]["RepetitiveScene"]
        self.film_type = json_object["sensor"]["film_type"]
        self.bands = json_object["sensor"]["bands"]
        self.no_data_value = json_object["sensor"]["NoDataValue"]

        self.cover_whole_scene = json_object["sensor"]["orthographic"]["cover_whole_scene"]
        self.sample_per_pixel = json_object["sensor"]["orthographic"]["sample_per_square_meter"]
        self.sub_region_width = json_object["sensor"]["orthographic"]["sub_region_width"]
        self.sub_region_height = json_object["sensor"]["orthographic"]["sub_region_height"]

        self.virtual_detector_directions = json_object["sensor"]["PhotonTracing"]["virtualDetectorDirections"]
        self.sun_ray_resolution = json_object["sensor"]["PhotonTracing"]["sunRayResolution"]
        self.number_Of_directions = json_object["sensor"]["PhotonTracing"]["NumberOfDirections"]
        self.BRF_product = json_object["sensor"]["PhotonTracing"]["BRFProduct"]
        self.up_down_product = json_object["sensor"]["PhotonTracing"]["UpDownProduct"]
        self.virtual_directions = json_object["sensor"]["PhotonTracing"]["virtualDirections"]
        self.fPAR_product = json_object["sensor"]["PhotonTracing"]["fPARProduct"]
        return self

    def to_json_object(self):
        json_object = {"thermal_radiation": self.thermal_radiation,
                       "record_only_direct": self.record_only_direct,
                       "image_height": self.image_height,
                       "RepetitiveScene": self.repetitive_scene,
                       "film_type": self.film_type,
                       "PhotonTracing": {
                           "virtualDetectorDirections": self.virtual_detector_directions,
                           "sunRayResolution": self.sun_ray_resolution,
                           "NumberOfDirections": self.number_Of_directions,
                           "BRFProduct": self.BRF_product,
                           "UpDownProduct": self.up_down_product,
                           "virtualDirections": self.virtual_directions,
                           "fPARProduct": self.fPAR_product
                       },
                       "orthographic": {
                          "cover_whole_scene": self.cover_whole_scene,
                          "sample_per_square_meter": self.sample_per_pixel,
                          "sub_region_width": self.sub_region_width,
                          "sub_region_height": self.sub_region_height
                        },
                       "image_width": self.image_width,
                       "bands": self.bands,
                       "sensor_type": self.sensor_type,
                       "NoDataValue": self.no_data_value}
        return json_object


class SensorPerspective(SensorBasic):
    def __init__(self):
        super().__init__()
        self.has_four_components_product = False
        self.sample_per_pixel = 128
        self.fov_x = 40
        self.fov_y = 30
        self.fov_axis = "diagonal"

    def init_sensor_from_json(self, json_object):
        self.sensor_type = json_object["sensor"]["sensor_type"]
        self.thermal_radiation = json_object["sensor"]["thermal_radiation"]
        self.record_only_direct = json_object["sensor"]["record_only_direct"]
        self.image_height = json_object["sensor"]["image_height"]
        self.image_width = json_object["sensor"]["image_width"]
        self.repetitive_scene = json_object["sensor"]["RepetitiveScene"]
        self.has_four_components_product = json_object["sensor"]["hasFourComponentProduct"]
        self.film_type = json_object["sensor"]["film_type"]
        self.bands = json_object["sensor"]["bands"]
        self.no_data_value = json_object["sensor"]["NoDataValue"]

        self.sample_per_pixel = json_object["sensor"]["perspective"]["sample_per_square_meter"]
        self.fov_x = json_object["sensor"]["perspective"]["fovx"]
        self.fov_y = json_object["sensor"]["perspective"]["fovy"]
        self.fov_axis = json_object["sensor"]["perspective"]["fovAxis"]

        return self

    def to_json_object(self):
        json_object = {"thermal_radiation": self.thermal_radiation,
                       "record_only_direct": self.record_only_direct,
                       "image_height": self.image_height,
                       "RepetitiveScene": self.repetitive_scene,
                       "hasFourComponentProduct": self.has_four_components_product,
                       "film_type": self.film_type,
                       "perspective": {
                          "sample_per_square_meter": self.sample_per_pixel,
                          "fovx": self.fov_x,
                          "fovy": self.fov_y,
                          "fovAxis": self.fov_axis
                        },
                       "image_width": self.image_width,
                       "bands": self.bands,
                       "sensor_type": self.sensor_type,
                       "NoDataValue": self.no_data_value}
        return json_object


class SensorFisheye(SensorBasic):
    def __init__(self):
        super().__init__()
        self.sample_per_square_meter = 128
        self.angular_fov = 165
        self.projection_type = "equisolid"

    def init_sensor_from_json(self, json_object):
        self.sensor_type = json_object["sensor"]["sensor_type"]
        self.thermal_radiation = json_object["sensor"]["thermal_radiation"]
        self.record_only_direct = json_object["sensor"]["record_only_direct"]
        self.image_height = json_object["sensor"]["image_height"]
        self.image_width = json_object["sensor"]["image_width"]
        self.repetitive_scene = json_object["sensor"]["RepetitiveScene"]
        self.film_type = json_object["sensor"]["film_type"]
        self.bands = json_object["sensor"]["bands"]
        self.no_data_value = json_object["sensor"]["NoDataValue"]

        self.sample_per_pixel = json_object["sensor"]["CircularFisheye"]["sample_per_square_meter"]
        self.angular_fov = json_object["sensor"]["CircularFisheye"]["angular_fov"]
        self.projection_type = json_object["sensor"]["CircularFisheye"]["projection_type"]

        return self

    def to_json_object(self):
        json_object = {"thermal_radiation": self.thermal_radiation,
                       "record_only_direct": self.record_only_direct,
                       "image_height": self.image_height,
                       "RepetitiveScene": self.repetitive_scene,
                       "film_type": self.film_type,
                       "CircularFisheye": {
                          "angular_fov": self.angular_fov,
                          "projection_type": self.projection_type,
                          "sample_per_square_meter": self.sample_per_pixel
                        },
                       "image_width": self.image_width,
                       "bands": self.bands,
                       "sensor_type": self.sensor_type,
                       "NoDataValue": self.no_data_value}
        return json_object
