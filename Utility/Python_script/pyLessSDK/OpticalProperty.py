# coding: utf-8
from Element import Element


class OpticalItem(object):
    def __init__(self, op_name="", op_value="", op_type=1):
        self.op_name = op_name
        self.op_value = op_value
        self.op_type = op_type

    def get_op_name(self):
        return self.op_name

    def set_op_name(self, op_name):
        self.op_name = op_name

    def get_op_value(self):
        return self.op_value

    def set_op_value(self, op_value):
        self.op_value = op_value

    def get_op_type(self):
        return self.op_type

    def set_op_type(self, op_type):
        self.op_type = op_type


class OpticalProperties(Element):
    def __init__(self):
        super().__init__()
        self.optical_properties = [OpticalItem("birch_branch", "0.105,0.476;0.000,0.000;0.000,0.000", 0),
                                   OpticalItem("dark_soil_mollisol", "0.188,0.351;0.000,0.000;0.000,0.000", 0),
                                   OpticalItem("birch_leaf_green", "0.058,0.472;0.058,0.472;0.000,0.000", 0)]

    def init_ops_from_json(self, json_object):
        self.optical_properties.clear()
        op_node = json_object["scene"]["optical_properties"]
        for op_name in op_node:
            op_type = op_node[op_name]["Type"]
            op_value = op_node[op_name]["value"]
            op = OpticalItem(op_name, op_value, op_type)
            self.optical_properties.append(op)
        return self

    def to_json_object(self):
        json_object = {}
        for op_item in self.optical_properties:
            json_object_item = {"Type": op_item.op_type, "value": op_item.op_value}
            json_object[op_item.op_name] = json_object_item
        return json_object

    def is_op_exist(self, op_name):
        for op_item in self.optical_properties:
            if op_name == op_item.op_name:
                return True
        return False

    def add_optical_item(self, op_item):
        op_name = op_item.op_name
        if not self.is_op_exist(op_name):
            self.optical_properties.append(op_item)

    def get_optical_item(self, op_name):
        for op_item in self.optical_properties:
            if op_name == op_item.op_name:
                return op_item
        return None

    # #  refresh op database before running the simulation
    # def refresh_op_properties(self):
    #     for op_item in self.optical_properties:
    #         if op_item.op_type == 0:
    #             # get information from databse
