# coding: utf-8
from OpticalProperty import OpticalProperties
from Terrain import Terrain
from SceneObjects import SceneObjects, SceneObject
from Element import Element


class Landscape(Element):
    def __init__(self):
        super().__init__()
        # forest
        self.scene_objects = SceneObjects()

        # terrain
        self.terrain = Terrain()

        # optical properties
        self.optical_properties = OpticalProperties()

        # temperature
        self.temperature_properties = {}

        # others
        self.extra_scene = ""

    def init_landscape_from_json(self, json_object):
        # forest
        scene_objects = SceneObjects()
        scene_objects.set_sim(self.get_sim())
        scene_objects.init_objects_from_json(json_object)
        self.scene_objects = scene_objects

        # terrain
        terrain = Terrain()
        terrain.set_sim(self.get_sim())
        terrain.init_terrain_from_json(json_object)
        self.terrain = terrain

        # optical properties
        ops = OpticalProperties()
        ops.init_ops_from_json(json_object)
        self.optical_properties = ops

        # temperature
        self.temperature_properties = json_object["scene"]["temperature_properties"]

        # others
        self.extra_scene = json_object["scene"]["extra_scene"]

        return self

    def to_json_object(self, sim):
        json_obj = {"forest": self.scene_objects.to_json_object(),
                    "terrain": self.terrain.to_json_object(),
                    "optical_properties": self.optical_properties.to_json_object(),
                    "temperature_properties": self.temperature_properties,
                    "extra_scene": self.extra_scene}
        return json_obj

    def add_op_item(self, op_item):
        self.optical_properties.add_optical_item(op_item)

    def add_object(self, scene_object: SceneObject):
        self.scene_objects.add_object(scene_object)

    def place_object(self, obj_name, x=50.0, y=50.0, z=0.0, rotate=0.0):
        self.scene_objects.place_object_to(obj_name, x, y, z, rotate)
