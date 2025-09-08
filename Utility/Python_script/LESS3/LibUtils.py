# coding: utf-8
import os
import sys
from Utils import Utils


def init_mitsuba_path():
    curr_dir = os.path.split(os.path.realpath(__file__))[0]
    __sim_mode = "devel"
    if curr_dir.startswith(r"D:\My_program\LESS_program") or curr_dir.startswith(r"E:\03-Coding\lessrt"):
        __sim_mode = "devel"
    else:
        __sim_mode = "prod"

    if __sim_mode == "devel":
        lessrt_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        pyd_dir = os.path.join(lessrt_dir, "Utility", "Python_script", "LESS3", "LESSRTCore3")
    else:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        pyd_dir = os.path.join(root_dir, "Python_script", "LESS3", "LESSRTCore3")
    if os.path.exists(pyd_dir):
        sys.path.append(pyd_dir)
        import mitsuba as mi
        # print(mi.variants())
        # mi.set_variant("scalar_spectral_double")
        if Utils.is_nvidia_gpu_present():
            mi.set_variant("cuda_spectral")
        else:
            mi.set_variant("scalar_spectral")
        return True
    else:
        raise Exception("can not find LESSRTCore3")
        return False




init_mitsuba_path()
