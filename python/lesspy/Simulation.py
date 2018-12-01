#coding: utf-8
from session import *
#执行模拟

import os
import subprocess
import math
from RasterHelper import *
# sys.path.append(os.getcwd()+'/rt/dist-rgb/python/2.7')


def do_ats_simulation(cores):
    currdir = os.path.split(os.path.realpath(__file__))[0]
    rt_dir = os.path.join(currdir + '/bin/rt/' + current_rt_program)
    os.environ['PATH'] = rt_dir + os.pathsep + os.environ['PATH']
    cfgfile = session.get_config_file()
    f = open(cfgfile, 'r')
    cfg = json.load(f)
    excuable = "lessrt"

    distFile = os.path.join(session.get_output_dir(), "atsIllumination")
    scene_file_path = os.path.join(session.get_scenefile_path(), atmosphere_scene_file)

    server_file = os.path.join(session.get_input_dir(), "server.txt")
    current_working_dir = os.getcwd()
    os.chdir(rt_dir)
    if cfg["Advanced"]["network_sim"]:
        if cores == -1:
            subprocess.call([excuable, scene_file_path, "-o", distFile, "-s", server_file])
        else:
            subprocess.call(
                [excuable, scene_file_path, "-o", distFile, "-p", cores, "-s", server_file])
    else:
        if cores == -1:
            subprocess.call([excuable, scene_file_path, "-o", distFile])
        else:
            subprocess.call([excuable, scene_file_path, "-o", distFile, "-p", str(cores)])
    os.chdir(current_working_dir)


def do_simulation_multi_spectral(cores):
    currdir = os.path.split(os.path.realpath(__file__))[0]
    rt_dir = os.path.join(currdir + '/bin/rt/'+current_rt_program)
    os.environ['PATH'] =  rt_dir + os.pathsep + os.environ['PATH']
    cfgfile = session.get_config_file()
    f = open(cfgfile, 'r')
    cfg = json.load(f)
    excuable = "lessrt"
    distFileName = ""
    imgPrefix = ""
    if cfg["sensor"]["thermal_radiation"]:
        imgPrefix = thermal_img_prefix
    else:
        imgPrefix = spectral_img_prefix

    if cfg["sensor"]["sensor_type"] == "orthographic":
        distFileName = imgPrefix + "VZ=" + str(cfg["observation"]["obs_zenith"]) + \
                "_VA=" + str(cfg["observation"]["obs_azimuth"])
    if cfg["sensor"]["sensor_type"] == "perspective" or cfg["sensor"]["sensor_type"] == "CircularFisheye":
        ox,oy,oz,tx,ty,tz = cfg["observation"]["obs_o_x"], cfg["observation"]["obs_o_y"], cfg["observation"]["obs_o_z"],\
                            cfg["observation"]["obs_t_x"], cfg["observation"]["obs_t_y"], cfg["observation"]["obs_t_z"]
        distFileName = imgPrefix + "ox=%.2f_oy=%.2f_oz=%.2f_tx=%.2f_ty=%.2f_tz=%.2f"%(ox,oy,oz,tx,ty,tz)
        distFileName = distFileName.replace(".","_")

    if cfg["sensor"]["sensor_type"] == "PhotonTracing":
        distFileName = photon_tracing_img_prefix + str(cfg["sensor"]["PhotonTracing"]["sunRayResolution"]).replace(".", "_")

    distFile = os.path.join(session.get_output_dir(), distFileName)
    scene_file_path = os.path.join(session.get_scenefile_path(), main_scene_xml_file)

    server_file = os.path.join(session.get_input_dir(),"server.txt")
    current_working_dir = os.getcwd()
    os.chdir(rt_dir)
    if cfg["Advanced"]["network_sim"]:
        if cores == -1:
            subprocess.call([excuable, scene_file_path, "-o", distFile,"-s", server_file])
        else:
            subprocess.call(
                [excuable, scene_file_path, "-o", distFile,"-p",cores, "-s", server_file])
    else:
        if cores == -1:
            subprocess.call([excuable,scene_file_path,"-o",distFile])
        else:
            subprocess.call([excuable, scene_file_path, "-o", distFile,"-p", str(cores)])
    os.chdir(current_working_dir)

    # subprocess.check_output([excuable,scene_file_path,"-o",distFile])
    # sys.exit(0)
    #write info.txt
    infofile = os.path.join(session.get_output_dir(), spectral_info_file)
    f = open(infofile,'w')
    f.write(distFileName)
    f.close()

    if cfg["sensor"]["sensor_type"] == "PhotonTracing":
        out_file_no_extension = distFile + "_downwelling"
        output_fileName = distFile + "_downwelling.npy"
        if output_format not in ("npy", "NPY") and os.path.exists(output_fileName):
            data = np.load(output_fileName)
            bandlist = cfg["sensor"]["bands"].split(",")
            RasterHelper.saveToHdr_no_transform(data, out_file_no_extension, bandlist, output_format)
            os.remove(output_fileName)
        out_file_no_extension = distFile + "_upwelling"
        output_fileName = distFile + "_upwelling.npy"
        if output_format not in ("npy", "NPY") and os.path.exists(output_fileName):
            data = np.load(output_fileName)
            bandlist = cfg["sensor"]["bands"].split(",")
            RasterHelper.saveToHdr_no_transform(data, out_file_no_extension, bandlist, output_format)
            os.remove(output_fileName)
    else:
        out_file_no_extension = distFile + "_4Components"
        output_fileName = distFile + "_4Components.npy"

        if output_format not in ("npy", "NPY") and os.path.exists(output_fileName):
            data = np.load(output_fileName)
            dshape = data.shape
            if len(dshape) == 3:
                data = data[:,:,0]
            bandlist = []
            RasterHelper.saveToHdr_no_transform(data, out_file_no_extension, bandlist, output_format)
            os.remove(output_fileName)

        if output_format not in ("npy", "NPY") and os.path.exists(distFile + ".npy"):
            data = np.load(distFile + ".npy")

            # converte to brightness temperature
            if cfg["sensor"]["thermal_radiation"]:
                bandlist = cfg["sensor"]["bands"].split(",")
                data = RasterHelper.convertRadiance2BTimage(data, bandlist)

            bandlist = cfg["sensor"]["bands"].split(",")
            RasterHelper.saveToHdr_no_transform(data, distFile, bandlist, output_format)
            os.remove(distFile + ".npy")

    log("INFO: Finished")



