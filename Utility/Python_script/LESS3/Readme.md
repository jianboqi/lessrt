## How to use LESS3
#### This document does not guide you in configuring the environment
#### You need NVIDIA GPU for this project.

step1: You can look at the main.py file.


    sim_dir = r"D:\LESS\LESS_project\scene\scene\HLS"
    sim_helper = SimulationHelper(r"D:/LESS/LESS-2.1.7-11-22/LESS")  # Create SimulationHelper with LESS installation root directory as the parameter
    sim = Simulation(sim_dir, sim_helper)  # Simulation
    sim.read_sim_project()
    sim.save_sim_project()
    less3sim = LESS3Simulation(sim)
    less3sim.start()  # start simulation
    diff_render_config = DiffRenderConfig()
    diff_render_config.result_dir_path = os.path.join(sim.get_sim_dir(), "Results", "per_optimize_result")  # result dir path
    diff_render_config.ref_brf_image_path = less3sim.get_scene().brf_image_path  # config the ref brf image path
    diff_render_config.is_open_comparison_between_opt_and_origin = True
    diff_render_config.optimize_spp = 1024  # if you want to be faster, you can set spp to 64, but the performance may be lower
    diff_render_config.init_epoch = 0
    diff_render_config.stop_epoch = 200
    diff_render_config.optimize_params = ["birch_leaf_green", "dark_soil_mollisol"]  # choose the params, the params are same as the optical database of LESS and be loaded in to the scene

    less3sim.start_diff_spectrum(diff_render_config)


step2: Change the "sim_dir" and the "sim_helper" to your own "sim_dir" and "sim_helper".
Choose the "optimize_params" you want to invert.

step3: Run the main.py file.

step4: You can find the result in the "result_dir_path".

step5: You can look the "optimize_params_199.xlsx" and "origin_params.xlsx" 
to see the result of inversion. Pay attention to the parameters to be inverted in the scene