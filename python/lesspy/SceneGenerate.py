#coding: utf-8
#根据输入，生成场景

import platform
from SceneParser import *
from Loger import log
from Utils import convert_obj_2_serialized, check_if_string_is_zero_and_comma, ensureDirs
currdir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(currdir + '/bin/rt/' + current_rt_program + '/python/3.6/')
os.environ['PATH'] = currdir + '/bin/rt/' + current_rt_program + '/' + os.pathsep + os.environ['PATH']
import codecs

class SceneGenerate:

    @staticmethod
    def write_range_num_for_RT(config_file_path):
        f = open(config_file_path, 'r')
        cfg = json.load(f)
        #band num
        SKYLs = cfg["sensor"]["bands"].split(",")
        bandnum = len(SKYLs)

        # write band number information to dist
        currdir = os.path.split(os.path.realpath(__file__))[0]
        numCFGpath = os.path.join(currdir, "bin", "rt", current_rt_program, ".less")
        ensureDirs(numCFGpath)
        numCFGpath = os.path.join(numCFGpath, "num.cfg")
        cfgFile = open(numCFGpath, 'w')
        cfgFile.write(str(bandnum))
        cfgFile.close()

        rangePath = os.path.join(currdir, "bin", "rt", current_rt_program, ".less")
        ensureDirs(rangePath)
        rangePath = os.path.join(rangePath, "range.cfg")
        cfgFile = open(rangePath, 'w')
        cfgFile.write(LESS_BAND_START + " " + LESS_BAND_END)
        cfgFile.close()

        # write num.cfg and range.cfg to .less/
        curr_dir = os.getcwd()
        lessfolder = os.path.join(curr_dir, ".less")
        ensureDirs(lessfolder)
        numCFGpath = os.path.join(lessfolder, "num.cfg")
        cfgFile = open(numCFGpath, 'w')
        cfgFile.write(str(bandnum))
        cfgFile.close()
        rangePath = os.path.join(lessfolder, "range.cfg")
        cfgFile = open(rangePath, 'w')
        cfgFile.write(LESS_BAND_START + " " + LESS_BAND_END)
        cfgFile.close()

    @staticmethod
    def terr_generate(config_file_path, terrain_file_prifix=""):
        log("INFO: Generating terrain...")
        f = open(config_file_path, 'r')
        cfg = json.load(f)

        if cfg["scene"]["terrain"]["terr_file"] == "" and\
                        cfg["scene"]["terrain"]["terrain_type"] != "PLANE":
            return

        f = open(combine_file_path(session.get_scenefile_path(),terrain_file_prifix + terr_scene_file), "w")
        doc = minidom.Document()

        root = doc.createElement("scene")
        doc.appendChild(root)
        root.setAttribute("version", "0.5.0")

        demNode = doc.createElement("shape")
        root.appendChild(demNode)
        demNode.setAttribute("id","terrain")
        if cfg["scene"]["terrain"]["terrain_type"] == "RASTER":
            demNode.setAttribute("type", "heightfield")
            boolNode = doc.createElement("boolean")
            demNode.appendChild(boolNode)
            boolNode.setAttribute("name", "shadingNormals")
            boolNode.setAttribute("value", "false")
            # textureNode = doc.createElement("texture")
            # demNode.appendChild(textureNode)
            # textureNode.setAttribute("type", "bitmap")
            strNode = doc.createElement("string")
            demNode.appendChild(strNode)
            # textureNode.appendChild(strNode)
            strNode.setAttribute("name","filename")
            exr_file_path = combine_file_path(session.get_scenefile_path(),cfg["scene"]["terrain"]["terr_file"]+".exr")
            RasterHelper.convert_dem_to_mip_monochromatic_chanel(combine_file_path(session.get_input_dir(),\
                                                              cfg["scene"]["terrain"]["terr_file"]), exr_file_path)
            strNode.setAttribute("value", cfg["scene"]["terrain"]["terr_file"]+".exr")
            # floatNode = doc.createElement("float")
            # demNode.appendChild(floatNode)
            # floatNode.setAttribute("name", "scale")
            # floatNode.setAttribute("value", "1.4")
            transNode = doc.createElement("transform")
            demNode.appendChild(transNode)
            transNode.setAttribute("name", "toWorld")
            rotateNode = doc.createElement("rotate")
            transNode.appendChild(rotateNode)
            rotateNode.setAttribute("angle", "-90")
            rotateNode.setAttribute("x" ,"1")
            scaleNode = doc.createElement("scale")
            transNode.appendChild(scaleNode)
            scaleNode.setAttribute("x", str(cfg["scene"]["terrain"]["extent_width"]/2.0))
            scaleNode.setAttribute("z", str(cfg["scene"]["terrain"]["extent_height"]/2.0))

        if cfg["scene"]["terrain"]["terrain_type"] == "MESH":

            demNode.setAttribute("type", "obj")
            strNode = doc.createElement("string")
            demNode.appendChild(strNode)
            strNode.setAttribute("name","filename")
            strNode.setAttribute("value", cfg["scene"]["terrain"]["terr_file"])
            # raster_file = combine_file_path(session.get_input_dir(), cfg["scene"]["terrain"]["terr_file"])
            # meshfile = combine_file_path(session.get_scenefile_path(), cfg["scene"]["terrain"]["terr_file"]+".obj")
            # RasterHelper.Raster2Ojb(raster_file, meshfile)
            facenormalNode = doc.createElement("boolean")
            demNode.appendChild(facenormalNode)
            facenormalNode.setAttribute("name","faceNormals")
            facenormalNode.setAttribute("value","true")

        if cfg["scene"]["terrain"]["terrain_type"] == "PLANE":

            demNode.setAttribute("type", "rectangle")
            transNode = doc.createElement("transform")
            demNode.appendChild(transNode)
            transNode.setAttribute("name", "toWorld")
            rotateNode = doc.createElement("rotate")
            transNode.appendChild(rotateNode)
            rotateNode.setAttribute("angle", "-90")
            rotateNode.setAttribute("x", "1")
            scaleNode = doc.createElement("scale")
            transNode.appendChild(scaleNode)
            scaleNode.setAttribute("x", str(cfg["scene"]["terrain"]["extent_width"] / 2.0))
            scaleNode.setAttribute("z", str(cfg["scene"]["terrain"]["extent_height"] / 2.0))
        bsdf = doc.createElement("bsdf")
        demNode.appendChild(bsdf)
        if cfg["scene"]["terrain"]["terrBRDFType"] == "Soilspect":
            bsdf.setAttribute("type","soilspect")
        elif cfg["scene"]["terrain"]["terrBRDFType"] == "Lambertian":
            bsdf.setAttribute("type", "diffuse")

        # for thermal
        if cfg["sensor"]["thermal_radiation"]:
            emitter_node = doc.createElement("emitter")
            demNode.appendChild(emitter_node)
            emitter_node.setAttribute("type", "planck")
            tNode = doc.createElement("float")
            emitter_node.appendChild(tNode)
            tNode.setAttribute("name","temperature")
            terrTempStr = cfg["scene"]["temperature_properties"][cfg["scene"]["terrain"]["temperature"]]
            terrArr = terrTempStr.split(":")
            tNode.setAttribute("value",terrArr[0])
            tNode = doc.createElement("float")
            emitter_node.appendChild(tNode)
            tNode.setAttribute("name", "deltaTemperature")
            tNode.setAttribute("value", terrArr[1])
            arrs = cfg["sensor"]["bands"].split(",")
            wavelengths = []
            for wl in arrs:
                arr = wl.split(":")
                wavelengths.append(arr[0])
            waveNode = doc.createElement("spectrum")
            emitter_node.appendChild(waveNode)
            waveNode.setAttribute("name","wavelengths")
            waveNode.setAttribute("value",",".join(wavelengths))
            ft = open(os.path.join(session.get_output_dir(),wavelength_file_for_thermal),'w')
            ft.write(",".join(wavelengths))
            ft.close()

            v_node = doc.createElement("vector")
            emitter_node.appendChild(v_node)
            v_node.setAttribute("name", "direction")
            theta = float(cfg["illumination"]["sun"]["sun_zenith"]) / 180.0 * np.pi
            phi = (float(cfg["illumination"]["sun"]["sun_azimuth"]) - 90) / 180.0 * np.pi
            x = np.sin(theta) * np.cos(phi)
            z = np.sin(theta) * np.sin(phi)
            y = -np.cos(theta)
            v_node.setAttribute("x", str(x))
            v_node.setAttribute("y", str(y))
            v_node.setAttribute("z", str(z))

            # from Utils import emittion_spectral
            # spectrumNode = doc.createElement("spectrum")
            # emitter_node.appendChild(spectrumNode)
            # spectrumNode.setAttribute("name","radiance")
            # emit_spectral = emittion_spectral(float(cfg["scene"]["temperature_properties"][cfg["scene"]["terrain"]["temperature"]]),
            #                         cfg["sensor"]["bands"])
            # spectrumNode.setAttribute("value",emit_spectral)


        if "landcover" not in cfg["scene"]["terrain"]:
            if cfg["scene"]["terrain"]["terrBRDFType"] == "Lambertian":
                reflectancenode = doc.createElement("spectrum")
                bsdf.appendChild(reflectancenode)
                reflectancenode.setAttribute("name", "reflectance")
                factor = cfg["scene"]["terrain"]["optical_scale"]
                defined_optical_name = cfg["scene"]["terrain"]["optical"]
                optical_name_or_list = cfg["scene"]["optical_properties"][defined_optical_name]
                if optical_name_or_list == "":
                    log("No optical property of ground detected.")
                    sys.exit(0)
                reflectancenode.setAttribute("value", optical_name_or_list.split(";")[0])
            elif cfg["scene"]["terrain"]["terrBRDFType"] == "Soilspect":
                spec  = doc.createElement("spectrum")
                bsdf.appendChild(spec)
                spec.setAttribute("name", "albedo")
                spec.setAttribute("value", cfg["scene"]["terrain"]["soilSpectParams"]["albedo"])
                spec = doc.createElement("spectrum")
                bsdf.appendChild(spec)
                spec.setAttribute("name", "c1")
                spec.setAttribute("value", cfg["scene"]["terrain"]["soilSpectParams"]["c1"])
                spec = doc.createElement("spectrum")
                bsdf.appendChild(spec)
                spec.setAttribute("name", "c2")
                spec.setAttribute("value", cfg["scene"]["terrain"]["soilSpectParams"]["c2"])
                spec = doc.createElement("spectrum")
                bsdf.appendChild(spec)
                spec.setAttribute("name", "c3")
                spec.setAttribute("value", cfg["scene"]["terrain"]["soilSpectParams"]["c3"])
                spec = doc.createElement("spectrum")
                bsdf.appendChild(spec)
                spec.setAttribute("name", "c4")
                spec.setAttribute("value", cfg["scene"]["terrain"]["soilSpectParams"]["c4"])
                spec = doc.createElement("spectrum")
                bsdf.appendChild(spec)
                spec.setAttribute("name", "h1")
                spec.setAttribute("value", cfg["scene"]["terrain"]["soilSpectParams"]["h1"])
                spec = doc.createElement("spectrum")
                bsdf.appendChild(spec)
                spec.setAttribute("name", "h2")
                spec.setAttribute("value", cfg["scene"]["terrain"]["soilSpectParams"]["h2"])
        else:
            textureNode = doc.createElement("texture")
            bsdf.appendChild(textureNode)
            textureNode.setAttribute("type", "bitmap")
            textureNode.setAttribute("name","reflectance")
            strNode = doc.createElement("string")
            textureNode.appendChild(strNode)
            strNode.setAttribute("name","filename")
            strNode.setAttribute("value","landcover.exr")
            boolNode = doc.createElement("boolean")
            textureNode.appendChild(boolNode)
            boolNode.setAttribute("name","cache")
            boolNode.setAttribute("value","false")
            from create_envmap import createLandcoverMap, createLandcoverMap_trans
            log("INFO: Creating land cover map...")
            createLandcoverMap(os.path.join(session.get_input_dir(),imported_landcover_raster_name),
                               os.path.join(session.get_scenefile_path(), "landcover.exr"),
                               os.path.join(session.get_input_dir(), "landcover.txt"),
                               cfg["scene"]["optical_properties"],
                               len(cfg["sensor"]["bands"].split(",")))
            # createLandcoverMap_trans(os.path.join(session.get_input_dir(), imported_landcover_raster_name),
            #                    os.path.join(session.get_scenefile_path(), "landtrans.exr"),
            #                    os.path.join(session.get_input_dir(), "landcover.txt"),
            #                    cfg["scene"]["optical_properties"],
            #                    len(cfg["sensor"]["bands"].split(",")))



        xm = doc.toprettyxml()
        # xm = xm.replace('<?xml version="1.0" ?>', '')
        f.write(xm)
        f.close()
        if terrain_file_prifix  == "":
            log("INFO: Terrain generated.")

    # return the generated file list this function only generate the positions of trees
    @staticmethod
    def forest_generate(config_file_path, forest_prifix=""):
        f = open(config_file_path, 'r')
        cfg = json.load(f)
        tree_pos = combine_file_path(session.get_input_dir(),cfg["scene"]["forest"]["tree_pos_file"])
        if cfg["scene"]["forest"]["tree_pos_file"] == "" or (not os.path.exists(tree_pos)):
            print("INFO: No tree positions defined.")
            return

        #total line
        totalline = -1
        f = open(tree_pos,'r')
        for line in f:
            totalline += 1
        num = int(totalline/NUM_EACH_FOREST_FILE)
        filelist = ""
        for i in range(0,num+1):
            forest_file_name = forest_prifix + forest_scene_file + "_" + str(i) + ".xml"
            filelist += forest_file_name + ","
            linestart = i*NUM_EACH_FOREST_FILE
            lineend = min((i+1)*NUM_EACH_FOREST_FILE,totalline)
            SceneGenerate.forest_generate_according_tree_pos_file(config_file_path,forest_file_name, \
                    linestart,lineend,forest_prifix)

    @staticmethod
    def get_hidded_objects():
        hidden_obj_file_path = os.path.join(session.get_input_dir(), hide_objects_file)
        f = open(hidden_obj_file_path)
        hidden_objects = []
        for line in f:
            hidden_objects.append(line.replace("\n", ""))
        return hidden_objects


    #generate objects file: objects.xml
    @staticmethod
    def generate_objects_file(config_file_path, obj_file_prifix=""):
        f = open(config_file_path, 'r')
        cfg = json.load(f)
        objects_file_path = combine_file_path(session.get_input_dir(), cfg["scene"]["forest"]["objects_file"])
        if cfg["scene"]["forest"]["objects_file"] == "" or (not os.path.exists(objects_file_path)):
            log("INFO: No objects defined.")
            return

        # objf = open(os.path.join(session.get_scenefile_path(), obj_file_prifix + object_scene_file), 'w')
        objf = codecs.open(os.path.join(session.get_scenefile_path(), obj_file_prifix + object_scene_file), "w", "utf-8-sig")
        objdoc = minidom.Document()
        objroot = objdoc.createElement("scene")
        objdoc.appendChild(objroot)
        objroot.setAttribute("version", "0.5.0")

        hidden_objects = SceneGenerate.get_hidded_objects()

        tf = open(objects_file_path)
        opticalSet = set()
        object_optical = []
        for line in tf:
            if line != "":
                arr = line.replace("\n", "").split(" ")
                object_name = arr[0]
                if object_name not in hidden_objects:
                    object_optical.append(arr)
                    for i in range(1, len(arr),4):
                        opticalSet.add(arr[i+1]) # add all spectral properties to set

        opticalSet = list(opticalSet)
        for i in range(0, len(opticalSet)):
            defined_op = cfg["scene"]["optical_properties"][opticalSet[i]]
            arr = defined_op.split(";")
            if len(arr) != 3:
                log("Error while setting optical properties.")
            if check_if_string_is_zero_and_comma(arr[1]) and check_if_string_is_zero_and_comma(arr[2]):
                # oneside
                bsdf = objdoc.createElement("bsdf")
                bsdf.setAttribute("id", opticalSet[i])
                objroot.appendChild(bsdf)
                bsdf.setAttribute("type", "diffuse")
                specnode = objdoc.createElement("spectrum")
                bsdf.appendChild(specnode)
                specnode.setAttribute("name", "reflectance")
                specnode.setAttribute("value", arr[0])
            else:
                # twoside
                bsdfnode = objdoc.createElement("bsdf")
                objroot.appendChild(bsdfnode)
                bsdfnode.setAttribute("id", opticalSet[i])
                bsdfnode.setAttribute("type", "mixturebsdf")
                bnode = objdoc.createElement("boolean")
                bsdfnode.appendChild(bnode)
                bnode.setAttribute("name", "ensureEnergyConservation")
                bnode.setAttribute("value", "false")
                strnode = objdoc.createElement("string")
                bsdfnode.appendChild(strnode)
                strnode.setAttribute("name", "weights")
                strnode.setAttribute("value", "1,1")
                twobsdf = objdoc.createElement("bsdf")
                bsdfnode.appendChild(twobsdf)
                twobsdf.setAttribute("type", "twosided")
                diffbsdf = objdoc.createElement("bsdf")
                twobsdf.appendChild(diffbsdf)
                diffbsdf.setAttribute("type", "diffuse")
                specnode = objdoc.createElement("spectrum")
                diffbsdf.appendChild(specnode)
                specnode.setAttribute("name", "reflectance")
                specnode.setAttribute("value", arr[0])
                diffbsdf = objdoc.createElement("bsdf")
                twobsdf.appendChild(diffbsdf)
                diffbsdf.setAttribute("type", "diffuse")
                specnode = objdoc.createElement("spectrum")
                diffbsdf.appendChild(specnode)
                specnode.setAttribute("name", "reflectance")
                specnode.setAttribute("value", arr[1])

                transnode = objdoc.createElement("bsdf")
                bsdfnode.appendChild(transnode)
                transnode.setAttribute("type", "difftrans")
                specnode = objdoc.createElement("spectrum")
                transnode.appendChild(specnode)
                specnode.setAttribute("name", "transmittance")
                specnode.setAttribute("value", arr[2])
        for i in range(0, len(object_optical)):
            rowdata = object_optical[i]
            objectName = rowdata[0]
            #创建group
            shapenode = objdoc.createElement("shape")
            objroot.appendChild(shapenode)
            shapenode.setAttribute("id", objectName)
            shapenode.setAttribute("type", "shapegroup")

            for j in range(1, len(rowdata),4):
                compnentName = rowdata[j]
                opticalName = rowdata[j+1]
                temperatureName = rowdata[j+2]
                subshapnode = objdoc.createElement("shape")
                shapenode.appendChild(subshapnode)
                subshapnode.setAttribute("type", "serialized")
                strnode = objdoc.createElement("string")
                subshapnode.appendChild(strnode)
                strnode.setAttribute("name", "filename")
                # import chardet
                # convert to serizlized
                # the string reading from object.txt, which is produced by Java, is in gbk encoding
                # objfile = os.path.join(session.get_input_dir(), compnentName.encode("gbk").decode("utf-8"))
                objfile = os.path.join(session.get_input_dir(), compnentName)
                convert_obj_2_serialized(objfile, session.get_scenefile_path())
                strnode.setAttribute("value", os.path.splitext(compnentName)[0] + ".serialized")
                refnode = objdoc.createElement("ref")
                subshapnode.appendChild(refnode)
                refnode.setAttribute("id", opticalName)
                # using face normal
                boolNode = objdoc.createElement("boolean")
                subshapnode.appendChild(boolNode)
                boolNode.setAttribute("name", "faceNormals")
                boolNode.setAttribute("value", "true")

                # for thermal
                if cfg["sensor"]["thermal_radiation"]:
                    emitter_node = objdoc.createElement("emitter")
                    subshapnode.appendChild(emitter_node)
                    emitter_node.setAttribute("type", "planck")
                    tNode = objdoc.createElement("float")
                    emitter_node.appendChild(tNode)
                    tNode.setAttribute("name", "temperature")
                    tmperatureStr = cfg["scene"]["temperature_properties"][temperatureName]
                    tmparr = tmperatureStr.split(":")
                    tNode.setAttribute("value", tmparr[0])
                    tNode = objdoc.createElement("float")
                    emitter_node.appendChild(tNode)
                    tNode.setAttribute("name", "deltaTemperature")
                    tNode.setAttribute("value", tmparr[1])
                    arrs = cfg["sensor"]["bands"].split(",")
                    wavelengths = []
                    for wl in arrs:
                        arr = wl.split(":")
                        wavelengths.append(arr[0])
                    waveNode = objdoc.createElement("spectrum")
                    emitter_node.appendChild(waveNode)
                    waveNode.setAttribute("name", "wavelengths")
                    waveNode.setAttribute("value", ",".join(wavelengths))

                    v_node = objdoc.createElement("vector")
                    emitter_node.appendChild(v_node)
                    v_node.setAttribute("name", "direction")
                    theta = float(cfg["illumination"]["sun"]["sun_zenith"]) / 180.0 * np.pi
                    phi = (float(cfg["illumination"]["sun"]["sun_azimuth"]) - 90) / 180.0 * np.pi
                    x = np.sin(theta) * np.cos(phi)
                    z = np.sin(theta) * np.sin(phi)
                    y = -np.cos(theta)
                    v_node.setAttribute("x", str(x))
                    v_node.setAttribute("y", str(y))
                    v_node.setAttribute("z", str(z))


                    # from Utils import emittion_spectral
                    # emitter_node = objdoc.createElement("emitter")
                    # subshapnode.appendChild(emitter_node)
                    # emitter_node.setAttribute("type", "area")
                    # spectrumNode = objdoc.createElement("spectrum")
                    # emitter_node.appendChild(spectrumNode)
                    # spectrumNode.setAttribute("name", "radiance")
                    # emit_spectral = emittion_spectral(
                    #     float(cfg["scene"]["temperature_properties"][temperatureName]),
                    #     cfg["sensor"]["bands"])
                    # spectrumNode.setAttribute("value", emit_spectral)
        xm = objdoc.toprettyxml()
        # xm = xm.replace('<?xml version="1.0" ?>', '')
        objf.write(xm)
        objf.close()


    @staticmethod
    def forest_generate_according_tree_pos_file(config_file_path,forest_file_name, linestart, lineend,forest_prifix=""):
        import mitsuba
        from mitsuba.core import Vector, Point, Ray, Thread
        from mitsuba.render import SceneHandler
        from mitsuba.render import RenderQueue, RenderJob
        from mitsuba.render import Scene
        from mitsuba.render import Intersection


        f = open(config_file_path, 'r')
        cfg = json.load(f)
        tree_pos = combine_file_path(session.get_input_dir(),cfg["scene"]["forest"]["tree_pos_file"])
        if cfg["scene"]["forest"]["tree_pos_file"] == "" or (not os.path.exists(tree_pos)):
            return
        # 保存场景中树的位置 forest*.xml
        # f = open(os.path.join(session.get_scenefile_path(),forest_file_name),'w')
        f = codecs.open(os.path.join(session.get_scenefile_path(),forest_file_name), "w", "utf-8-sig")
        doc = minidom.Document()
        root = doc.createElement("scene")
        doc.appendChild(root)
        root.setAttribute("version", "0.5.0")

        #读取地形数据 计算每个树的高程
        if cfg["scene"]["terrain"]["terrain_type"] != "PLANE" and cfg["scene"]["terrain"]["terrain_type"] == "RASTER":
            demfile = combine_file_path(session.get_input_dir(),cfg["scene"]["terrain"]["terr_file"])
            img_w, img_h, dem_arr = RasterHelper.read_dem_as_array(demfile)
            dem_arr = dem_arr-dem_arr.min()

        #读取object boundingbox 数据
        fobj = open(os.path.join(session.get_input_dir(),obj_bounding_box_file))
        bound_dict = dict()
        for line in fobj:
            arr = line.split(":")
            objName = arr[0]
            arr = list(map(lambda x:float(x), arr[1].split(" ")))
            bound_dict[objName] = [arr[3]-arr[0],arr[4]-arr[1],arr[5]-arr[2]]

        scenepath = session.get_scenefile_path()
        # if "Windows" in platform.system():
        #     scenepath = str(scenepath.replace('\\', '\\\\'))
        #得到高程信息 通过光线跟踪的方法精确得到高程信息
        fileResolver = Thread.getThread().getFileResolver()
        logger = Thread.getThread().getLogger()
        logger.clearAppenders()
        fileResolver.appendPath(str(scenepath))
        # 由于batch模式不会改变地形几何结构，因此在用地形打点计算树木的高程时，用第一个terrain文件即可，所以加上了_0_
        if(forest_prifix != ""):
            forest_prifix = forest_prifix[0:len(forest_prifix)-1] +"_0_"
        scene = SceneHandler.loadScene(fileResolver.resolve(str(forest_prifix+terr_scene_file)))
        # scene = SceneHandler.loadScene(fileResolver.resolve(r"E:\Research\20-LESS\RealScene\SimProj\calLAI\Parameters\_scenefile\terrain1.xml"))
        scene.configure()
        scene.initialize()
        tf = open(tree_pos)

        hidden_objects = SceneGenerate.get_hidded_objects()

        #创建一个虚拟根节点，最后再删除
        treeIdx = 0
        for line in tf:
            if treeIdx >= linestart and treeIdx <= lineend:
                arr = line.replace("\n", "").strip().split(" ")
                objectName = arr[0]
                if objectName in hidden_objects:
                    continue

                shapenode = doc.createElement("shape")
                root.appendChild(shapenode)
                shapenode.setAttribute("type", "instance")
                refnode = doc.createElement("ref")
                shapenode.appendChild(refnode)
                refnode.setAttribute("id", objectName)
                trnode = doc.createElement("transform")
                shapenode.appendChild(trnode)
                trnode.setAttribute("name", "toWorld")
                if len(arr) == 6: # fit with
                    scale_node = doc.createElement("scale")
                    trnode.appendChild(scale_node)
                    scale_node.setAttribute("x", str(float(arr[4]) / bound_dict[objectName][0]))
                    scale_node.setAttribute("z", str(float(arr[4]) / bound_dict[objectName][0]))
                    scale_node.setAttribute("y", str(float(arr[5]) / bound_dict[objectName][1]))

                if len(arr) == 5: # for roatation of the tree
                    angle = arr[len(arr)-1]
                    rotatenode = doc.createElement("rotate")
                    trnode.appendChild(rotatenode)
                    rotatenode.setAttribute("y", '1')
                    rotatenode.setAttribute("angle", angle)
                translatenode = doc.createElement("translate")
                trnode.appendChild(translatenode)
                x = float(arr[1])
                y = float(arr[2])
                z = float(arr[3])
                xScale = cfg["scene"]["terrain"]["extent_width"]
                zScale = cfg["scene"]["terrain"]["extent_height"]
                # treeX = xScale - x * (2 * xScale) / float(img_w)
                # treeZ = zScale - y * (2 * zScale) / float(img_h)
                treeX = 0.5*xScale - x
                treeZ = 0.5*zScale - y
                translatenode.setAttribute("x", str(treeX))
                translatenode.setAttribute("z", str(treeZ))
                if cfg["scene"]["terrain"]["terrain_type"] != "PLANE":
                    ray = Ray()
                    ray.setOrigin(Point(treeX, 9999, treeZ))
                    ray.setDirection(Vector(0, -1, 0))
                    its = scene.rayIntersect(ray)
                    if not its is None:
                        translatenode.setAttribute("y", str(its.p[1]+z))
                        # translatenode.setAttribute("y", str(z))
                    else:
                        # log("warning: precise height not found.")
                        if cfg["scene"]["terrain"]["terrain_type"] == "RASTER":
                            im_r = int((y / float(zScale)) * img_h)
                            im_c = int((x / float(xScale)) * img_w)
                            translatenode.setAttribute("y", str(dem_arr[im_r][im_c]+z))
                        else:
                            translatenode.setAttribute("y", str(z))
                else:
                    translatenode.setAttribute("y", str(z))

            treeIdx += 1

        xm = doc.toprettyxml()
        # xm = xm.replace('<?xml version="1.0" ?>', '')
        f.write(xm)
        f.close()

        log("INFO: Objects and positions generated.")

    @staticmethod
    def test():
        import socket
        import mitsuba

        from mitsuba.core import RemoteWorker, SocketStream

        stream = SocketStream('127.0.0.1', 7554)
        # Create a remote worker instance that communicates over the stream
        remoteWorker = RemoteWorker('netWorker', stream)




if __name__ == "__main__":
    # SceneGenerate.terr_generate(session.getState("current_sim")+"/input/input.conf")
    # SceneGenerate.forest_generate_according_tree_pos_file(session.getState("current_sim") + "/input/input.conf")
    SceneGenerate.test()


