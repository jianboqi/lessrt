# coding: utf-8
import os
from Element import Element
import shutil
from LSBoundingBox import LSBoundingBox
from Utility import OBJHelper


class SceneObject(Element):
    def __init__(self, name=None, components={}):
        super().__init__()
        self.scene_obj_name = name
        self.scene_obj_components = components

    def set_scene_obj_name(self, name):
        self.scene_obj_name = name

    def get_scene_obj_name(self):
        return self.scene_obj_name

    def add_component_from_file(self, obj_path, op_name, temperature="-", color="0x006400ff"):
        # get filename
        (dir_path, file_name) = os.path.split(obj_path)
        component_name = self.scene_obj_name + "_" + file_name
        if file_name not in self.scene_obj_components:
            self.scene_obj_components[component_name] = {"op_name": op_name, "temperature": temperature, "color": color,
                                                    "obj_file_path": obj_path}
        else:
            print("Warning: Component " + component_name + "already exists.")

    @staticmethod
    def read_components(obj_path):
        pass


class SceneObjects(Element):
    def __init__(self):
        super().__init__()
        self.cache_OBJ_file = True
        self.tree_pos_file = "instances.txt"
        self.objects_file = "objects.txt"

        # object and instances data
        self.objects = {}
        self.instances = {}

    def init_objects_from_json(self, json_object):
        self.cache_OBJ_file = json_object["scene"]["forest"]["CacheOBJFile"]
        self.tree_pos_file = json_object["scene"]["forest"]["tree_pos_file"]
        self.objects_file = json_object["scene"]["forest"]["objects_file"]
        # objects and instances
        self.load_objects()
        self.load_instances()
        return self

    def to_json_object(self):
        json_obj = {"CacheOBJFile": self.cache_OBJ_file,
                    "tree_pos_file": self.tree_pos_file,
                    "objects_file": self.objects_file}

        # save objects and instances
        self.save_objects()
        self.save_instances()
        return json_obj

    def load_objects(self):
        objects_file_path = os.path.join(self.get_sim().get_sim_dir(), "Parameters", "objects.txt")
        if os.path.exists(objects_file_path):
            f = open(objects_file_path)
            for line in f:
                arr = line.rstrip().split(" ")
                components = {}
                for i in range(1, len(arr), 4):
                    components[arr[i]] = {"op_name": arr[i+1], "temperature": arr[i+2], "color": arr[i+3]}
                self.objects[arr[0]] = components
            f.close()

    def load_instances(self):
        instances_file_path = os.path.join(self.get_sim().get_sim_dir(), "Parameters", "instances.txt")
        if os.path.exists(instances_file_path):
            f = open(instances_file_path)
            for line in f:
                arr = line.strip().split(" ")
                obj_name = arr[0]
                coord = list(map(lambda x: float(x), arr[1:]))
                if obj_name in self.instances:
                    self.instances[obj_name].append(coord)
                else:
                    self.instances[obj_name] = [coord]
            f.close()

    def save_objects(self):
        if len(self.objects) != 0:
            objects_file_path = os.path.join(self.get_sim().get_sim_dir(), "Parameters", "objects.txt")
            f = open(objects_file_path, "w")
            for obj_name in self.objects:
                out_str = obj_name
                for comp_name in self.objects[obj_name]:
                    out_str += " " + comp_name
                    out_str += " " + self.objects[obj_name][comp_name]["op_name"]
                    out_str += " " + self.objects[obj_name][comp_name]["temperature"]
                    out_str += " " + self.objects[obj_name][comp_name]["color"]
                out_str += "\n"
                f.write(out_str)
            f.close()

    def save_instances(self):
        if len(self.instances) != 0:
            instances_file_path = os.path.join(self.get_sim().get_sim_dir(), "Parameters", "instances.txt")
            f = open(instances_file_path, "w")
            for obj_name in self.instances:
                for coord in self.instances[obj_name]:
                    out_str = obj_name
                    out_str += " " + " ".join(list(map(lambda x: str(x), coord))) + "\n"
                    f.write(out_str)
            f.close()

    def __is_scene_object_valid(self, scene_object: SceneObject):
        # Check components
        if len(scene_object.scene_obj_components) == 0:
            print("Error: scene object " + scene_object.get_scene_obj_name() + "does not have components.")
            return False
        # Check optical property
        for component_name in scene_object.scene_obj_components:
            op_name = scene_object.scene_obj_components[component_name]["op_name"]
            if not self.get_sim().get_scene().get_landscape().optical_properties.is_op_exist(op_name):
                print("Error: optical property " + op_name + " does not exists, please define first.")
                return False
        return True

    def __is_scene_object_exist(self, obj_name):
        if obj_name in self.objects:
            return True
        return False

    def __copy_components(self, components, override_file=True):
        for comp_name in components:
            obj_file_path = components[comp_name]["obj_file_path"]
            dst_file_path = os.path.join(self.get_sim().get_sim_dir(), "Parameters", comp_name)
            if os.path.exists(dst_file_path):
                if override_file:
                    shutil.copy(obj_file_path, dst_file_path)
            else:
                shutil.copy(obj_file_path, dst_file_path)

    def __copy_components_with_translate(self, components, translate_to_origin, override_file=True):
        obj_bound_box = LSBoundingBox()
        for comp_name in components:
            obj_file_path = components[comp_name]["obj_file_path"]
            bound_box = OBJHelper.get_obj_bound(obj_file_path)
            obj_bound_box.add_child(bound_box)
        offsetx = - 0.5 * (obj_bound_box.minX + obj_bound_box.maxX)
        offsey = - obj_bound_box.minY
        offsetz = -0.5 * (obj_bound_box.minZ + obj_bound_box.maxZ)
        if translate_to_origin == "xy":
            offsey = 0
        for comp_name in components:
            obj_file_path = components[comp_name]["obj_file_path"]
            dst_file_path = os.path.join(self.get_sim().get_sim_dir(), "Parameters", comp_name)
            write_file = False
            if os.path.exists(dst_file_path):
                if override_file:
                    write_file = True
            else:
                write_file = True

            if write_file:
                fout = open(dst_file_path, "w")
                fin = open(obj_file_path)
                for line in fin:
                    if line.startswith("v"):
                        (x, y, z) = list(map(lambda xx: float(xx), line[1:].strip().split(" ")))
                        newx, newy, new = x+offsetx, y+offsey, z+offsetz
                        fout.write("v %f %f %f\n" % (newx, newy, new))
                    else:
                        fout.write(line)
                fin.close()
                fout.close()

    # add a object
    def add_object(self, scene_object: SceneObject, override_file=True, translate_to_origin="no"):
        obj_name = scene_object.get_scene_obj_name()
        # check if scene object is valid
        if self.__is_scene_object_valid(scene_object):
            if obj_name in self.objects:
                print("Warning: scene object " + obj_name + " already exists.")
            else:
                self.objects[obj_name] = scene_object.scene_obj_components
                if translate_to_origin == "no":
                    self.__copy_components(scene_object.scene_obj_components)
                else:
                    print("INFO: Translating obj...")
                    self.__copy_components_with_translate(scene_object.scene_obj_components,
                                                          translate_to_origin)

    def place_object_to(self, obj_name, x=50.0, y=50.0, z=0.0, rotate=0.0):
        if not self.__is_scene_object_exist(obj_name):
            print("Error: scene object " + obj_name + " doest not exist.")
        else:
            coord = [x, y, z, rotate]
            if obj_name in self.instances:
                self.instances[obj_name].append(coord)
            else:
                self.instances[obj_name] = [coord]

    # For open the project with LESS GUI, this function must be executed before
    def calculate_object_bounding_box(self):
        if len(self.objects) > 0:
            for obj_name in self.objects:
                obj_bound_box = LSBoundingBox()
                for comp_name in self.objects[obj_name]:
                    comp_obj_file_path = os.path.join(self.get_sim().get_sim_dir(), "Parameters", comp_name)
                    comp_bound_box = LSBoundingBox()
                    f = open(comp_obj_file_path)
                    for line in f:
                        if line.startswith("v "):
                            arr = line.strip().split(" ")
                            (x, y, z) = list(map(lambda xx: float(xx), arr[1:]))
                            if x < comp_bound_box.minX:
                                comp_bound_box.minX = x
                            if y < comp_bound_box.minY:
                                comp_bound_box.minY = y
                            if z < comp_bound_box.minZ:
                                comp_bound_box.minZ = z
                            if x > comp_bound_box.maxX:
                                comp_bound_box.maxX = x
                            if y > comp_bound_box.maxY:
                                comp_bound_box.maxY = y
                            if z > comp_bound_box.maxZ:
                                comp_bound_box.maxZ = z
                    f.close()
                    obj_bound_box.add_child(comp_bound_box)
                instances_file_path = os.path.join(self.get_sim().get_sim_dir(), "Parameters", "objects_boundingbox.txt")
                f = open(instances_file_path, "w")
                f.write(obj_name + ":" + obj_bound_box.to_string()+"\n")
                f.close()