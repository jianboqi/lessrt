# coding: utf-8
import os
import sys
from LibUtils import *
from Simulation import Simulation
from LESS3Scene import LESS3Scene


class LESS3Simulation(object):
    def __init__(self, less_sim: Simulation):
        self.less_sim = less_sim
        self.__less3scene = LESS3Scene(self.less_sim.get_scene())

    def start(self):
        # less3scene = LESS3Scene(self.less_sim.get_scene())
        self.__less3scene.render()
        pass

    def start_diff_spectrum(self, diff_render_config):
        # less3scene = LESS3Scene(self.less_sim.get_scene())
        self.__less3scene.render_diff_spectrum(diff_render_config)

    def get_scene(self):
        return self.__less3scene


    # def start_diff_spectrum_multi_angle(self, diff_render_config):
    #     less3scene = LESS3Scene(self.less_sim.get_scene())
    #     less3scene.render_diff_spectrum_multi_angle(diff_render_config)

    # def get_scene_xml(self):
    #     # 用于测试
    #     less3scene = LESS3Scene(self.less_sim.get_scene())
    #     less3scene.dict_to_xml()
    #     # less3scene.__print_dict()
    #

    def __check_diff_render_config(self, diff_render_config):
        if diff_render_config is None:
            raise Exception("diff_render_config is None")
        # 待完善====
        pass

    def get_scene_dict(self):
        # 用于测试
        less3scene = LESS3Scene(self.less_sim.get_scene())
        return less3scene.get_dict()

    def _start_dict_test(self, dict):
        # 用于测试
        less3scene = LESS3Scene(self.less_sim.get_scene())
        less3scene.render(n_dict=dict)

    def start_xml_test(self, xml_path):
        # 用于测试
        less3scene = LESS3Scene(self.less_sim.get_scene())
        less3scene.render(xml_file=xml_path)