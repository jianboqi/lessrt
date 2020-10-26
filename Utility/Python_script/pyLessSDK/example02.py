# coding: utf-8
# Author: Jianbo Qi
# Date: 2020/7/6
# example02: this exmample code shows how to change spectra of terrain for batch processing
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Observation import ObservationOrthographic
from OpticalProperty import OpticalItem
from SceneObjects import SceneObject
import Terrain
import os
from PostProcessing import PostProcessing

sim_dir = r"D:\LESS\simulations\TESTS\test_auto_create"
sim_helper = SimulationHelper(r"D:\LESS")  # 新建SimulationHelper,参数为LESS的安装根目录
sim_helper.create_new_sim(sim_dir)  # 新建模拟工程
sim = Simulation(sim_dir, sim_helper)  # 初始化Simulation对象
sim.read_sim_project()  # 读取模拟工程的内容

# get scene components
scene = sim.get_scene()  # 得到Scene
landscape = scene.get_landscape()  # 得到LandScape对象

# # 定义一个光学属性（正面反射；背面反射；透射）
# op_item = OpticalItem("op_terrain", "0.2,0.4;0.0,0.0;0.0,0.0")
# landscape.add_op_item(op_item)  # 添加到场景库
# for i in range(0, 10):
#     op_item = landscape.get_op_item("op_terrain")
#     op_item.set_op_value("0.25,0.45;0.0,0.0;0.0,0.0")
#     sim.set_dist_file(os.path.join(r"D:\LESS\simulations\TESTS\test_auto_create\Results", "dist_op_"+str(i)))
#     brf_dist_file = sim.dist_file + "_BRF"
#     sim.save_sim_project()
#     sim.start()  # 开始模拟
#     PostProcessing.radiance2brf(sim.get_sim_dir(), sim.dist_file, brf_dist_file)

landscape.get_terrain().set_terr_brdf_type(Terrain.BRDF_TYPE.LAND_ALBEDO_MAP)
for i in range(0, 5):
    # landalbedomap 是envi标准格式文件，每个波段对应LESS模拟的一个波段，
    # landalbedomap每个像素的值就是对应的像素的反射率，比如场景是100m*100m，landalbedomap像素为200*200
    # 那么，最终场景每0.5m*0.5m范围内就有一个不同的反射率
    # 每个循环可以换成不同的反射率影像，这个影像可以通过gdal等库动态生成
    landscape.get_terrain().set_landalbedo_file(r"D:\LESS\simulations\Dataset\landalbedomap")
    # 模拟的输出文件
    sim_dist_file = os.path.join(sim_dir, "Results", "dist_file"+str(i))
    sim.set_dist_file(sim_dist_file)
    # BRF文件
    sim_dist_file_brf = sim_dist_file + "_BRF"
    sim.save_sim_project()
    sim.start()  # 开始模拟
    # 将模拟的辐亮度影像转换为反射率影像
    PostProcessing.radiance2brf(sim.get_sim_dir(), sim_dist_file, sim_dist_file_brf)