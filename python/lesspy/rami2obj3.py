#coding: utf-8
# convert RAMI scene into obj file

import os
import argparse
import math
from pyrr import Matrix44, Vector4, Vector3

parser = argparse.ArgumentParser(description='Convert RAMI scene into obj file.')
parser.add_argument("-phase", help="RAMI Phases: 1, 2, 3, IV.", required=True)
parser.add_argument("-sceneID", help="Scene name.", required=True)
parser.add_argument("-distDir", help="Destination dir.", required=True)
parser.add_argument("-X", type=float, help="X dimention.", required=True)
parser.add_argument("-Y", type=float, help="Y dimention.", required=True)
args = parser.parse_args()


def getTransMatrix(trans_arr):
    matrix = Matrix44()
    matrix[0][0] = trans_arr[0]
    matrix[0][1] = trans_arr[1]
    matrix[0][2] = trans_arr[2]
    matrix[1][0] = trans_arr[3]
    matrix[1][1] = trans_arr[4]
    matrix[1][2] = trans_arr[5]
    matrix[2][0] = trans_arr[6]
    matrix[2][1] = trans_arr[7]
    matrix[2][2] = trans_arr[8]
    matrix[3][3] = 1
    return matrix

def degree_to_rad(angle):
    return angle/float(180)*math.pi


# combine file path for two parameters
def combine_file_path(p1, p2):
    if p1[-1] != os.path.sep:
        p1 += os.path.sep
    return p1+p2

# combine file paths for several parameters
def combine_file_path_multi(*args):
    param_len = len(args)
    final_path = args[0]
    for i in range(1, param_len):
        final_path = combine_file_path(final_path, args[i])
    return final_path

# needle is represented as cylinders with discs as end caps
# the cylinder is approximated as hexagonal prism controlled by total area
class Needle:
    def __init__(self, needle_diameter=0.00092, needle_length=0.0285, needle_area=6.472631578947369e-05):
        self.needle_diameter = needle_diameter
        self.needle_length = needle_length
        self.needle_area = needle_area

        # hexagonal
        self.side_length = self.compute_length_of_cross_side()
        self.lower_plane = []
        self.upper_plane = []
        self.generate_vertexs()
        self.vertexes = self.lower_plane + self.upper_plane

    def get_total_surface_area(self):
        return self.needle_area
    # def get_total_surface_area(self):
    #     r = self.needle_diameter*0.5
    #     return 2*math.pi*r*r+math.pi*self.needle_diameter*self.needle_length

    def compute_length_of_cross_side(self):
        delta = math.sqrt(36*self.needle_length*self.needle_length+12*math.sqrt(3)*self.get_total_surface_area())
        side_length = (-6*self.needle_length + delta)/float(6*math.sqrt(3))
        return side_length

    def generate_vertexs(self):
        """
        First generate a needle along y axis, originated at (0,0,0), Y is vertical axis.
        """
        for i in range(0, 360, 60):
            angle_rad = degree_to_rad(i)
            x = self.side_length * math.cos(angle_rad)
            y = self.side_length * math.sin(angle_rad)
            self.lower_plane.append([x, y, 0])
            self.upper_plane.append([x, y, self.needle_length])

    def toObj(self, filepath):
        f = open(filepath, 'w')
        num = len(self.vertexes)
        for i in range(0, num):
            f.write("v " + str(-self.vertexes[i][0]) + " " +
                    str(self.vertexes[i][2]) + " " + str(self.vertexes[i][1]) + "\n")
        lower = "f"
        upper = "f"
        num = int(num*0.5)
        for i in range(1, num + 1):
            if i == num:
                next_i = 1
            else:
                next_i = i + 1
            f.write("f " + str(i) + " " + str(next_i) + " " + str(num + next_i) + " " + str(num + i) + "\n")
            lower += " " + str(num - i + 1)
            upper += " " + str(num + i)
        f.write(lower + "\n")
        f.write(upper + "\n")
        f.close()


