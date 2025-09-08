# coding: utf-8
import sys

from Utils import Utils
from Illumination import Illumination
import mitsuba as mi



class LESS3Illumination(object):
    def __init__(self, less_illumination: Illumination):
        self.less_illumination = less_illumination
        self.sun_irr, self.sky_irr = self.__get_spectrum()

    def get_sun_dict(self):
        # cwd = os.getcwd()
        # script_lesspy_path = self.less_illumination.get_sim().get_scene_helper.get_script_less_py_path()  # get_scene_helper  self.__sim_helper.get_script_less_py_path()
        # sun_irr, sky_irr = self.__get_spectrum()
        band_value_and_band_width_inf = self.less_illumination.get_sim().get_scene().get_sensor().get_spectral_bands().split(",")
        band_value = [float(x.split(":")[0]) for x in band_value_and_band_width_inf]
        bandwidth = [float(x.split(":")[1]) for x in band_value_and_band_width_inf]
        sun_irr = self.sun_irr
        if len(self.sun_irr) == 1:
            sun_irr = self.sun_irr[0][1]
        emitter_dict = {
            'type': 'directional',
            'direction': Utils.spherical_to_xyz_coords(self.less_illumination.sun_zenith,
                                                       self.less_illumination.sun_azimuth),
            'irradiance': {
                'type': 'spectrum',
                'value': sun_irr  # 这里就是value
                # # 下面这样设置是考虑了波段宽度，不过波宽在最先开始已经经过积分了，如果这里设置的话，可能计算上会引入误差（虽然误差不大），注意这里和传感器的波宽要么同时设置，要么都不设置。
                # 'type': 'irregular',
                # 'wavelengths': f"{sun_irr[0][0]}, {sun_irr[0][0]+10}, {sun_irr[1][0]-10}, {sun_irr[1][0]}",
                # "values": f"{sun_irr[0][1]/10}, {sun_irr[0][1]/10}, {sun_irr[1][1]/10}, {sun_irr[1][1]/10}"  #
            }
        }
        return emitter_dict

    def get_sky_dict(self):
        import numpy as np
        import math
        sky_radiance = []
        cos_zenith = math.cos(self.less_illumination.sun_zenith / 180.0 * np.pi)
        for i in range(len(self.sky_irr)):
            sky_radiance.append((self.sky_irr[i][0], self.sky_irr[i][1] * cos_zenith / np.pi))

        if len(self.sky_irr) == 1:
            sky_radiance = sky_radiance[0][1]
        emitter_dict = {
            'type': 'constant',
            'radiance': {
                'type': 'spectrum',
                'value': sky_radiance  # 这里就是value
            }
        }
        # emitter_dict = {
        #     'type': 'constant',
        #     'radiance': {
        #         'type': 'irregular',
        #         'wavelengths': '450.0,560.0,650.0,730.0,840.0',
        #         'values': '0.0486,0.1535,0.2280,0.2860,0.3339'
        #     }
        # }
        return emitter_dict

    # def __get_sky_radiance(self):
    #     import numpy as np
    #     sky_radiance = []
    #     for i in range(len(self.sky_irr)):
    #         sky_radiance.append((self.sky_irr[i][0], self.sky_irr[i][1] / np.pi))
    #     return sky_radiance

    def __get_spectrum(self):
        sun_irr = []  # [(600.0, 1.0), (900.0, 2.0)]
        sky_irr = []  # [(600.0, 2.0), (900.0, 3.0)]
        spectral_bands = list(map(lambda x: float(x.split(":")[0]),
                                  self.less_illumination.get_sim().get_scene().get_sensor().get_spectral_bands().split(",")))
        # If user sun and sky spectral are provided
        if self.less_illumination.get_sun_spectrum() != "" and self.less_illumination.get_sky_spectrum() != "":
            sun_irr = list(map(lambda x, y: (y, float(x)), self.less_illumination.get_sun_spectrum().split(","), spectral_bands))
            sky_irr = list(map(lambda x, y: (y, float(x), ), self.less_illumination.get_sky_spectrum().split(","), spectral_bands))
        elif self.less_illumination.get_ats_type() == "SKY_TO_TOTAL":
            # 思考一下加sun的辐照度的理解
            script_lesspy_path = self.less_illumination.get_sim().get_scene_helper().get_less_py_dir()
            sys.path.append(script_lesspy_path)
            from DBReader import sun_irradiance_db
            sky_percentage_list = list(map(lambda x: float(x), self.less_illumination.get_ats_percentage().split(",")))
            sun_irr, sky_irr = sun_irradiance_db.read_toa_with_bandwidth_SKYLs(self.less_illumination.get_sim().get_scene().get_sensor().get_spectral_bands(),
                                                                               sky_percentage_list, hasFluor=False)

            # if all(abs(x) > 1e-9 for x in sky_irr):
            #     # tolerance = 1e-9
            #     raise Exception("sky_percentage is not supported for this running")

            sun_irr = list(
                map(lambda x, y: (y, float(x)), sun_irr, spectral_bands))
            sky_irr = list(
                map(lambda x, y: (y, float(x)), sky_irr, spectral_bands))

            pass

        return sun_irr, sky_irr