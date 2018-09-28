#coding: utf-8
from xml.dom import minidom
import numpy as np
from DBReader import *
from session import *
import math
from RasterHelper import *
from Atmosphere import *
from create_envmap import create_isotropic_diffuse_sky

class SceneParser:
    def __init__(self):
        self.BoundingInfomation = []

    def getCameraAltitudeHeight(self, main_scene_xml_file_prifix, pos_x, pos_z):
        currdir = os.path.split(os.path.realpath(__file__))[0]
        sys.path.append(currdir + '/bin/rt/' + current_rt_program + '/python/2.7/')
        os.environ['PATH'] = currdir + '/bin/rt/' + current_rt_program + os.pathsep + os.environ['PATH']
        import mitsuba
        from mitsuba.core import Vector, Point, Ray, Thread
        from mitsuba.render import SceneHandler
        import platform
        scenepath = session.get_scenefile_path()
        fileResolver = Thread.getThread().getFileResolver()
        logger = Thread.getThread().getLogger()
        logger.clearAppenders()
        scenepath = scenepath.encode('utf-8')
        fileResolver.appendPath(scenepath)
        filepath = os.path.join(session.get_scenefile_path(), main_scene_xml_file_prifix + terr_scene_file).encode(
            "utf-8")
        scene = SceneHandler.loadScene(fileResolver.resolve(filepath))
        scene.configure()
        scene.initialize()
        ray = Ray()
        ray.setOrigin(Point(pos_x, 999999999, pos_z))
        ray.setDirection(Vector(0, -1, 0))
        its = scene.rayIntersect(ray)
        if not its is None:
            return its.p[1]
        else:
            print("Camera is outside of the scene, do not use relative height")
            return 0

    #get boundingSphereAccording object boundbox
    def getBoundingSphereInfoStatic(self, instanceFileName, main_scene_xml_file_prifix,xScale,zScale):
        currdir = os.path.split(os.path.realpath(__file__))[0]
        sys.path.append(os.path.join(currdir,"bin","rt",current_rt_program,"python","3.6"))
        os.environ['PATH'] = os.path.join(currdir,"bin","rt",current_rt_program) + os.pathsep + os.environ['PATH']
        from mitsuba.core import AABB,Point

        # read object bounding box
        objBoundboxFilePath = os.path.join(session.get_input_dir(),obj_bounding_box_file)
        f = open(objBoundboxFilePath)
        objBoundDics = dict()
        for line in f:
            arr = line.split(":")
            objName = arr[0]
            arr = list(map(lambda x:float(x), arr[1].split()))
            aabb = AABB()
            aabb.reset()
            for i in range(0, len(arr), 6):
                minx, miny,minz,maxx,maxy,maxz = arr[i:i+6]
                subAABB = AABB(Point(minx, miny,minz), Point(maxx,maxy,maxz))
                aabb.expandBy(subAABB)
            objBoundDics[objName] = aabb
        f.close()

        totalAABB = self.getTerrainBoundingAABB(main_scene_xml_file_prifix)

        # get bounding box of the whole scene
        instanceFilePth = os.path.join(session.get_input_dir(), instanceFileName)
        f = open(instanceFilePth)
        for line in f:
            arr = line.split()
            objName = arr[0]

            x = float(arr[1])
            y = float(arr[2])
            z = float(arr[3])
            treeX = 0.5 * xScale - x
            treeZ = 0.5 * zScale - y

            insPoint = [treeX, z, treeZ]
            aabb = AABB(objBoundDics[objName])
            aabb.min = Point(insPoint[0]+aabb.min[0],insPoint[1]+aabb.min[1],insPoint[2]+aabb.min[2])
            aabb.max = Point(insPoint[0] + aabb.max[0], insPoint[1] + aabb.max[1], insPoint[2] + aabb.max[2])
            totalAABB.expandBy(aabb)

        f.close()
        bSphere = totalAABB.getBSphere()
        radius = bSphere.radius
        targetx, targety, targetz = bSphere.center[0], bSphere.center[1], bSphere.center[2]
        self.BoundingInfomation = [radius, targetx, targety, targetz, totalAABB.max.y]

    def getTerrainBoundingAABB(self, main_scene_xml_file_prifix):
        # get bounding sphere
        currdir = os.path.split(os.path.realpath(__file__))[0]
        sys.path.append(os.path.join(currdir, "bin", "rt", current_rt_program, "python", "3.6"))
        os.environ['PATH'] = os.path.join(currdir, "bin", "rt", current_rt_program) + os.pathsep + os.environ['PATH']
        import mitsuba
        from mitsuba.core import Vector, Point, Ray, Thread
        from mitsuba.render import SceneHandler
        import platform
        scenepath = session.get_scenefile_path()
        # if "Windows" in platform.system():
        #     scenepath = str(scenepath.replace('\\', '\\\\'))
        # 得到高程信息 通过光线跟踪的方法精确得到高程信息
        fileResolver = Thread.getThread().getFileResolver()
        logger = Thread.getThread().getLogger()
        logger.clearAppenders()
        scenepath = scenepath.encode('utf-8')
        fileResolver.appendPath(scenepath)
        filepath = os.path.join(session.get_scenefile_path(), main_scene_xml_file_prifix + terr_scene_file).encode("utf-8")
        scene = SceneHandler.loadScene(fileResolver.resolve(filepath))
        scene.configure()
        scene.initialize()
        return scene.getKDTree().getAABB()

    # 解析配置文件，并生成LESS能用的xml文件格式
    # 运行batch模式时，加上一个前缀main_scene_xml_file_prifix，使得生成的文件名不同
    def parse(self, config_file_path, main_scene_xml_file_prifix="", seq_name=""):
        log("INFO: Generating view and illumination.")
        f = open(config_file_path, 'r')
        cfg = json.load(f)
        f = open(combine_file_path(session.get_scenefile_path(),main_scene_xml_file_prifix+main_scene_xml_file), "w")
        doc = minidom.Document()
        rootNode = doc.createElement("scene")
        rootNode.setAttribute("version", "0.5.0")
        doc.appendChild(rootNode)

        integratorNode = doc.createElement("integrator")
        if cfg["sensor"]["sensor_type"] == "PhotonTracing":
            integratorNode.setAttribute("type", "photonrt")
            floatNode = doc.createElement("float")
            floatNode.setAttribute("name", "sunRayResolution")
            floatNode.setAttribute("value", str(cfg["sensor"]["PhotonTracing"]["sunRayResolution"]))
            integratorNode.appendChild(floatNode)

            boolNode = doc.createElement("boolean")
            integratorNode.appendChild(boolNode)
            boolNode.setAttribute("name","BRFProduct")
            boolNode.setAttribute("value","true" if cfg["sensor"]["PhotonTracing"]["BRFProduct"] else "false")

            boolNode = doc.createElement("boolean")
            integratorNode.appendChild(boolNode)
            boolNode.setAttribute("name", "UpDownProduct")
            boolNode.setAttribute("value", "true" if cfg["sensor"]["PhotonTracing"]["UpDownProduct"] else "false")

            # virtual directions virtualDirections
            if "virtualDirections" in cfg["sensor"]["PhotonTracing"]:
                virtualDirectionStr = cfg["sensor"]["PhotonTracing"]["virtualDirections"]
                if virtualDirectionStr != "":
                    strNode = doc.createElement("string")
                    integratorNode.appendChild(strNode)
                    strNode.setAttribute("name","virtualDirections")
                    strNode.setAttribute("value",virtualDirectionStr)

            # virtual detectors
            if "virtualDetectorDirections" in  cfg["sensor"]["PhotonTracing"]:
                virtualDetectorStr = cfg["sensor"]["PhotonTracing"]["virtualDetectorDirections"]
                if virtualDetectorStr != "":
                    strNode = doc.createElement("string")
                    integratorNode.appendChild(strNode)
                    strNode.setAttribute("name", "virtualDetectorDirections")
                    strNode.setAttribute("value", virtualDetectorStr)

            # Number of directions for solid patches
            if "NumberOfDirections" in cfg["sensor"]["PhotonTracing"]:
                intNode = doc.createElement("integer")
                integratorNode.appendChild(intNode)
                intNode.setAttribute("name","NumberOfDirections")
                intNode.setAttribute("value",str(cfg["sensor"]["PhotonTracing"]["NumberOfDirections"]))

        else:
            integratorNode.setAttribute("type", "path")
        rootNode.appendChild(integratorNode)

        # integrator
        # scene dimension
        xExtendNode = doc.createElement("float")
        integratorNode.appendChild(xExtendNode)
        xExtendNode.setAttribute("name", "subSceneXSize")
        xExtendNode.setAttribute("value", str(cfg["scene"]["terrain"]["extent_width"]))

        yExtendNode = doc.createElement("float")
        integratorNode.appendChild(yExtendNode)
        yExtendNode.setAttribute("name", "subSceneZSize")
        yExtendNode.setAttribute("value", str(cfg["scene"]["terrain"]["extent_height"]))

        boolNode = doc.createElement("boolean")
        integratorNode.appendChild(boolNode)
        boolNode.setAttribute("name","strictNormals")
        boolNode.setAttribute("value","true")

        integerNode = doc.createElement("integer")
        integerNode.setAttribute("name", "maxDepth")
        integerNode.setAttribute("value", str(cfg["sensor"]["record_only_direct"]))
        # if cfg["sensor"]["record_only_direct"]:
        #     integerNode.setAttribute("value", "2")
        # else:
        #     integerNode.setAttribute("value", "-1")
        integratorNode.appendChild(integerNode)
        integerNode = doc.createElement("integer")
        integerNode.setAttribute("name", "rrDepth")
        integerNode.setAttribute("value", str(cfg["Advanced"]["minimum_iteration"]))
        integratorNode.appendChild(integerNode)

        floatNode = doc.createElement("float")
        floatNode.setAttribute("name", "NoDataValue")
        floatNode.setAttribute("value", str(cfg["sensor"]["NoDataValue"]))
        integratorNode.appendChild(floatNode)

        intNode = doc.createElement("integer")
        integratorNode.appendChild(intNode)
        intNode.setAttribute("name","RepetitiveScene")
        intNode.setAttribute("value",str(cfg["sensor"]["RepetitiveScene"]))

        arrs = cfg["sensor"]["bands"].split(",")
        wavelengths = []
        for wl in arrs:
            arr = wl.split(":")
            wavelengths.append(arr[0])
        waveNode = doc.createElement("spectrum")
        integratorNode.appendChild(waveNode)
        waveNode.setAttribute("name", "wavelengths")
        waveNode.setAttribute("value", ",".join(wavelengths))

        if cfg["sensor"]["thermal_radiation"]:
            booleanNode = doc.createElement("boolean")
            integratorNode.appendChild(booleanNode)
            booleanNode.setAttribute("name", "isThermal")
            booleanNode.setAttribute("value", "true")

        if "hasFourComponentProduct" in cfg["sensor"]:
            booleanNode = doc.createElement("boolean")
            integratorNode.appendChild(booleanNode)
            booleanNode.setAttribute("name","hasFourComponentProduct")
            booleanNode.setAttribute("value","true" if cfg["sensor"]["hasFourComponentProduct"] else "false")

        if cfg["illumination"]["atmosphere"]["ats_type"] == "ATMOSPHERE":
            # generate atmosphere xml file
            generateAtsXmlNF(r"D:\DART\user_data\simulations\Hemisphere\skyView\output\atmosphereMaket.txt",
                             os.path.join(session.get_scenefile_path(), atmosphere_scene_file), 50000, 50000)
            includenode = doc.createElement("include")
            rootNode.appendChild(includenode)
            includenode.setAttribute("filename", atmosphere_scene_file)
        else:
            if os.path.exists(os.path.join(session.get_scenefile_path(), atmosphere_scene_file)):
                os.remove(os.path.join(session.get_scenefile_path(), atmosphere_scene_file))


        # <boolean name="hideEmitters" value="true"/>
        if cfg["sensor"]["film_type"] == "spectrum" and not cfg["sensor"]["thermal_radiation"] and cfg["sensor"]["sensor_type"]\
                != "CircularFisheye":
            boolNode = doc.createElement("boolean")
            integratorNode.appendChild(boolNode)
            boolNode.setAttribute("name", "hideEmitters")
            boolNode.setAttribute("value", "true")
        # virtual plane
        virtualNode = doc.createElement("boolean")
        integratorNode.appendChild(virtualNode)
        virtualNode.setAttribute("name", "SceneVirtualPlane")
        if "virtualPlane" in cfg["sensor"]:
            virtualNode.setAttribute("value", "true")

            scene_width = cfg["scene"]["terrain"]["extent_width"]
            scene_height = cfg["scene"]["terrain"]["extent_height"]

            floatNode = doc.createElement("float")
            integratorNode.appendChild(floatNode)
            floatNode.setAttribute("name", "vx")
            floatNode.setAttribute("value", str(scene_width*0.5-float(cfg["sensor"]["virtualPlane"]["vx"])))

            floatNode = doc.createElement("string")
            integratorNode.appendChild(floatNode)
            floatNode.setAttribute("name", "vy")
            floatNode.setAttribute("value", cfg["sensor"]["virtualPlane"]["vz"])

            stringNode = doc.createElement("float")
            integratorNode.appendChild(stringNode)
            stringNode.setAttribute("name", "vz")
            stringNode.setAttribute("value", str(scene_height*0.5-float(cfg["sensor"]["virtualPlane"]["vy"])))

            floatNode = doc.createElement("float")
            integratorNode.appendChild(floatNode)
            floatNode.setAttribute("name", "sizex")
            floatNode.setAttribute("value", cfg["sensor"]["virtualPlane"]["sizex"])

            floatNode = doc.createElement("float")
            integratorNode.appendChild(floatNode)
            floatNode.setAttribute("name", "sizez")
            floatNode.setAttribute("value", cfg["sensor"]["virtualPlane"]["sizey"])
        else:
            virtualNode.setAttribute("value", "false")


        # sensor
        sensor_node = doc.createElement("sensor")
        rootNode.appendChild(sensor_node)
        if cfg["sensor"]["sensor_type"] == "orthographic" or cfg["sensor"]["sensor_type"] == "PhotonTracing":
            sensor_node.setAttribute("type", "orthographic")

        if cfg["sensor"]["sensor_type"] == "perspective":
            sensor_node.setAttribute("type", "perspective")

        if cfg["sensor"]["sensor_type"] == "CircularFisheye":
            sensor_node.setAttribute("type", "hemispherical_fisheye")

        clidNode = doc.createElement("float")
        sensor_node.appendChild(clidNode)
        clidNode.setAttribute("name","nearClip")
        clidNode.setAttribute("value", "0.0000001")
        clidNode = doc.createElement("float")
        sensor_node.appendChild(clidNode)
        clidNode.setAttribute("name", "farClip")
        clidNode.setAttribute("value", "10000000000")

        trans_node = doc.createElement("transform")
        sensor_node.appendChild(trans_node)
        trans_node.setAttribute("name", "toWorld")

        # orthographic 才需要设置scale
        x,y,z,target_x,target_y,target_z, phi = 0, 0, 0, 0, 0, 0, 0
        if cfg["sensor"]["sensor_type"] == "orthographic" or cfg["sensor"]["sensor_type"] == "PhotonTracing":


            scale_node = doc.createElement("scale")
            trans_node.appendChild(scale_node)

            region_width = cfg["sensor"]["orthographic"]["sub_region_width"]/float(2)
            region_height = cfg["sensor"]["orthographic"]["sub_region_height"]/float(2)

            theta = float(cfg["observation"]["obs_zenith"]) / 180.0 * np.pi
            phi_degree = float(cfg["observation"]["obs_azimuth"])
            phi = -(phi_degree - 90) / 180.0 * np.pi

            if "virtualPlane" in cfg["sensor"]:

                if len(self.BoundingInfomation) == 0:
                    self.getBoundingSphereInfoStatic(cfg["scene"]["forest"]["tree_pos_file"],
                                                     main_scene_xml_file_prifix,cfg["scene"]["terrain"]["extent_width"],
                                                     cfg["scene"]["terrain"]["extent_height"])

                rx = float(cfg["sensor"]["virtualPlane"]["sizex"])*0.5
                ry = float(cfg["sensor"]["virtualPlane"]["sizey"])*0.5
                r = math.sqrt(rx*rx+ry*ry)
                region_x, region_y = r, r

                scene_width = cfg["scene"]["terrain"]["extent_width"]
                scene_height = cfg["scene"]["terrain"]["extent_height"]

                target_x = scene_width * 0.5 - float(cfg["sensor"]["virtualPlane"]["vx"])
                target_y = self.BoundingInfomation[4]
                target_z = scene_height * 0.5 - float(cfg["sensor"]["virtualPlane"]["vy"])

            else:
                if cfg["sensor"]["orthographic"]["cover_whole_scene"]:
                    # 计算场景的最小包围球
                    if len(self.BoundingInfomation) == 0:
                        self.getBoundingSphereInfoStatic(cfg["scene"]["forest"]["tree_pos_file"],main_scene_xml_file_prifix,
                                                         cfg["scene"]["terrain"]["extent_width"],
                                                     cfg["scene"]["terrain"]["extent_height"])
                    if theta == 0 and (phi_degree == 0 or phi_degree == 90 or
                                           phi_degree == 180 or phi_degree == 270):
                        region_x = region_width
                        region_y = region_height
                    else:
                        region_x = self.BoundingInfomation[0]
                        region_y = self.BoundingInfomation[0]

                        target_x = self.BoundingInfomation[1]
                        target_y = self.BoundingInfomation[2]
                        target_z = self.BoundingInfomation[3]
                else:
                    region_x = region_width
                    region_y = region_height


            scale_node.setAttribute("x", str(region_x))
            scale_node.setAttribute("y", str(region_y))

            floatNode = doc.createElement("float")
            sensor_node.appendChild(floatNode)
            floatNode.setAttribute("name", "aspect")
            floatNode.setAttribute("value", str(region_x / region_y))

            x = -cfg["observation"]["obs_R"] * np.sin(theta) * np.cos(phi) + target_x
            z = cfg["observation"]["obs_R"] * np.sin(theta) * np.sin(phi) + target_z
            y = cfg["observation"]["obs_R"] * np.cos(theta) + target_y


        # perspective 设置视场角
        if cfg["sensor"]["sensor_type"] == "perspective":
            floatnode = doc.createElement("float")
            floatnode.setAttribute("name","fov")
            fovx = math.pi*cfg["sensor"]["perspective"]["fovx"]/180.0
            fovy = math.pi*cfg["sensor"]["perspective"]["fovy"]/180.0
            fovDiagonal = 2*math.atan(math.sqrt(math.tan(fovx*0.5)**2+math.tan(fovy*0.5)**2))/math.pi*180
            floatnode.setAttribute("value", str(fovDiagonal))
            sensor_node.appendChild(floatnode)
            strNode = doc.createElement("string")
            strNode.setAttribute("name","fovAxis")
            strNode.setAttribute("value","diagonal")
            sensor_node.appendChild(strNode)
            floatNode = doc.createElement("float")
            sensor_node.appendChild(floatNode)
            floatNode.setAttribute("name","aspect")
            floatNode.setAttribute("value", str(fovx/fovy))

            scene_width = cfg["scene"]["terrain"]["extent_width"]
            scene_height = cfg["scene"]["terrain"]["extent_height"]

            x = scene_width * 0.5 - cfg["observation"]["obs_o_x"]
            z = scene_height*0.5 - cfg["observation"]["obs_o_y"]
            y = cfg["observation"]["obs_o_z"]
            target_x = scene_width * 0.5 - cfg["observation"]["obs_t_x"]
            target_y = cfg["observation"]["obs_t_z"]
            target_z =  scene_height*0.5 - cfg["observation"]["obs_t_y"]
            if cfg["observation"]["relative_height"]:
                y += self.getCameraAltitudeHeight(main_scene_xml_file_prifix, x, z)
                target_y += self.getCameraAltitudeHeight(main_scene_xml_file_prifix, x, z)
            phi = -(180 - 90) / 180.0 * np.pi

        if cfg["sensor"]["sensor_type"] == "CircularFisheye":
            floatnode = doc.createElement("float")
            floatnode.setAttribute("name", "angular_fov")
            floatnode.setAttribute("value", str(cfg["sensor"]["CircularFisheye"]["angular_fov"]))
            sensor_node.appendChild(floatnode)

            strNode = doc.createElement("string")
            strNode.setAttribute("name", "projection_type")
            strNode.setAttribute("value", cfg["sensor"]["CircularFisheye"]["projection_type"])
            sensor_node.appendChild(strNode)

            rotate_node = doc.createElement("rotate")
            rotate_node.setAttribute("x","1")
            rotate_node.setAttribute("angle","90")
            trans_node.appendChild(rotate_node)

            scene_width = cfg["scene"]["terrain"]["extent_width"]
            scene_height = cfg["scene"]["terrain"]["extent_height"]

            x = scene_width * 0.5 - cfg["observation"]["obs_o_x"]
            z = scene_height * 0.5 - cfg["observation"]["obs_o_y"]
            y = cfg["observation"]["obs_o_z"]
            target_x = scene_width * 0.5 - cfg["observation"]["obs_t_x"]
            target_y = cfg["observation"]["obs_t_z"]
            target_z = scene_height * 0.5 - cfg["observation"]["obs_t_y"]
            if cfg["observation"]["relative_height"]:
                y += self.getCameraAltitudeHeight(main_scene_xml_file_prifix, x, z)
                target_y += self.getCameraAltitudeHeight(main_scene_xml_file_prifix, x, z)
            phi = -(180 - 90) / 180.0 * np.pi



        lookat_node = doc.createElement("lookat")
        trans_node.appendChild(lookat_node)
        lookat_node.setAttribute("origin", str(x) + "," + str(y) + "," + str(z))
        lookat_node.setAttribute("target", str(target_x) + "," + str(target_y) + "," + str(target_z))
        if abs(x-target_x) < 0.00000001 and abs(z-target_z) < 0.00000001:
            upx = np.cos(phi)
            upz = -np.sin(phi)
            lookat_node.setAttribute("up", "%.5f" % upx + "," + "0" + "," + "%.5f" % upz)
        else:
            xx,yy,zz = target_x- x, target_y - y, target_z - z
            x1 = -xx * yy / (xx * xx + zz * zz)
            z1 = -yy * zz / (xx * xx + zz * zz)
            lookat_node.setAttribute("up", "%.5f" % x1 + "," + "1" + "," + "%.5f" % z1)



        sampler_node = doc.createElement("sampler")
        sensor_node.appendChild(sampler_node)
        sampler_node.setAttribute("type","halton")
        i_node = doc.createElement("integer")
        sampler_node.appendChild(i_node)
        i_node.setAttribute("name", "sampleCount")
        # 将每平米的采样数，转换成每个像元
        if cfg["sensor"]["sensor_type"] == "orthographic" or cfg["sensor"]["sensor_type"] == "PhotonTracing":
            # convert from samples per square meter to per pixels
            # that is to determine the pixels size.
            # total samples
            total_samples = cfg["sensor"]["orthographic"]["sample_per_square_meter"] * \
            cfg["sensor"]["orthographic"]["sub_region_width"] * cfg["sensor"]["orthographic"]["sub_region_height"]
            # per pixel samples
            per_pixel = int(math.ceil(total_samples / float(cfg["sensor"]["image_width"] * cfg["sensor"]["image_height"])))
            i_node.setAttribute("value", str(per_pixel))

        if cfg["sensor"]["sensor_type"] == "perspective":
            #首先计算perspective覆盖的范围
            i_node.setAttribute("value", str(cfg["sensor"]["perspective"]["sample_per_square_meter"]))

        if cfg["sensor"]["sensor_type"] == "CircularFisheye":
            #首先计算perspective覆盖的范围
            i_node.setAttribute("value", str(cfg["sensor"]["CircularFisheye"]["sample_per_square_meter"]))


        film_node = doc.createElement("film")
        sensor_node.appendChild(film_node)
        if cfg["sensor"]["film_type"] == "rgb" or cfg["sensor"]["film_type"] == "RGB":
            film_node.setAttribute("type", "ldrfilm")
            bool_node = doc.createElement("boolean")
            film_node.appendChild(bool_node)
            bool_node.setAttribute("name", "banner")
            bool_node.setAttribute("value", "false")
            float_node = doc.createElement("float")
            film_node.appendChild(float_node)
            float_node.setAttribute("name", "exposure")
            float_node.setAttribute("value", "2")
            rfilterNode = doc.createElement("rfilter")
            film_node.appendChild(rfilterNode)
            rfilterNode.setAttribute("type", "lanczos")
            integerNode = doc.createElement("integer")
            rfilterNode.appendChild(integerNode)
            integerNode.setAttribute("name", "lobes")
            integerNode.setAttribute("value", "2")
        if cfg["sensor"]["film_type"] == "spectrum":
            film_node.setAttribute("type", "mfilm")
            strNode = doc.createElement("string")
            film_node.appendChild(strNode)
            strNode.setAttribute("name", "fileFormat")
            strNode.setAttribute("value", "numpy")
            strNode = doc.createElement("string")
            film_node.appendChild(strNode)
            strNode.setAttribute("name", "pixelFormat")
            strNode.setAttribute("value", "spectrum")
            rfilterNode = doc.createElement("rfilter")
            film_node.appendChild(rfilterNode)
            rfilterNode.setAttribute("type", "box")
            floatNode = doc.createElement("float")
            rfilterNode.appendChild(floatNode)
            floatNode.setAttribute("name","radius")
            floatNode.setAttribute("value", "0.4")



        i_node = doc.createElement("integer")
        film_node.appendChild(i_node)
        i_node.setAttribute("name", "width")
        i_node.setAttribute("value", str(cfg["sensor"]["image_width"]))
        i_node = doc.createElement("integer")
        film_node.appendChild(i_node)
        i_node.setAttribute("name", "height")
        i_node.setAttribute("value", str(cfg["sensor"]["image_height"]))

        if cfg["illumination"]["atmosphere"]["ats_type"] == "ATMOSPHERE":
            refNode = doc.createElement("ref")
            sensor_node.appendChild(refNode)
            refNode.setAttribute("id","ats_medium")

        #emitters
        #direct
        # For thermal radiation, no need to consider the sun radiation
        if not cfg["sensor"]["thermal_radiation"]:
            d_e_node = doc.createElement("emitter")
            rootNode.appendChild(d_e_node)
            if cfg["sensor"]["sensor_type"] == "PhotonTracing":
                d_e_node.setAttribute("type", "directional")
            else:
                d_e_node.setAttribute("type","directional")
            v_node = doc.createElement("vector")
            d_e_node.appendChild(v_node)
            v_node.setAttribute("name","direction")
            theta = float(cfg["illumination"]["sun"]["sun_zenith"])/180.0*np.pi
            phi = (float(cfg["illumination"]["sun"]["sun_azimuth"])-90)/180.0*np.pi
            x = np.sin(theta)*np.cos(phi)
            z = np.sin(theta) * np.sin(phi)
            y = -np.cos(theta)
            v_node.setAttribute("x", str(x))
            v_node.setAttribute("y", str(y))
            v_node.setAttribute("z", str(z))


        #sky radiance according to planck
        if cfg["sensor"]["thermal_radiation"]:
            from Utils import emittion_spectral
            sky_e_node = doc.createElement("emitter")
            rootNode.appendChild(sky_e_node)
            sky_e_node.setAttribute("type", "hemisphere")
            spectrum_node = doc.createElement("spectrum")
            sky_e_node.appendChild(spectrum_node)
            spectrum_node.setAttribute("name", "radiance")
            skyTemperStr = cfg["scene"]["temperature_properties"][cfg["illumination"]["atmosphere"]["AtsTemperature"]]
            skyarr = skyTemperStr.split(":")
            emit_spectral = emittion_spectral(
                    float(skyarr[0]), cfg["sensor"]["bands"])

            spectrum_node.setAttribute("value", emit_spectral)

        # write BOA to output  batch模式下，每个运行单元的irradiance可能不同，需要分别计算
        # fi = open(combine_file_path(session.get_output_dir(), main_scene_xml_file_prifix+irradiance_file), 'w')
        irr_str = "" #返回一个字符串，包含了太阳水平下行辐射和天空光辐射
        if (not cfg["sensor"]["thermal_radiation"])\
                and (cfg["illumination"]["atmosphere"]["ats_type"] == "SKY_TO_TOTAL"
                     or cfg["illumination"]["atmosphere"]["ats_type"] == "ATMOSPHERE"):
            spectrum_node = doc.createElement("spectrum")
            d_e_node.appendChild(spectrum_node)
            spectrum_node.setAttribute("name", "irradiance")
            bands = cfg["sensor"]["bands"].split(",")
            bandnum = len(bands)
            if cfg["illumination"]["atmosphere"]["ats_type"] == "ATMOSPHERE":
                SKYL = ','.join(['0' for i in range(bandnum)])
            else:
                SKYL = cfg["illumination"]["atmosphere"]["percentage"]

            skyls = list(map(lambda x:float(x), SKYL.split(",")))
            if (not "sun_spectrum" in cfg["illumination"]["sun"])  and (not "sky_spectrum" in cfg["illumination"]["atmosphere"]):
                sun_irr, sky_irr = sun_irradiance_db.read_toa_with_bandwidth_SKYLs( cfg["sensor"]["bands"],skyls)
                sky_irr = list(map(lambda x:x*math.cos(theta),sky_irr))
            else:
                sun_irr = list(map(lambda x:float(x), cfg["illumination"]["sun"]["sun_spectrum"].split(",")))
                sky_irr = list(map(lambda x: float(x), cfg["illumination"]["atmosphere"]["sky_spectrum"].split(",")))

            # write sun
            tmp = list(map(lambda x:str(x),sun_irr))
            spectrum_node.setAttribute("value", ','.join(tmp))

            irr_str = "BOA_SUN "
            for i in range(0, len(sun_irr)):
                irr_str += str(sun_irr[i] * math.cos(theta)) + " "
            # fi.write(irr_str + "\n")
            # write sky
            if any(x > 0 for x in sky_irr):
                # create_isotropic_diffuse_sky(map(lambda x1: x1/math.pi,
                #                                  sky_irr),
                #                              combine_file_path(session.get_scenefile_path(), main_scene_xml_file_prifix+"ats.exr"),len(sun_irr))
                # sky_e_node = doc.createElement("emitter")
                # rootNode.appendChild(sky_e_node)
                # sky_e_node.setAttribute("type", "envmap")
                # strNode = doc.createElement("string")
                # sky_e_node.appendChild(strNode)
                # strNode.setAttribute("name", "filename")
                # strNode.setAttribute("value", main_scene_xml_file_prifix+"ats.exr")

                # creating sky using hemisphere
                sky_e_node = doc.createElement("emitter")
                rootNode.appendChild(sky_e_node)
                sky_e_node.setAttribute("type", "hemisphere")
                spectrum_node = doc.createElement("spectrum")
                sky_e_node.appendChild(spectrum_node)
                spectrum_node.setAttribute("name", "radiance")
                tmp = list(map(lambda x: str(x/math.pi), sky_irr))
                spectrum_node.setAttribute("value", ','.join(tmp))

                # sampling weight
                sampleRatio = max(list(map(lambda x, y: x/float(x+y), sun_irr, sky_irr)))
                floatNode = doc.createElement("float")
                d_e_node.appendChild(floatNode)
                floatNode.setAttribute("name", "samplingWeight")
                floatNode.setAttribute("value", str(sampleRatio))

                floatNode = doc.createElement("float")
                sky_e_node.appendChild(floatNode)
                floatNode.setAttribute("name", "samplingWeight")
                floatNode.setAttribute("value", str(1-sampleRatio))

                irr_str += "\nBOA_SKY "
                for i in range(0, len(sky_irr)):
                    irr_str += str(sky_irr[i]) + " "
                # fi.write(irr_str)


        #include terrain and forest
        if cfg["scene"]["terrain"]["terr_file"] == "" and \
                        cfg["scene"]["terrain"]["terrain_type"] != "PLANE":
            log("Terrain: DEM file is not set.")
        else:
            includenode = doc.createElement("include")
            rootNode.appendChild(includenode)
            includenode.setAttribute("filename", main_scene_xml_file_prifix+terr_scene_file)

        tree_pos = combine_file_path(session.get_input_dir(),cfg["scene"]["forest"]["tree_pos_file"])

        if cfg["scene"]["forest"]["tree_pos_file"] != "" and os.path.exists(tree_pos):
            objfile_path = combine_file_path(session.get_scenefile_path(), seq_name+object_scene_file)
            if os.path.exists(objfile_path):
                includenode = doc.createElement("include")
                rootNode.appendChild(includenode)
                includenode.setAttribute("filename", seq_name+object_scene_file)

            forest_list = getFileList(session.get_scenefile_path(), seq_name+forest_scene_file)
            for forest in forest_list:
                includenode = doc.createElement("include")
                rootNode.appendChild(includenode)
                includenode.setAttribute("filename", forest)

        if cfg["scene"]["extra_scene"] != "":
            includenode = doc.createElement("include")
            rootNode.appendChild(includenode)
            includenode.setAttribute("filename", cfg["scene"]["extra_scene"])



        xm = doc.toprettyxml()
        xm = xm.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="utf-8"?>')
        f.write(xm)
        f.close()
        if main_scene_xml_file_prifix == "":
            log("INFO: View and illumination generated.")
        return irr_str


    # some utility functions
    def write_irr_to_file(self, irrstr):
        fi = open(combine_file_path(session.get_output_dir(),irradiance_file), 'w')
        fi.write("W/m2/nm\n")
        fi.write(irrstr)
        fi.close()

if __name__ == "__main__":
    pass
    # SceneParser.parse(session.getState("current_sim")+"/input/input.conf")