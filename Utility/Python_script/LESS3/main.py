# coding: utf-8
from LESS3Simulation import LESS3Simulation
from SimulationHelper import SimulationHelper
from Simulation import Simulation
import os
from PostProcessing import PostProcessing


if __name__ == '__main__':
    sim_dir = r"D:\LESS\LESS_2025\LESS_one_band_test"
    sim_helper = SimulationHelper(r"D:\LESS\LESS_2025\LESS")  # Create SimulationHelper，the parameter is the LESS installation folder
    sim_helper.create_new_sim(sim_dir)  # Create a new simulation
    sim = Simulation(sim_dir, sim_helper)  # initialize the simulation
    sim.read_sim_project()  # read the initialized simulation
    # set up the output file name
    sim.set_dist_file(os.path.join(sim.get_sim_dir(), "Results", "output_radiance_file"))
    # sim.start()
    scene = sim.get_scene()  # Get the scene object
    illu = scene.get_illumination()
    # scene.set_illumination(illu)
    illu.set_ats_percentage("0.0,0.0")
    sim.get_scene_helper().get_script_less_py_path()
    illu.set_sun_spectrum("1,2")
    illu.set_sky_spectrum("2,3")
    terr_obj = scene.get_landscape().get_terrain()
    terr_obj.set_terr_brdf_type(Terrain.TERRAIN_BRDF_TYPE.ART)
    terr_obj.artParams = {"snow_particle_size":100, "snow_pollution_content":1}
    terr_obj.rpvParams = {"rho0":"0.075", "k":"0.55", "THETA": "-0.25", "rhoc":"0.075"}
    sim.save_sim_project()  # save the project
    sim.start()
    PostProcessing.radiance2brf(sim.get_sim_dir(), sim.get_dist_file(), sim.get_dist_file() + "_BRF")
    # using the LESS3 object, which support the differentiable modeling
    less3sim = LESS3Simulation(sim)
    less3sim.start()




