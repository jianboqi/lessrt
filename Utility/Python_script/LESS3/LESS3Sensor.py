# coding: utf-8
# This is a wrapper class for  sensor.
# from logging import raiseExceptions
from Sensor import SensorOrthographic, SensorPerspective
import mitsuba as mi
import numpy as np
# from box import Box


class LESS3Sensor(object):
    def __init__(self, sensor):
        self.sensor = sensor


    def get_dict(self):
        # sensor_config = Box()
        if isinstance(self.sensor, SensorOrthographic):
            sensor_dict = {
                'type': 'orthographic',
                'near_clip': 0.000001,
                'far_clip': 10000000000,
                'to_world': self.__get_to_world_config(),
                "film": self.__get_film_config(),
                "sampler": self.__get_sampler_config(),
            }
            # Box=====================================================
            # sensor_config.type = 'orthographic'
            # sensor_config.near_clip = 0.0000001
            # sensor_config.far_clip = 10000000000
            # sensor_config.to_world = mi.ScalarTransform4f.look_at(
            #     origin=[0, 3000, 0],
            #     target=[0, 0, 0],
            #     up=[0, 0, 1]
            # ) @ mi.ScalarTransform4f.scale([self.sensor.sub_region_width*0.5, self.sensor.sub_region_height*0.5, 1])
            # sensor_config.film = self.__get_film_config()
            # sensor_config.sampler = self.__get_sampler_config()
            # sensor_dict = sensor_config.to_dict()
            return sensor_dict
        # return "Sensor type is not supported"

        elif isinstance(self.sensor, SensorPerspective):
            sensor_dict = {
                'type': 'perspective',
                'near_clip': 0.0000001,
                'far_clip': 10000000000,
                'to_world': self.__get_to_world_config(),
                "film": self.__get_film_config(),
                "sampler": self.__get_sampler_config(),  # 采样器
                "fov": self.__get_fov_config(),
                "fov_axis": "diagonal"
            }

            return sensor_dict

        raise Exception("Sensor type is not supported")

    # @classmethod
    # def get_to_world_config_orthographic(cls, sensor_obs_zenith, sensor_obs_azimuth, obs_radius):
    #     # sensor_obs_zenith = sensor_obs_zenith_azimuth[0]
    #     # sensor_obs_azimuth = sensor_obs_zenith_azimuth[1]
    #     # obs_radius = self.less_scene.get_observation().obs_R
    #     x, y, z, target_x, target_y, target_z, phi = 0, 0, 0, 0, 0, 0, 0
    #     theta = float(sensor_obs_zenith) / 180.0 * np.pi
    #     phi_degree = float(sensor_obs_azimuth)
    #     phi = -(phi_degree - 90) / 180.0 * np.pi
    #     x = -obs_radius * np.sin(theta) * np.cos(phi) + target_x
    #     z = obs_radius * np.sin(theta) * np.sin(phi) + target_z
    #     y = obs_radius * np.cos(theta) + target_y
    #     if abs(x - target_x) < 0.00000001 and abs(z - target_z) < 0.00000001:
    #         x1 = np.cos(phi)
    #         z1 = -np.sin(phi)
    #     else:
    #         xx, yy, zz = target_x - x, target_y - y, target_z - z
    #         x1 = -xx * yy / (xx * xx + zz * zz)
    #         z1 = -yy * zz / (xx * xx + zz * zz)
    #
    #     to_world_dict = {
    #         'to_world': mi.ScalarTransform4f.look_at(
    #             origin=[x, y, z],
    #             target=[target_x, target_y, target_z],
    #             up=[x1, 1, z1]
    #         ) @ mi.ScalarTransform4f.scale(
    #             [self.sensor.sub_region_width * 0.5, self.less_scene.get_sensor().sub_region_height * 0.5,
    #              1])
    #     }


    def __get_to_world_config(self):
        # to_world_dict = {
        #     'to_world': mi.ScalarTransform4f.look_at(
        #         origin=[0, 3000, 0],
        #         target=[0, 0, 0],
        #         up=[0, 0, 1]
        #     ) @ mi.ScalarTransform4f.scale([self.sensor.sub_region_width * 0.5, self.sensor.sub_region_height * 0.5, 1])
        # }
        x, y, z, target_x, target_y, target_z, phi = 0, 0, 0, 0, 0, 0, 0
        if self.sensor.sensor_type == "orthographic":
            obs_radius = self.sensor.get_sim().get_scene().get_observation().obs_R
            obs_zenith = self.sensor.get_sim().get_scene().get_observation().obs_zenith
            obs_azimuth = self.sensor.get_sim().get_scene().get_observation().obs_azimuth
            theta = float(obs_zenith) / 180.0 * np.pi
            phi_degree = float(obs_azimuth)
            phi = -(phi_degree - 90) / 180.0 * np.pi

            x = -obs_radius * np.sin(theta) * np.cos(phi) + target_x
            z = obs_radius * np.sin(theta) * np.sin(phi) + target_z
            y = obs_radius * np.cos(theta) + target_y

        elif self.sensor.sensor_type == "perspective":

            scene_width = self.sensor.get_sim().get_scene().get_landscape().get_terrain().extent_width
            scene_height = self.sensor.get_sim().get_scene().get_landscape().get_terrain().extent_height

            x = scene_width * 0.5 - self.sensor.get_sim().get_scene().get_observation().obs_o_x
            z = scene_height * 0.5 - self.sensor.get_sim().get_scene().get_observation().obs_o_y
            y = self.sensor.get_sim().get_scene().get_observation().obs_o_z
            target_x = scene_width * 0.5 - self.sensor.get_sim().get_scene().get_observation().obs_t_x
            target_y = self.sensor.get_sim().get_scene().get_observation().obs_t_z
            target_z = scene_height * 0.5 - self.sensor.get_sim().get_scene().get_observation().obs_t_y
            if self.sensor.get_sim().get_scene().get_observation().relative_height:
                raise Exception("Relative height is not supported")
                # y += self.getCameraAltitudeHeight(main_scene_xml_file_prifix, x, z)
                # target_y += self.getCameraAltitudeHeight(main_scene_xml_file_prifix, x, z)
            phi = -(180 - 90) / 180.0 * np.pi
        else:
            raise Exception("Sensor type is not supported")
            # lookat_node.setAttribute("origin", str(x) + "," + str(y) + "," + str(z))
            # lookat_node.setAttribute("target", str(target_x) + "," + str(target_y) + "," + str(target_z))
            # if abs(x - target_x) < 0.00000001 and abs(z - target_z) < 0.00000001:
            #     upx = np.cos(phi)
            #     upz = -np.sin(phi)
            #     lookat_node.setAttribute("up", "%.5f" % upx + "," + "0" + "," + "%.5f" % upz)
            # else:
            #     xx, yy, zz = target_x - x, target_y - y, target_z - z
            #     x1 = -xx * yy / (xx * xx + zz * zz)
            #     z1 = -yy * zz / (xx * xx + zz * zz)
            #     lookat_node.setAttribute("up", "%.5f" % x1 + "," + "1" + "," + "%.5f" % z1)


        if abs(x - target_x) < 0.00000001 and abs(z - target_z) < 0.00000001:
            x1 = np.cos(phi)
            z1 = -np.sin(phi)
            # lookat_node.setAttribute("up", "%.5f" % upx + "," + "0" + "," + "%.5f" % upz)
            # raise Exception("camera position and target position are the same, please check the camera position and target position")
        else:
            xx, yy, zz = target_x - x, target_y - y, target_z - z
            x1 = -xx * yy / (xx * xx + zz * zz)
            z1 = -yy * zz / (xx * xx + zz * zz)

        if self.sensor.sensor_type == "orthographic":
            # LESS3的scale和LESS的是有区别的
            scale_max = max(self.sensor.sub_region_width, self.sensor.sub_region_height)
            to_world_dict = {
                'to_world': mi.ScalarTransform4f().look_at(
                    origin=[x, y, z],
                    target=[target_x, target_y, target_z],
                    up=[x1, 1, z1]
                ) @ mi.ScalarTransform4f().scale([scale_max * 0.5, scale_max * 0.5, 1])
            }
        elif self.sensor.sensor_type == "perspective":
            to_world_dict = {
                # mi3.5
                # 'to_world': mi.ScalarTransform4f.look_at(
                #     origin=[x, y, z],
                #     target=[target_x, target_y, target_z],
                #     up=[x1, 1, z1]
                # mi3.6.4,兼容3.5
                'to_world': mi.ScalarTransform4f().look_at(
                    origin=[x, y, z],
                    target=[target_x, target_y, target_z],
                    up=[x1, 1, z1]
                )
            }

        # 测试实测数据============================================================================================
        # to_world_dict = {
        #     'to_world': mi.ScalarTransform4f.look_at(
        #         origin=[0, 3000, -1],
        #         target=[0, 0, -1],
        #         up=[0, 0, 1]
        #     ) @ mi.ScalarTransform4f.scale([12 * 0.5, 2 * 0.5, 1])
        # }
        # 测试实测数据结束============================================================================================

        return to_world_dict['to_world']

    def __get_film_config(self):
        band_value_and_band_width_inf = self.sensor.get_spectral_bands().split(",")
        band_value = [float(x.split(":")[0]) for x in band_value_and_band_width_inf]
        if band_value.index(min(band_value)) != 0 or band_value.index(max(band_value)) != len(band_value) - 1:
            raise Exception("Please arrange the bands from smallest to largest")
        bandwidth = [float(x.split(":")[1]) for x in band_value_and_band_width_inf]
        # # 是否重新考虑波宽， 如果光源考虑波宽，这里也要考虑，否则无需考虑，设置为1即可
        bandwidth = [1 for _ in band_value_and_band_width_inf]
        if len(band_value_and_band_width_inf) == 1:   # 之前的测试
            str_value_name = 'values'
        else:
            str_value_name = 'values'
        band_value[0] = band_value[0] + bandwidth[0] / 2
        band_value[len(band_value_and_band_width_inf)-1] = band_value[len(band_value_and_band_width_inf)-1] - bandwidth[-1] / 2

        # film_config = Box()

        if self.sensor.get_film_type() == "spectrum":
            film_config = {
                "type": "specfilm",
                "rfilter": {
                    "type": "box"
                },
                "width": self.sensor.get_image_width(),
                "height": self.sensor.get_image_height(),
                "component_format": "float32",  # float16, float32, or uint32

            }
            for i in range(len(band_value_and_band_width_inf)):
                film_config["band" + str(i+1)] = {
                    'type': 'regular',
                    'wavelength_min': band_value[i] - bandwidth[i] / 2,
                    'wavelength_max': band_value[i] + bandwidth[i] / 2,
                    str_value_name: '1, 1'  # maybe this can set srf
                }  # float(band_value_and_band_width_inf[i].split(":")[0])
            # Box============================================================
            # film_config.type = 'specfilm'
            # film_config.rfilter = Box()
            # film_config.rfilter.type = 'box'
            # film_config.width = self.sensor.get_image_width()
            # film_config.height = self.sensor.get_image_height()
            # film_config.component_format = "float32"
            # for i, (value, width) in enumerate(zip(band_value, bandwidth)):
            #     band_config = Box()
            #     band_config.type = 'regular'
            #     band_config.wavelength_min = value - width / 2
            #     band_config.wavelength_max = value + width / 2
            #     band_config[str_value_name] = '1, 1'  # 可能这里可以设置srf
            #     # print(band_config.values)
            #     # band_config.values = '1, 1'  # 不能band_config.values这样设置，会报错
            #     film_config[f"band{i + 1}"] = band_config


            return film_config

        # 下面的不适用于spectrum
        # film_dict = {
        #     "type": "hdrfilm",
        #     "rfilter": {
        #         "type": "box"
        #     },
        #     "width": self.sensor.get_image_width(),
        #     "height": self.sensor.get_image_height(),
        # }
        raise Exception("Sensor film type is not supported")
        # return "Sensor film type is not supported"


    def __get_sampler_config(self):
        # sampler_config = {
        #     "type": "independent",
        #     "sample_count": self.sensor.get_sample_per_pixel()
        # }
        sampler_config = {
            "type": "ldsampler",
            "sample_count": self.sensor.get_sample_per_pixel()
        }
        return sampler_config

    def __get_fov_config(self):
        import math
        if self.sensor.sensor_type == "perspective":
            # pixel_ratio = self.sensor.image_width / self.sensor.image_height
            # fov_ratio = self.sensor.fov_x / self.sensor.fov_y
            # if abs(pixel_ratio - fov_ratio) > 1e-6:
            #     raise ValueError("视场角比例与像素宽高比例不一致！"
            #                      f"像素宽高比: {pixel_ratio}, 视场角宽高比: {fov_ratio}")

            fovx = math.pi * self.sensor.fov_x / 180.0
            fovy = math.pi * self.sensor.fov_y / 180.0

            # 计算fx和fy（逆用视场角公式）
            fx = self.sensor.image_width / (2 * math.tan(fovx / 2))
            fy = self.sensor.image_height / (2 * math.tan(fovy / 2))

            # 计算绝对差异和相对差异
            abs_diff = abs(fx - fy)
            max_focal = max(fx, fy)
            rel_diff = abs_diff / max_focal if max_focal != 0 else 0

            if rel_diff > 0.05:
                raise Exception("The difference between fx and fy is too large!")

            fovDiagonal = 2 * math.atan(
                math.sqrt(math.tan(fovx * 0.5) ** 2 + math.tan(fovy * 0.5) ** 2)) / math.pi * 180
        return fovDiagonal