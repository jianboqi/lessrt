# coding: utf-8
import sys
from SimulationHelper import SimulationHelper
from Simulation import Simulation
from Observation import ObservationOrthographic
from OpticalProperty import OpticalItem
from SceneObjects import SceneObject
import random

sim_helper = SimulationHelper(r"D:\LESS")  # 新建SimulationHelper,参数为LESS的安装根目录
sim_helper.create_new_sim(r"D:\LESS\simulations\test_auto_create")  # 新建模拟工程
sim = Simulation(r"D:\LESS\simulations\test_auto_create", sim_helper)  # 初始化Simulation对象
sim.read_sim_project()  # 读取模拟工程的内容

# get scene components
scene = sim.get_scene()  # 得到Scene
landscape = scene.get_landscape()  # 得到LandScape对象
sensor = scene.get_sensor()  # 得到Sensor

# clear previous objects
landscape.scene_objects.objects.clear()  # 清除工程已有的场景元素（重复运行程序时，必须执行）
landscape.scene_objects.instances.clear()

# define scene
# 定义一个光学属性（正面反射；背面反射；透射）
op_item = OpticalItem("op_leaves", "0.05,0.4;0.05,0.4;0.05,0.4")
landscape.add_op_item(op_item)  # 添加到场景库

landscape.terrain.optical = "op_leaves"

scene_obj = SceneObject("tree1")  # 定义一个场景物体，名叫tree1
# 添加一个obj文件作为tree1的一个组分
scene_obj.add_component_from_file(r"lm_10.obj", "op_leaves")
scene_obj.add_component_from_file(r"ww_10.obj", "op_leaves")
landscape.add_object(scene_obj)

# 随机放置在场景中
for i in range(1000):
    x = 10+random.random()*80
    y = 10+random.random()*80
    landscape.place_object("tree1", x=x, y=y)

# This is needed when using LESS GUI to open the created project
landscape.scene_objects.calculate_object_bounding_box()

# 设置相机参数
sensor.film_type = "rgb"
sensor.image_width = 300
sensor.image_height = 300
sensor.sample_per_pixel = 10
# 新建一个Observation，然后设置到场景中，也可以直接读取，再修改
obs = ObservationOrthographic()
scene.set_observation(obs)
sim.save_sim_project()
sim.start()  # 开始模拟
