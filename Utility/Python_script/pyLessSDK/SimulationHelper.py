# coding: utf-8
import os
import shutil
import platform


class SimulationHelper(object):
    def __init__(self, less_install_root_path):
        self.less_install_root_path = less_install_root_path

    def get_less_py_dir(self):
        __lesspy_dir = os.path.join(self.less_install_root_path, "app", "bin", "scripts", "Lesspy") \
            if platform.system() == "Windows" else ""
        return __lesspy_dir

    def get_py_interpreter_path(self):
        __py_interpreter_path = os.path.join(self.less_install_root_path, "app", "bin", "python", "python.exe") \
            if platform.system() == "Windows" else ""
        return __py_interpreter_path

    def get_script_less_py_path(self):
        return os.path.join(self.get_less_py_dir(), "less.py")

    def get_default_config_file(self):
        return os.path.join(self.get_less_py_dir(), "default.conf")

    def create_new_sim(self, new_sim_path):
        if not os.path.exists(new_sim_path):
            os.makedirs(new_sim_path)
        dirs = os.listdir(new_sim_path)
        if len(dirs) == 0:
            cwd = os.getcwd()
            os.chdir(new_sim_path)
            interpreter = self.get_py_interpreter_path()
            script_lesspy_path = self.get_script_less_py_path()
            os.system(interpreter + " " + script_lesspy_path + " -n")
            shutil.copy(self.get_default_config_file(), os.path.join(new_sim_path, "Parameters", "input.conf"))
            os.chdir(cwd)
        else:
            print("Warning: The simulation directory is not empty, skip creating")