class Shoot:
    def __init__(self, needle, twig_length=0.077, twig_diameter=0.003):
        self.prim_needle = needle
        self.vertexes = []
        self.twig_vertexes = []
        self.needle_num = 0
        self.twig_length = twig_length
        self.twig_diameter = twig_diameter

    def generate_twig_from_file(self, filepath):
        f = open(filepath, 'r')
        for line in f:
            if line.startswith("sphere"):
                arr = line.split(" ")
                if len(arr) > 10:
                    self.needle_num += 1
                    zenith_rotation_angle = degree_to_rad(float(arr[13]))
                    azimuth_rotation_angle = degree_to_rad(float(arr[18]))
                    translate_vector = Vector3([float(arr[20]), float(arr[21]), float(arr[22])])
                    matrix = Matrix44.from_y_rotation(zenith_rotation_angle)
                    matrix = matrix * Matrix44.from_z_rotation(azimuth_rotation_angle)
                    matrix = matrix * Matrix44.from_translation(translate_vector)
                    # applying rotation
                    newNeedle_vertexes = list(map(lambda x: matrix * Vector3(x), self.prim_needle.vertexes))
                    self.vertexes += newNeedle_vertexes
        f.close()
        # generate twig
        r = math.pi * self.twig_diameter / 6.0
        lower_plane, upper_plane = [], []
        for i in range(0, 360, 60):
            angle_rad = degree_to_rad(i)
            x = r * math.cos(angle_rad)
            y = r * math.sin(angle_rad)
            lower_plane.append([x, y, 0])
            upper_plane.append([x, y, self.twig_length])
        self.twig_vertexes = lower_plane + upper_plane


    def toObj(self, filepath):
        f = open(filepath, 'w')
        vnum = len(self.vertexes)
        for i in range(0, vnum):
            f.write("v " + str(-self.vertexes[i][0]) + " " +
                    str(self.vertexes[i][2]) + " " + str(self.vertexes[i][1]) + "\n")

        for i in range(0, len(self.twig_vertexes)):
            f.write("v " + str(-self.twig_vertexes[i][0]) + " " +
                    str(self.twig_vertexes[i][2]) + " " + str(self.twig_vertexes[i][1]) + "\n")

        # write f needle
        for i in range(0, self.needle_num):
            num = len(self.prim_needle.vertexes)
            needle_start = i * num
            lower = "f"
            upper = "f"
            num = int(num * 0.5)
            for i in range(1, num + 1):
                if i == num:
                    next_i = 1
                else:
                    next_i = i + 1
                f.write("f " + str(needle_start+i) + " " + str(needle_start+next_i) + " " +
                        str(needle_start+num + next_i) + " " + str(needle_start+num + i) + "\n")
                lower += " " + str(needle_start + num - i + 1)
                upper += " " + str(needle_start + num + i)
            f.write(lower + "\n")
            f.write(upper + "\n")

        # twig
        lower = "f"
        upper = "f"
        num = len(self.twig_vertexes)
        num = int(num * 0.5)
        start = len(self.prim_needle.vertexes) * self.needle_num
        for i in range(1, num + 1):
            if i == num:
                next_i = 1
            else:
                next_i = i + 1
            f.write("f " + str(start+i) + " " + str(start+next_i) + " " +
                    str(start+num + next_i) + " " + str(start+num + i) + "\n")
            lower += " " + str(start+num - i + 1)
            upper += " " + str(start+num + i)
        f.write(lower + "\n")
        f.write(upper + "\n")
        f.close()

