# coding: utf-8
# change optical property of a component
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Observation import ObservationOrthographic
from OpticalProperty import OpticalItem
from SceneObjects import SceneObject
import random

sim_helper = SimulationHelper(r"D:\LESS")  # 新建SimulationHelper,参数为LESS的安装根目录
sim_helper.create_new_sim(r"D:\LESS\simulations\TESTS\test_change_op")  # 新建模拟工程
sim = Simulation(r"D:\LESS\simulations\TESTS\test_change_op", sim_helper)  # 初始化Simulation对象
sim.read_sim_project()  # 读取模拟工程的内容

# get scene components
scene = sim.get_scene()  # 得到Scene
landscape = scene.get_landscape()  # 得到LandScape对象
sensor = scene.get_sensor()  # 得到Sensor

# define scene
# 定义一个光学属性（正面反射；背面反射；透射）
op_item = OpticalItem("op_leaves2", "0.05,0.4;0.05,0.4;0.05,0.4")
landscape.add_op_item(op_item)  # 添加到场景库


# landscape.get_scene_objects().objects["tree1"]["tree1_leaves.obj"]["op_name"] = "op_leaves"
landscape.get_scene_objects().get_object("tree1").set_component_op("tree1_leaves.obj", "op_leaves2")

sim.save_sim_project()
sim.start()  # 开始模拟