def do_simulation_multi_spectral_py():
    currdir = os.path.split(os.path.realpath(__file__))[0]
    sys.path.append(currdir + '/bin/rt/' + current_rt_program + '/python/2.7/')
    os.environ['PATH'] = currdir + '/bin/rt/' + current_rt_program + os.pathsep + os.environ['PATH']
    import mitsuba
    from mitsuba.core import Vector, Point, Ray, Thread, Scheduler, LocalWorker, PluginManager, Transform
    from mitsuba.render import SceneHandler
    from mitsuba.render import RenderQueue, RenderJob
    from mitsuba.render import Scene
    import multiprocessing

    scheduler = Scheduler.getInstance()
    for i in range(0, multiprocessing.cpu_count()):
        scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))
    scheduler.start()

    cfgfile = session.get_config_file()
    f = open(cfgfile, 'r')
    cfg = json.load(f)
    distFileName = spectral_img_prefix + "_VZ=" + str(cfg["observation"]["obs_zenith"]) + \
                   "_VA=" + str(cfg["observation"]["obs_azimuth"])
    distFile = os.path.join(session.get_output_dir(), distFileName).encode("utf-8")
    scene_file_path = os.path.join(session.get_scenefile_path(), main_scene_xml_file).encode("utf-8")

    scene_path = session.get_scenefile_path().encode("utf-8")
    fileResolver = Thread.getThread().getFileResolver()
    fileResolver.appendPath(scene_path)
    scene = SceneHandler.loadScene(fileResolver.resolve(scene_file_path))
    scene.setDestinationFile(distFile)
    scene.configure()
    scene.initialize()
    queue = RenderQueue()
    sceneResID = scheduler.registerResource(scene)
    job = RenderJob(('Simulation Job '+distFileName).encode("utf-8"), scene, queue, sceneResID)
    job.start()
    queue.waitLeft(0)
    queue.join()

    if output_format not in ("npy", "NPY") and os.path.exists(distFile + ".npy"):
        data = np.load(distFile + ".npy")
        bandlist = cfg["sensor"]["bands"].split(",")
        RasterHelper.saveToHdr_no_transform(data, distFile, bandlist, output_format)
        os.remove(distFile + ".npy")
    log("INFO: Finished")

def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

# def do_simulation_multi_spectral_seq(seqname):
#     currdir = os.path.split(os.path.realpath(__file__))[0]
#     os.environ['PATH'] = currdir + '/bin/rt/'+current_rt_program + os.pathsep + os.environ['PATH']
#     cfgfile = session.get_config_file()
#     f = open(cfgfile, 'r')
#     cfg = json.load(f)
#     excuable = "lessrt"
#     scene_path = session.get_scenefile_path()
#     seq_header = seq_file_prefix + "_" + seqname
#     for filename in os.listdir(scene_path):
#         if os.path.isfile(combine_file_path(scene_path, filename)):
#             if filename.startswith(seq_header):
#                 distFile = combine_file_path(session.get_output_dir(),\
#                                              spectral_img_prefix + filename[0:len(filename) - 4])
#                 parameter = " -o " + distFile
#                 cmd = excuable + " " + combine_file_path(session.get_scenefile_path(), filename) + parameter
#                 os.system(cmd)
#                 if output_format not in ("npy", "NPY"):
#                     data = np.load(distFile + ".npy")
#                     bandlist = cfg["sensor"]["bands"].split(",")
#                     RasterHelper.saveToHdr_no_transform(data, distFile, bandlist, output_format)
#                     os.remove(distFile + ".npy")