class PISYTree:
    def __init__(self, shoot, foliage_file, stem_file, branch_file):
        self.shoot = shoot
        self.foliage_file = foliage_file
        self.stem_file = stem_file
        self.branch_file = branch_file

        self.leaf_vertexes = []
        self.branch_vertexes = []
        self.twig_vertexes = []

        self.shoot_num = 0

    def generate_tree(self):
        # generate leaves
        f = open(self.foliage_file, 'r')
        for line in f:
            if line.startswith("object"):
                arr = line.replace("\n", "").replace("  "," ").split(" ")
                if len(arr) > 10:
                    self.shoot_num += 1
                    matrix = getTransMatrix(list(map(lambda x: float(x), arr[3:])))
                    trans = list(map(lambda x: float(x), arr[-3:]))
                    translate_vector = Vector3(trans)
                    matrix = matrix * Matrix44.from_translation(translate_vector)
                    new_shoot_vertexes = list(map(lambda x: matrix * Vector3(x), self.shoot.vertexes))
                    self.leaf_vertexes += new_shoot_vertexes
                    new_twig_vertexes = list(map(lambda x: matrix * Vector3(x), self.shoot.twig_vertexes))
                    self.twig_vertexes += new_twig_vertexes
        f.close()

        # generate branches
        f = open(self.branch_file, 'r')
        line_index = 0
        for line in f:
            if line.startswith("triangle") and line_index > 10:
                arr = line.replace("\n", "").split(" ")
                arr = list(map(lambda x: float(x), arr[1:]))
                self.branch_vertexes.append([arr[0], arr[1], arr[2]])
                self.branch_vertexes.append([arr[3], arr[4], arr[5]])
                self.branch_vertexes.append([arr[6], arr[7], arr[8]])
            line_index += 1

        # generate stem
        f = open(self.stem_file, 'r')
        line_index = 0
        for line in f:
            if line.startswith("triangle") and line_index > 10:
                arr = line.replace("\n", "").split(" ")
                arr = list(map(lambda x: float(x), arr[1:]))
                self.branch_vertexes.append([arr[0], arr[1], arr[2]])
                self.branch_vertexes.append([arr[3], arr[4], arr[5]])
                self.branch_vertexes.append([arr[6], arr[7], arr[8]])
            line_index += 1

    def toObj(self, leaf_file, branch_file):
        f = open(leaf_file, 'w')
        vnum = len(self.leaf_vertexes)
        for i in range(0, vnum):
            f.write("v " + str(-self.leaf_vertexes[i][0]) + " " +
                    str(self.leaf_vertexes[i][2]) + " " + str(self.leaf_vertexes[i][1]) + "\n")

        # write f
        needleIndex = 0
        for ii in range(0, self.shoot_num):
            for jj in range(0, self.shoot.needle_num):
                num = len(self.shoot.prim_needle.vertexes)
                needle_start = needleIndex * num
                lower = "f"
                upper = "f"
                num = int(num * 0.5)
                for i in range(1, num + 1):
                    if i == num:
                        next_i = 1
                    else:
                        next_i = i + 1
                    f.write("f " + str(needle_start + i) + " " + str(needle_start + next_i) + " " +
                            str(needle_start + num + next_i) + " " + str(needle_start + num + i) + "\n")
                    lower += " " + str(needle_start + num - i + 1)
                    upper += " " + str(needle_start + num + i)
                f.write(lower + "\n")
                f.write(upper + "\n")
                needleIndex += 1
        f.close()



        f = open(branch_file, 'w')
        # write branch
        vertex_num = len(self.branch_vertexes)
        for i in range(0, vertex_num):
            f.write("v " + str(-self.branch_vertexes[i][0]) + " " +
                    str(self.branch_vertexes[i][2]) + " " + str(self.branch_vertexes[i][1]) + "\n")

        for i in range(0, len(self.twig_vertexes)):
            f.write("v " + str(-self.twig_vertexes[i][0]) + " " +
                    str(self.twig_vertexes[i][2]) + " " + str(self.twig_vertexes[i][1]) + "\n")

        # branch f
        for i in range(1, vertex_num + 1, 3):
            f.write("f " + str(i) + " " + str(i + 2) + " " +
                    str(i + 1) + "\n")
        # twig
        for i in range(0, self.shoot_num):
            num = len(self.shoot.twig_vertexes)
            needle_start = vertex_num + i * num
            lower = "f"
            upper = "f"
            num = int(num * 0.5)
            for i in range(1, num + 1):
                if i == num:
                    next_i = 1
                else:
                    next_i = i + 1
                f.write("f " + str(needle_start + i) + " " + str(needle_start + next_i) + " " +
                        str(needle_start + num + next_i) + " " + str(needle_start + num + i) + "\n")
                lower += " " + str(needle_start + num - i + 1)
                upper += " " + str(needle_start + num + i)
            f.write(lower + "\n")
            f.write(upper + "\n")
        f.close()

