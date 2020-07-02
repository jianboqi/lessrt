#coding: utf-8

#通过光线跟踪方法，计算每棵树所对应的高程，为3D现实而使用.

import platform
from SceneParser import *
from Loger import log
from Utils import convert_obj_2_serialized, check_if_string_is_zero_and_comma
currdir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(currdir + '/bin/rt/' + current_rt_program + '/python/2.7/')
os.environ['PATH'] = currdir + '/bin/rt/' + current_rt_program + '/' + os.pathsep + os.environ['PATH']


class threeDView:
    @staticmethod
    def forest_generate_according_tree_pos_file_for3d(config_file_path):
        import mitsuba
        from mitsuba.core import Vector, Point, Ray, Thread
        from mitsuba.render import SceneHandler
        from mitsuba.render import RenderQueue, RenderJob
        from mitsuba.render import Scene
        from mitsuba.render import Intersection

        f = open(config_file_path, 'r')
        cfg = json.load(f)
        tree_pos = combine_file_path(session.get_input_dir(), cfg["scene"]["forest"]["tree_pos_file"])
        if cfg["scene"]["forest"]["tree_pos_file"] == "" or (not os.path.exists(tree_pos)):
            return

        # 读取地形数据 计算每个树的高程
        if cfg["scene"]["terrain"]["terrain_type"] != "PLANE" and cfg["scene"]["terrain"]["terrain_type"] == "RASTER":
            demfile = combine_file_path(session.get_input_dir(), cfg["scene"]["terrain"]["terr_file"])
            img_w, img_h, dem_arr = RasterHelper.read_dem_as_array(demfile)
            dem_arr = dem_arr - dem_arr.min()

        scenepath = session.get_scenefile_path()
        if "Windows" in platform.system():
            scenepath = str(scenepath.replace('\\', '\\\\'))
        # 得到高程信息 通过光线跟踪的方法精确得到高程信息
        fileResolver = Thread.getThread().getFileResolver()
        logger = Thread.getThread().getLogger()
        logger.clearAppenders()
        fileResolver.appendPath(scenepath)
        # 由于batch模式不会改变地形几何结构，因此在用地形打点计算树木的高程时，用第一个terrain文件即可，所以加上了_0_

        scene = SceneHandler.loadScene(fileResolver.resolve(str(terr_scene_file)))
        scene.configure()
        scene.initialize()
        tf = open(tree_pos)

        objectPosFile = open(os.path.join(session.get_input_dir(),"object_pos_3dView.txt"),'w')

        # 创建一个虚拟根节点，最后再删除
        for line in tf:
            arr = line.replace("\n", "").split(" ")
            objectName = arr[0]
            x = float(arr[1])
            y = float(arr[2])
            xScale = cfg["scene"]["terrain"]["extent_width"]
            zScale = cfg["scene"]["terrain"]["extent_height"]
            treeX = 0.5 * xScale - x
            treeZ = 0.5 * zScale - y
            if cfg["scene"]["terrain"]["terrain_type"] != "PLANE":
                ray = Ray()
                ray.setOrigin(Point(treeX, 9999, treeZ))
                ray.setDirection(Vector(0, -1, 0))
                its = scene.rayIntersect(ray)
                if not its is None:
                    linestr = objectName + " "+str(treeX) + " " +str(its.p[1]) + " " + str(treeZ) + "\n"
                else:
                    # log("warning: precise height not found.")
                    if cfg["scene"]["terrain"]["terrain_type"] == "RASTER":
                        im_r = int((y / float(zScale)) * img_h)
                        im_c = int((x / float(xScale)) * img_w)
                        if im_r >= img_h:
                            im_r = img_h - 1
                        if im_c >= img_w:
                            im_c = img_w - 1
                        linestr = objectName + " "+str(treeX) + " " + str(dem_arr[im_r][im_c]) + " " + str(treeZ) + "\n"
                    else:
                        linestr = objectName + " "+str(treeX) + " " + str(0) + " " + str(treeZ) + "\n"
            else:
                linestr = objectName + " "+str(treeX) + " " + str(0) + " " + str(treeZ) + "\n"
            objectPosFile.write(linestr)
        objectPosFile.close()