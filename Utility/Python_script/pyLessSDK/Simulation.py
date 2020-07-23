# coding: utf-8
import os
import sys
import json
from Scene import Scene
from Landscape import Landscape
from Sensor import SensorBasic, SensorOrthographic, SensorPhotonTracing, SensorPerspective, SensorFisheye
from Illumination import Illumination
from Observation import ObservationOrthographic, ObservationPerspective, ObservationFisheye
from AdvancedParams import AdvancedParams
from SimulationHelper import SimulationHelper


class Simulation(object):
    def __init__(self, sim_dir, simulation_helper):
        self.__sim_dir = sim_dir
        self.__sim_helper = simulation_helper
        self.__scene = Scene()
        self.dist_file = ""

        # calculated members
        self.__input_conf_path = os.path.join(sim_dir, "Parameters", "input.conf")
        f = open(self.__input_conf_path)
        self.__input_conf = json.load(f)
        f.close()

    def get_dist_file(self):
        return self.dist_file

    def set_dist_file(self, dist_file):
        self.dist_file = dist_file

    def __read_sensor_from_json(self):
        sensor_type = self.__input_conf["sensor"]["sensor_type"]
        sensor = SensorBasic()
        if sensor_type == "orthographic":
            sensor = SensorOrthographic()
            sensor.init_sensor_from_json(self.__input_conf)
        if sensor_type == "PhotonTracing":
            sensor = SensorPhotonTracing()
            sensor.init_sensor_from_json(self.__input_conf)
        if sensor_type == "perspective":
            sensor = SensorPerspective()
            sensor.init_sensor_from_json(self.__input_conf)
        if sensor_type == "CircularFisheye":
            sensor = SensorFisheye()
            sensor.init_sensor_from_json(self.__input_conf)
        sensor.set_sim(self)
        return sensor

    def __read_observation_from_json(self):
        sensor_type = self.__input_conf["sensor"]["sensor_type"]
        if sensor_type == "orthographic":
            observation = ObservationOrthographic()
            observation.init_obs_from_json(self.__input_conf)
            return observation
        if sensor_type == "PhotonTracing":  # This is actually not used
            observation = ObservationOrthographic()
            observation.init_obs_from_json(self.__input_conf)
            return observation
        if sensor_type == "perspective":
            observation = ObservationPerspective()
            observation.init_obs_from_json(self.__input_conf)
            return observation
        if sensor_type == "CircularFisheye":
            observation = ObservationPerspective()
            observation.init_obs_from_json(self.__input_conf)
            return observation

    def get_scene(self):
        return self.__scene

    def get_sim_dir(self):
        return self.__sim_dir

    def is_sim_valid(self):
        if os.path.exists(os.path.join(self.__sim_dir, ".less")):
            return True
        else:
            return False

    def read_sim_project(self):
        if not self.is_sim_valid():
            print("Simulation project: "+self.__sim_dir+" is not a valid project.")
            sys.exit(0)
        # Sensor
        self.__scene.set_sensor(self.__read_sensor_from_json())

        # Landscape
        landscape = Landscape()
        landscape.set_sim(self)
        landscape.init_landscape_from_json(self.__input_conf)

        self.__scene.set_landscape(landscape)

        # Illumination
        illumination = Illumination()
        illumination.set_sim(self)
        illumination.init_illumination_from_json(self.__input_conf)
        self.__scene.set_illumination(illumination)

        # Observation
        self.__scene.set_observation(self.__read_observation_from_json())

        # Advanced parameters
        advanced_params = AdvancedParams()
        advanced_params.init_advanced_params_from_json(self.__input_conf)
        self.__scene.set_advanced_params(advanced_params)

    def save_sim_project(self):
        f_out = open(self.__input_conf_path, "w")
        json.dump(self.__scene.to_json_object(self), f_out, indent=2)
        f_out.close()

    def start(self):
        cwd = os.getcwd()
        os.chdir(self.__sim_dir)
        interpreter = self.__sim_helper.get_py_interpreter_path()
        script_lesspy_path = self.__sim_helper.get_script_less_py_path()
        os.system(interpreter + " " + script_lesspy_path + " -g s")
        os.system(interpreter + " " + script_lesspy_path + " -g v")
        if self.dist_file == "":
            os.system(interpreter + " " + script_lesspy_path + " -r n -p " +
                      str(self.get_scene().get_advanced_params().number_of_cores))
        else:
            os.system(interpreter + " " + script_lesspy_path + " -r n -p " +
                      str(self.get_scene().get_advanced_params().number_of_cores) + " -d " + self.dist_file)
        os.chdir(cwd)


if __name__ == "__main__":
    sim_helper = SimulationHelper(r"D:\LESS")
    sim_helper.create_new_sim(r"D:\LESS\simulations\test_auto_create")
    sim = Simulation(r"D:\LESS\simulations\test_auto_create", sim_helper)
    sim.read_sim_project()
    # Change parameters
    sim.get_scene().get_sensor().film_type = "rgb"
    for i in [0, 30, 50, 60]:
        # obs = ObservationOrthographic()
        # obs.obs_zenith = i
        # sim.get_scene().set_observation(obs)
        obs = ObservationFisheye()
        obs.obs_o_z = 50
        sim.get_scene().set_observation(obs)
        sim.save_sim_project()
        sim.start()