class BirchLeaf:
    def __init__(self):
        self.leaf_vertexes = []
        self.twig_vertex = []

    def generate_leaf_from_file(self, leaf_path):
        f = open(leaf_path, 'r')
        line_index = 1
        for line in f:
            if line.startswith("triangle") and line_index > 20:
                arr = line.replace("\n" , "").strip().replace("   ", " ").split(" ")
                arr = list(map(lambda x: float(x), arr[1:]))
                self.leaf_vertexes.append([arr[0], arr[1], arr[2]])
                self.leaf_vertexes.append([arr[3], arr[4], arr[5]])
                self.leaf_vertexes.append([arr[6], arr[7], arr[8]])
            line_index += 1


class BirchTree:
    def __init__(self, leaf,  foliage_file, stem_file, branch_file):
        self.leaf = leaf
        self.leaves_vertex = []
        self.branch_vertexes = []

        self.leaf_num = 0

        self.foliage_file = foliage_file
        self.stem_file = stem_file
        self.branch_file = branch_file

    def generate_tree(self):
        # generate leaves
        f = open(self.foliage_file, 'r')
        line_index = 1
        for line in f:
            if line.startswith("object") and line_index > 60:
                self.leaf_num += 1
                arr = line.replace("\n", "").replace("  ", " ").split(" ")
                matrix = getTransMatrix(map(lambda x: float(x), arr[3:]))
                trans = list(map(lambda x: float(x), arr[-3:]))
                translate_vector = Vector3(trans)
                matrix = matrix * Matrix44.from_translation(translate_vector)
                self.leaves_vertex += map(lambda x: matrix * Vector3(x), self.leaf.leaf_vertexes)
            line_index += 1
        f.close()

        # generate branches
        f = open(self.branch_file, 'r')
        line_index = 0
        for line in f:
            if line.startswith("triangle") and line_index > 10:
                arr = line.replace("\n", "").split(" ")
                arr = list(map(lambda x: float(x), arr[1:]))
                self.branch_vertexes.append([arr[0], arr[1], arr[2]])
                self.branch_vertexes.append([arr[3], arr[4], arr[5]])
                self.branch_vertexes.append([arr[6], arr[7], arr[8]])
            line_index += 1

        # generate stem
        f = open(self.stem_file, 'r')
        line_index = 0
        for line in f:
            if line.startswith("triangle") and line_index > 10:
                arr = line.replace("\n", "").split(" ")
                arr = list(map(lambda x: float(x), arr[1:]))
                self.branch_vertexes.append([arr[0], arr[1], arr[2]])
                self.branch_vertexes.append([arr[3], arr[4], arr[5]])
                self.branch_vertexes.append([arr[6], arr[7], arr[8]])
            line_index += 1

    def toObj(self, leaf_file, branch_file):
        f = open(leaf_file, 'w')
        vnum = len(self.leaves_vertex)
        for i in range(0, vnum):
            f.write("v " + str(-self.leaves_vertex[i][0]) + " " +
                    str(self.leaves_vertex[i][2]) + " " + str(self.leaves_vertex[i][1]) + "\n")

        # write f
        for i in range(1, vnum+1, 3):
            f.write("f " + str(i) + " " + str(i + 2) + " " +
                    str(i + 1) + "\n")
        f.close()

        f = open(branch_file, 'w')
        # write branch
        vertex_num = len(self.branch_vertexes)
        for i in range(0, vertex_num):
            f.write("v " + str(-self.branch_vertexes[i][0]) + " " +
                    str(self.branch_vertexes[i][2]) + " " + str(self.branch_vertexes[i][1]) + "\n")
        # branch f
        for i in range(1, vertex_num + 1, 3):
            f.write("f " + str(i) + " " + str(i + 2) + " " +
                    str(i + 1) + "\n")
        f.close()





