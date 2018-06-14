import platform
import os
import sys
import argparse
import socket
from Constant import current_rt_program, main_scene_xml_file
from session import session
print("Python", platform.python_version())

currdir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(currdir,"Utility","CSFtools"))
sys.path.append(os.path.join(currdir,"bin","rt",current_rt_program,"python","3.6"))
os.environ['PATH'] = os.path.join(currdir, "bin","rt",current_rt_program)+ os.pathsep + os.environ['PATH']

from mitsuba.core import Vector, Point, Ray, Thread
from mitsuba.render import SceneHandler
from mitsuba.render import Intersection


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--project', help="Project name.")
parser.add_argument('-x', '--width', help="Width of the scene.",type=float)
parser.add_argument('-y', '--height', help="Height of the scene.",type=float)
args = parser.parse_args()

project_dir = args.project
Defined_XSize = args.width
Defined_YSize = args.height

# class to represent the whole scene
class LESS:
    def __init__(self, XSize=Defined_XSize, YSize=Defined_YSize):
        self.XSize = XSize
        self.YSize = YSize

    # get the scene object
    def getScene(self):
        if(project_dir == "null"):
            print("No simulation.")
            return

        fileResolver = Thread.getThread().getFileResolver()
        logger = Thread.getThread().getLogger()
        logger.clearAppenders()
        scenepath = session.get_scenefile_path_according_to_basedir(project_dir)
        fileResolver.appendPath(str(scenepath))
        main_xml = str(os.path.join(scenepath, main_scene_xml_file))
        if not os.path.exists(main_xml):
            print("Simulation not generated.")
            return
        scene = SceneHandler.loadScene(main_xml)
        scene.configure()
        scene.initialize()
        return LessScene(scene, self.XSize, self.YSize)

    def generate3D(self):
        os.system(self.getPyExePath() +" "+ self.getScriptPath("less") +" -g s")

    def generateView(self):
        os.system(self.getPyExePath() +" "+ self.getScriptPath("less") +" -g v")

    def generateAll(self):
        self.generate3D()
        self.generateView()

    # def runLess(self,cores=-1):
    #     os.system(self.getPyExePath() + " " + self.getScriptPath("less.py") + " -r n -p "+str(cores))

    def getPyExePath(self):
        return sys.executable

    def getScriptPath(self,script):
        script_path = os.path.join(currdir, script+".py")
        if not os.path.exists(script_path):
            return os.path.join(currdir, script+".pyc")
        return script_path

    # close the python
    def clear(self):
        sys.exit()


class LessScene:
    def __init__(self, scene, XSize, YSize):
        self.scene = scene
        self.XSize = XSize
        self.YSize = YSize

    # convert x z coordinate system
    def X(self, x):
        return 0.5*self.XSize - x

    def Y(self, y):
        return 0.5*self.YSize - y

    def rayIntersect(self,o, xyz):
        origin = Point(self.X(o[0]), o[2], self.Y(o[1]))
        vector = Vector(-xyz[0], xyz[2], -xyz[1])
        ray = Ray()
        ray.setOrigin(origin)
        ray.setDirection(vector)
        its = self.scene.rayIntersect(ray)
        if its is None:
            return None
        else:
            itsp = its.p
            return self.X(itsp[0]), self.Y(itsp[2]), itsp[1]

class LESSGUI:
    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 8080
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))

    def send(self,message):
        self.sock.sendall(message+"\n")

    def bye(self):
        self.sock.sendall("bye\n")

    def placeInstance(self,xyz):
        xyzstr = "instance_"+str(xyz[0])+"_"+str(xyz[1])+"_"+str(xyz[2])+"\n"
        self.sock.sendall(xyzstr.encode('utf-8'))
#

# if __name__ == "__main__":
#     print 1,2,3