def do_simulation_multiangle_seq(seqname):
    currdir = os.path.split(os.path.realpath(__file__))[0]
    sys.path.append(currdir + '/bin/rt/' + current_rt_program + '/python/2.7/')
    os.environ['PATH'] = currdir + '/bin/rt/' + current_rt_program + os.pathsep + os.environ['PATH']
    import mitsuba
    from mitsuba.core import Vector, Point, Ray, Thread, Scheduler, LocalWorker, PluginManager, Transform
    from mitsuba.render import SceneHandler
    from mitsuba.render import RenderQueue, RenderJob
    from mitsuba.render import Scene
    import multiprocessing

    scheduler = Scheduler.getInstance()
    for i in range(0, multiprocessing.cpu_count()):
        scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))
    scheduler.start()


    scene_path = session.get_scenefile_path()
    fileResolver = Thread.getThread().getFileResolver()
    fileResolver.appendPath(str(scene_path))
    scene = SceneHandler.loadScene(fileResolver.resolve(
        str(os.path.join(session.get_scenefile_path(), main_scene_xml_file))))
    scene.configure()
    scene.initialize()
    queue = RenderQueue()
    sceneResID = scheduler.registerResource(scene)
    bsphere = scene.getKDTree().getAABB().getBSphere()
    radius = bsphere.radius
    targetx, targety, targetz = bsphere.center[0], bsphere.center[1], bsphere.center[2]
    f = open(seqname + ".conf", 'r')
    params = json.load(f)
    obs_azimuth = params['seq1']['obs_azimuth']
    obs_zenith = params['seq2']['obs_zenith']
    cfgfile = session.get_config_file()
    f = open(cfgfile, 'r')
    cfg = json.load(f)
    viewR = cfg["sensor"]["obs_R"]
    mode = cfg["sensor"]["film_type"]
    azi_arr = map(lambda x: float(x), obs_azimuth.strip().split(":")[1].split(","))
    zeni_arr = map(lambda x: float(x), obs_zenith.strip().split(":")[1].split(","))
    seq_header = multi_file_prefix + "_" + seqname
    index = 0
    for azi in azi_arr:
        for zeni in zeni_arr:
            distFile = os.path.join(session.get_output_dir(),
                                    seq_header + ("_VA_%.2f" % azi).replace(".", "_") + ("_VZ_%.2f" % zeni).replace(".", "_"))
            newScene = Scene(scene)
            pmgr = PluginManager.getInstance()
            newSensor = pmgr.createObject(scene.getSensor().getProperties())
            theta = zeni / 180.0 * math.pi
            phi = (azi - 90) / 180.0 * math.pi
            scale_x = radius
            scale_z = radius
            toWorld = Transform.lookAt(
                Point(targetx - viewR * math.sin(theta) * math.cos(phi), targety + viewR * math.cos(theta),
                      targetz - viewR * math.sin(theta) * math.sin(phi)),  # original
                Point(targetx, targety, targetz),  # target
                Vector(0, 0, 1)  # up
            ) * Transform.scale(
                Vector(scale_x, scale_z, 1)  # 视场大小
            )
            newSensor.setWorldTransform(toWorld)
            newFilm = pmgr.createObject(scene.getFilm().getProperties())
            newFilm.configure()
            newSensor.addChild(newFilm)
            newSensor.configure()
            newScene.addSensor(newSensor)
            newScene.setSensor(newSensor)
            newScene.setSampler(scene.getSampler())
            newScene.setDestinationFile(str(distFile))
            job = RenderJob('Simulation Job' + "VA_"+str(azi)+"_VZ_"+str(zeni), newScene, queue, sceneResID)
            job.start()
        queue.waitLeft(0)
        queue.join()
    # handle npy
    if mode == "spectrum" and (output_format not in ("npy", "NPY")):
        for azi in azi_arr:
            for zeni in zeni_arr:
                distFile = os.path.join(session.get_output_dir(),
                                        seq_header + ("_VA_%.2f" % azi).replace(".", "_") + ("_VZ_%.2f" % zeni).replace(
                                            ".", "_"))
                data = np.load(distFile + ".npy")
                bandlist = cfg["sensor"]["bands"].split(",")
                RasterHelper.saveToHdr_no_transform(data, distFile, bandlist, output_format)
                os.remove(distFile + ".npy")


if __name__ == "__main__":
    data = np.load(r"C:\Users\Jim\Desktop\12\m_multiangle_VA_150_94_VZ_9_00.npy")
    distFile = r"C:\Users\Jim\Desktop\12\m_multiangle_VA_150_94_VZ_9_00"
    RasterHelper.saveToHdr_no_transform(data, distFile, bandlist, output_format)