class Forest:
    def __init__(self):
        self.forest_data = dict()
    """
    generate tree positions from transform file
    """
    # input the template folder, it will automatically extract the transform files
    def generate_forest_accordering_to_transform(self, template_folder):
        file_list = os.listdir(template_folder)
        for file in file_list:
            arr = file.split("_")
            if arr[1] == "treetransform.dat":
                tree_id = arr[0]
                file_path = combine_file_path(template_folder, file)
                f = open(file_path, 'r')
                line_num = 0
                rotation_arr = []
                translate_arr = []
                for line in f:
                    if line.startswith("object") and line_num > 10:
                        line_arr = line.replace("\n", "").split(" ")
                        rotation_arr.append(float(line_arr[6]))
                        translate_arr.append(list(map(lambda x: float(x), line_arr[-3:])))
                    line_num += 1
                self.forest_data[tree_id] = [translate_arr,rotation_arr]
                f.close()

    def to_position_file(self, positionfile):
        f = open(positionfile, 'w')
        for tree in self.forest_data:
            f.write("o " + tree +"_branch_stem.obj branch_reflectance "+tree +"_foliage.obj leaf_ref_trans\n")
        index = 0
        for tree in self.forest_data:
            pos_data, rotation_data = self.forest_data[tree]
            for i in range(0, len(rotation_data)):
                f.write("i %.5f %.5f %d %.5f\n" % (pos_data[i][0], args.Y-pos_data[i][1], index, rotation_data[i]))
            index += 1
        f.close()

if args.phase == "RAMI-IV" and args.sceneID == "HET07_JPS_SUM":
    print(args.phase, args.sceneID)
    distDir = args.distDir
    currdir = os.path.split(os.path.realpath(__file__))[0]
    template_folder = combine_file_path_multi(currdir, "template", "RAMI", "RAMI-IV", "HET07_JPS_SUM")
    shoot_file = combine_file_path(template_folder, "PISY_shoot.def")
    # needle = Needle()
    # needle.toObj(r"E:\Coding\Mitsuba\simulations\RAMI4new\needle.obj")
    # shoot = Shoot(needle)
    # shoot.generate_twig_from_file(shoot_file)
    # shoot.toObj(r"E:\Coding\Mitsuba\simulations\RAMI4new\shoot.obj")

    # leaf_file = combine_file_path(template_folder, "BEPE_leaf.def")
    # foliage_file = combine_file_path(template_folder, "BEPE_foliage.dat")
    # stem_file = combine_file_path(template_folder, "BEPE_stem.dat")
    # branch_file = combine_file_path(template_folder, "BEPE_branches.dat")
    #
    # birch_leaf = BirchLeaf()
    # birch_leaf.generate_leaf_from_file(leaf_file)
    # bt = BirchTree(birch_leaf, foliage_file, stem_file, branch_file)
    # bt.generate_tree()
    # leaf_path = combine_file_path(distDir, "BEPE_foliage.obj")
    # branch_path = combine_file_path(distDir, "BEPE_branch_stem.obj")
    # bt.toObj(leaf_path, branch_path)

    # f = Forest()
    # f.generate_forest_accordering_to_transform(template_folder)
    # tree_file = combine_file_path(distDir, "trees.txt")
    # print tree_file
    # f.to_position_file(tree_file)

    # for i in range(9, 11):
    #     print("PISY" + str(i))
    #     foliage_file = combine_file_path(template_folder,"PISY"+str(i)+"_foliage.dat")
    #     stem_file = combine_file_path(template_folder, "PISY"+str(i)+"_stem.dat")
    #     branch_file = combine_file_path(template_folder, "PISY"+str(i)+"_branches.dat")

    #     needle = Needle()
    #     shoot = Shoot(needle)
    #     shoot.generate_twig_from_file(shoot_file)

    #     psitree = PISYTree(shoot, foliage_file, stem_file, branch_file)
    #     psitree.generate_tree()
    #     leaf_path = combine_file_path(distDir, "PISY"+str(i)+"_foliage.obj")
    #     branch_path = combine_file_path(distDir, "PISY"+str(i)+"_branch_stem.obj")
    #     psitree.toObj(leaf_path, branch_path)










