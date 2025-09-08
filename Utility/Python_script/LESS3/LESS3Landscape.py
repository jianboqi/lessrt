# coding: utf-8
# The wrapper class for objects and instances
import os.path
import mitsuba as mi
from Landscape import Landscape
import numpy as np


class LESS3Landscape(object):
    def __init__(self, less_landscape: Landscape):
        self.less_landscape = less_landscape

    def get_dict(self):
        param_dir = self.less_landscape.get_sim().get_parameters_dir()


        # objects get_spectrum_name
        objects = self.less_landscape.get_objects()
        shape_group_list = []
        optical_name_list = []
        # for shape_group_name in objects:
        #     shape_group_unique_name = "zz" + shape_group_name + "_shapegroup"
        #     shape_group_dict = {shape_group_unique_name: {
        #         "type": "shapegroup"
        #     }}
        #     for comp_name in objects[shape_group_name]:
        #         shape_group_dict[shape_group_unique_name][comp_name[0:-4]] = {"type": "obj"}
        #         shape_group_dict[shape_group_unique_name][comp_name[0:-4]]["filename"] = os.path.join(param_dir, comp_name)
        #         shape_group_dict[shape_group_unique_name][comp_name[0:-4]]["bsdf"] = {"type": "ref", "id": objects[shape_group_name][comp_name]["op_name"]}
        #         if objects[shape_group_name][comp_name]["op_name"] not in optical_name_list:
        #             optical_name_list.append(objects[shape_group_name][comp_name]["op_name"])
        #         shape_group_dict[shape_group_unique_name][comp_name[0:-4]]["face_normals"] = True
        #     shape_group_list.append(shape_group_dict)

        # instances
        instances = self.less_landscape.get_instances()
        instance_list = []
        temp_x = 999999
        temp_z = 999999
        intersections = [0,0,0]
        for shape_group_name in instances:
            shape_group_unique_name = "zz" + shape_group_name + "_shapegroup"
            # shapegroup and spectrum
            shape_group_dict = {shape_group_unique_name: {
                "type": "shapegroup"
            }}
            for comp_name in objects[shape_group_name]:
                shape_group_dict[shape_group_unique_name][comp_name[0:-4]] = {"type": "obj"}
                shape_group_dict[shape_group_unique_name][comp_name[0:-4]]["filename"] = os.path.join(param_dir, comp_name)
                shape_group_dict[shape_group_unique_name][comp_name[0:-4]]["bsdf"] = {"type": "ref", "id": objects[shape_group_name][comp_name]["op_name"]}
                if objects[shape_group_name][comp_name]["op_name"] not in optical_name_list:
                    optical_name_list.append(objects[shape_group_name][comp_name]["op_name"])
                shape_group_dict[shape_group_unique_name][comp_name[0:-4]]["face_normals"] = True
            shape_group_list.append(shape_group_dict)

            positions = instances[shape_group_name]
            for i, pos in enumerate(positions):
                instance_name = "zz" + shape_group_name+"_instance_"+str(i)
                instance_dict = {instance_name: {"type": "instance"}}
                x = 0.5 * self.less_landscape.get_terrain().get_extent_width() - pos[0]
                z = 0.5 * self.less_landscape.get_terrain().get_extent_height() - pos[1]
                if self.less_landscape.get_terrain().terrain_type != "PLANE":
                    if temp_x != x or temp_z != z:
                        temp_x = x
                        temp_z = z
                        obj_file_path = os.path.join(self.less_landscape.get_sim().get_parameters_dir(), self.less_landscape.get_terrain().terr_file)
                        ray_origin = np.array([x, 9999, z])  # 向量起点
                        ray_direction = np.array([0, -1, 0])  # 向量方向
                        intersections = self.__intersect_obj_with_ray(ray_origin, ray_direction, obj_file_path)
                    # if intersections:
                    #     print("交点坐标：")
                    #     for intersection in intersections:
                    #         print(intersection)
                    # else:
                    #     print("没有交点")
                    y = pos[2] + intersections[1]
                else:
                    y = pos[2]

                instance_dict[instance_name]["to_world"] = mi.ScalarTransform4f().translate([x, y, z]).rotate([0, 1, 0], pos[3])
                instance_dict[instance_name]["shapegroup"] = {"type": "ref", "id": shape_group_unique_name}
                instance_list.append(instance_dict)


        # terrain
        terrain_dict = self.__get_terrain_dict()
        # terrain_optical_name
        optical_name_list.append(self.less_landscape.get_terrain().get_optical())
        # 下一行代码用于测试
        # optical_name_list.append("birch_branch")

        # spectrum
        spectrum_dict_list = self.__get_spectrum_dict_list(optical_name_list)



        return shape_group_list, instance_list, terrain_dict, spectrum_dict_list


    def __get_terrain_dict(self):
        param_dir = self.less_landscape.get_sim().get_parameters_dir()
        # result_dir = os.path.dirname(self.less_landscape.get_sim().get_dist_file())
        terrain_brdf_type = self.less_landscape.get_terrain().get_terr_brdf_type()
        terrain_optical = self.less_landscape.get_terrain().get_optical()
        terrain_file = self.less_landscape.get_terrain().terr_file
        terrain_type = self.less_landscape.get_terrain().terrain_type
        terrain_half_width = self.less_landscape.get_terrain().get_extent_width() * 0.5
        terrain_half_height = self.less_landscape.get_terrain().get_extent_height() * 0.5
        # spectral_bands = list(map(lambda x: float(x.split(":")[0]),
        #                           self.less_landscape.get_sim().get_scene().get_sensor().get_spectral_bands().split(
        #                               ",")))
        # spectral_bands_str = ",".join(map(str, spectral_bands))

        if terrain_brdf_type != "Spatially Uniform":
            raise Exception("Spatially Uniform terrain type is not supported for this running")

        terrain_dict = {}
        terrain_dict_temp = {}
        if terrain_type == "PLANE":
            terrain_dict_temp = {
                "type": "rectangle",
                "bsdf":{
                    "type":"ref",
                    "id":terrain_optical
                },
                'to_world': mi.ScalarTransform4f().rotate([1, 0, 0], -90).scale([terrain_half_width, terrain_half_height, 1])
            }

        elif terrain_type == "MESH":
            terrain_dict_temp = {
                "type": "obj",
                "filename": os.path.join(param_dir, terrain_file),
                "bsdf": {
                    "type": "ref",
                    "id": terrain_optical
                },
                "face_normals":True
            }
            # raise Exception("MESH is not supported for this running")

        elif terrain_type == "RASTER_TO_MESH":
            terrain_dict_temp = {
                "type": "obj",
                "filename": os.path.join(param_dir, "_scenefile", f"{terrain_file}.obj"),
                "bsdf": {
                    "type": "ref",
                    "id": terrain_optical
                },
                "face_normals": True
            }
            raise Exception("Currently,maybe RASTER_TO_MESH is not supported for this running")

        terrain_dict["terrain"] = terrain_dict_temp

        return terrain_dict


    def __get_spectrum_dict_list(self, optical_name_list):

        spectrum_dict_list = []
        for optical_name in optical_name_list:
            optical_item = self.less_landscape.get_op_item(optical_name).op_value
            # print(optical_item)
            reflectance_front_values = optical_item.split(";")[0]
            reflectance_back_values = optical_item.split(";")[1]
            transmittance_values = optical_item.split(";")[2]

            spectral_bands = list(map(lambda x: float(x.split(":")[0]),
                                      self.less_landscape.get_sim().get_scene().get_sensor().get_spectral_bands().split(
                                          ",")))
            bands_num = len(spectral_bands)

            is_close_to_zero_for_rfv = all(abs(float(x)) <= 1e-9 for x in reflectance_front_values.split(","))
            is_close_to_zero_for_rbv = all(abs(float(x)) <= 1e-9 for x in reflectance_back_values.split(","))
            is_close_to_zero_for_tv = all(abs(float(x)) <= 1e-9 for x in transmittance_values.split(","))
            spectrum_dict = {}
            if bands_num == 1:
                str_value_name = 'value'  # 之前的测试
                reflectance_front_values = float(reflectance_front_values)
                reflectance_back_values = float(reflectance_back_values)
                transmittance_values = float(transmittance_values)
                # 注意这里的是为单波段时设置的波宽 # 下面部分可以注释掉如果加的话，每次反演时，某一波段的反射率反演会临近为两个0.5nm旁边的反射率综合得到（没有加这个功能）=====================
                # spectral_bands = [spectral_bands[0]-0.5, spectral_bands[0]+0.5]
                # reflectance_front_values = reflectance_front_values + "," + reflectance_front_values
                # reflectance_back_values = reflectance_back_values + "," + reflectance_back_values
                # transmittance_values = transmittance_values + "," + transmittance_values
                # ==============================================================================================
            else:
                str_value_name = 'values'
                # 下面部分可以注释掉如果加的话，每次反演时，某一波段的反射率反演会临近为两个0.5nm旁边的反射率综合得到（没有加这个功能）============================================================
                # spectral_bands[0] = spectral_bands[0] + 0.5
                # spectral_bands[-1] = spectral_bands[-1] - 0.5
                # temp_bandlist = []
                # for band in spectral_bands:
                #     temp_bandlist.append(band - 0.5)
                #     temp_bandlist.append(band + 0.5)
                # spectral_bands = temp_bandlist
                # temp_reflectance_front_values = []
                # temp_reflectance_back_values = []
                # temp_transmittance_values = []
                # for value in reflectance_front_values.split(','):
                #     temp_reflectance_front_values.append(value)
                #     temp_reflectance_front_values.append(value)
                # reflectance_front_values = ','.join(temp_reflectance_front_values)
                # for value in reflectance_back_values.split(','):
                #     temp_reflectance_back_values.append(value)
                #     temp_reflectance_back_values.append(value)
                # reflectance_back_values = ','.join(temp_reflectance_front_values)
                # for value in transmittance_values.split(','):
                #     temp_transmittance_values.append(value)
                #     temp_transmittance_values.append(value)
                # transmittance_values = ','.join(temp_reflectance_front_values)
                # 结束注释=================================================================

            str_spectral_bands = ",".join(map(str, spectral_bands))
            if is_close_to_zero_for_tv is not True:
                spectrum_dict[optical_name] = {
                    'type': 'mixbsdf',
                    'twosided_id': {
                        'type': 'twosided',
                        'diffuse_id1': {
                            'type': 'diffuse',
                            'reflectance': {
                                'type': 'irregular',
                                'wavelengths': str_spectral_bands,
                                str_value_name: reflectance_front_values
                            }
                        },
                        'diffuse_id2': {
                            'type': 'diffuse',
                            'reflectance': {
                                'type': 'irregular',
                                'wavelengths': str_spectral_bands,
                                str_value_name: reflectance_back_values
                            }
                        }
                    },
                    'principledthin_id': {
                        'type': 'principledthin',
                        'base_color': {
                            'type': 'irregular',
                            'wavelengths': str_spectral_bands,
                            str_value_name: transmittance_values
                        },
                        'diff_trans': {
                            'type': 'uniform',
                            'value': 2.0
                        },
                        'specular_reflectance_sampling_rate': 0,
                        'specular_transmittance_sampling_rate': 0,
                        'roughness': {
                            'type': 'uniform',
                            'value': 1.0
                        }
                    }
                }

                if bands_num == 1:
                    spectrum_dict[optical_name]["twosided_id"]["diffuse_id1"]["reflectance"]["type"] = "spectrum"
                    del spectrum_dict[optical_name]["twosided_id"]["diffuse_id1"]["reflectance"]["wavelengths"]
                    spectrum_dict[optical_name]["twosided_id"]["diffuse_id2"]["reflectance"]["type"] = "spectrum"
                    del spectrum_dict[optical_name]["twosided_id"]["diffuse_id2"]["reflectance"]["wavelengths"]
                    spectrum_dict[optical_name]["principledthin_id"]["base_color"]["type"] = "spectrum"
                    del spectrum_dict[optical_name]["principledthin_id"]["base_color"]["wavelengths"]
                if reflectance_front_values == reflectance_back_values:
                    del spectrum_dict[optical_name]["twosided_id"]["diffuse_id2"]

            elif is_close_to_zero_for_tv and is_close_to_zero_for_rfv is not True and is_close_to_zero_for_rbv is not True:
                spectrum_dict[optical_name] = {
                        'type': 'twosided',
                        'diffuse_id1': {
                            'type': 'diffuse',
                            'reflectance': {
                                'type': 'irregular',
                                'wavelengths': str_spectral_bands,
                                str_value_name: reflectance_front_values
                            }
                        },
                        'diffuse_id2': {
                            'type': 'diffuse',
                            'reflectance': {
                                'type': 'irregular',
                                'wavelengths': str_spectral_bands,
                                str_value_name: reflectance_back_values
                            }
                        }
                    }

                if bands_num == 1:
                    spectrum_dict[optical_name]["diffuse_id1"]["reflectance"]["type"] = "spectrum"
                    del spectrum_dict[optical_name]["diffuse_id1"]["reflectance"]["wavelengths"]
                    spectrum_dict[optical_name]["diffuse_id2"]["reflectance"]["type"] = "spectrum"
                    del spectrum_dict[optical_name]["diffuse_id2"]["reflectance"]["wavelengths"]
                if reflectance_front_values == reflectance_back_values:
                    del spectrum_dict[optical_name]["diffuse_id2"]

            # elif is_close_to_zero_for_tv and is_close_to_zero_for_rbv and is_close_to_zero_for_rfv is not True:
            else:
                if is_close_to_zero_for_rfv is True and bands_num != 1:  # possibilities
                    values = reflectance_front_values.split(',')
                    values[-1] = str(float(values[-1]) + 0.0000000000001)
                    reflectance_front_values = ','.join(values)
                spectrum_dict[optical_name] = {
                    'type':'diffuse',
                    'reflectance':{
                        'type':'irregular',
                        'wavelengths':str_spectral_bands,
                        str_value_name: reflectance_front_values
                    }
                }

                if bands_num == 1:
                    spectrum_dict[optical_name]["reflectance"]["type"] = "spectrum"
                    del spectrum_dict[optical_name]["reflectance"]["wavelengths"]

            spectrum_dict_list.append(spectrum_dict)

        return spectrum_dict_list

    # __intersect_obj_with_ray还没测试好
    def __intersect_obj_with_ray(self, ray_origin, ray_direction, obj_file_path):
        def load_obj(file_path):
            vertices = []
            faces = []
            with open(file_path, 'r') as file:
                for line in file:
                    if line.startswith('v '):
                        _, x, y, z = line.split()
                        vertices.append((float(x), float(y), float(z)))
                    elif line.startswith('f '):
                        face = [int(idx.split('/')[0]) - 1 for idx in line.split()[1:]]
                        faces.append(face)
            return np.array(vertices), faces

        def intersect_triangle(p0, d, v0, v1, v2):
            eps = 1e-6
            edge1 = v1 - v0
            edge2 = v2 - v0
            h = np.cross(d, edge2)
            a = np.dot(edge1, h)

            if abs(a) < eps:
                return None

            f = 1.0 / a
            s = p0 - v0
            u = f * np.dot(s, h)

            if u < 0.0 or u > 1.0:
                return None

            q = np.cross(s, edge1)
            v = f * np.dot(d, q)

            if v < 0.0 or u + v > 1.0:
                return None

            t = f * np.dot(edge2, q)

            if t > eps:
                intersection = p0 + t * d
                return intersection
            else:
                return None

        def intersect_model(p0, d, vertices, faces):
            closest_intersection = None
            min_distance = float('inf')

            for face in faces:
                if len(face) == 3:
                    v0, v1, v2 = vertices[face]
                    intersection = intersect_triangle(p0, d, v0, v1, v2)
                elif len(face) == 4:
                    v0, v1, v2, v3 = vertices[face]
                    intersection1 = intersect_triangle(p0, d, v0, v1, v2)
                    intersection2 = intersect_triangle(p0, d, v0, v2, v3)
                    intersection = intersection1 if intersection1 is not None else intersection2
                else:
                    continue

                if intersection is not None:
                    distance = np.linalg.norm(intersection - p0)
                    if distance < min_distance:
                        min_distance = distance
                        closest_intersection = intersection

            return closest_intersection

        def preprocess_faces(ray_origin, ray_direction, vertices, faces):
            face_bounds = []
            for face in faces:
                face_vertices = vertices[face]
                min_y = np.min(face_vertices[:, 1])
                max_y = np.max(face_vertices[:, 1])
                face_bounds.append((min_y, max_y))
            return vertices, faces

        vertices, faces = load_obj(obj_file_path)
        closest_intersection = intersect_model(ray_origin, ray_direction, vertices, faces)
        return closest_intersection

