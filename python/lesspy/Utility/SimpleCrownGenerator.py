# coding: utf-8
# Author: Jianbo Qi
# Date: 2020.4.16
# Generate tree crowns with randomly distributed leaves
import numpy as np
from scipy.linalg import expm, norm

class LAD:
    UNIFORM = "Uniform"
    SPHERICAL = "Spherical"
    ERECTOPHILE = "Erectophile"
    EXTREMOPHILE = "Extremophile"
    PLANOPHILE = "Planophile"
    PLAGIOPHILE = "PlagioPhile"


class CrownShape:
    CUBE = "Cube"
    ELLIPSOID = "Ellipsoid"
    CYLINDER = "Cylinder"
    CONE = "Cone"


class LeafShape:
    SQUARE = "Square"
    DISK = "Disk"


class CrownGenerator:
    def __init__(self):
        self.num_of_leaves = 100
        self.leaf_angle_dist = LAD.SPHERICAL
        self.crown_diameter_SN = 1
        self.crown_diameter_EW = 1
        self.crown_height = 3
        self.crown_shape = CrownShape.ELLIPSOID
        self.leaf_shape = LeafShape.SQUARE
        self.leaf_num_triangles = 12
        self.single_leaf_area = 0.01

        # trunk
        self.has_trunk = False
        self.trunk_height = 3
        self.dbh = 0.2

    def _generate_leaf_pos(self):
        all_pos = []
        if self.crown_shape == CrownShape.CUBE:
            for i in range(self.num_of_leaves):
                x = -0.5*self.crown_diameter_EW + np.random.rand()*self.crown_diameter_EW
                z = -0.5*self.crown_diameter_SN + np.random.rand()*self.crown_diameter_SN
                y = np.random.rand()*self.crown_height
                all_pos.append([x, y, z])
        if self.crown_shape == CrownShape.ELLIPSOID:
            for i in range(self.num_of_leaves):
                phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                theta = np.arccos(2*np.random.rand() - 1)  # randomly zenith angle
                r = np.cbrt(np.random.rand())
                x = r*self.crown_diameter_EW*0.5*np.sin(theta)*np.cos(phi)
                z = r*self.crown_diameter_SN*0.5*np.sin(theta)*np.sin(phi)
                y = r*self.crown_height*0.5*np.cos(theta) + self.crown_height*0.5
                all_pos.append([x, y, z])
        if self.crown_shape == CrownShape.CYLINDER:
            for i in range(self.num_of_leaves):
                phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                r = np.sqrt(np.random.rand())
                x = r*self.crown_diameter_EW * 0.5 * np.cos(phi)
                z = r*self.crown_diameter_SN * 0.5 * np.sin(phi)
                y = np.random.rand()*self.crown_height
                all_pos.append([x, y, z])
        if self.crown_shape == CrownShape.CONE:
            for i in range(self.num_of_leaves):
                phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                h = self.crown_height * (np.random.rand()) ** (1 / 3)
                rnd = np.random.rand()
                rew = (0.5*self.crown_diameter_EW / self.crown_height) * h * np.sqrt(rnd)
                rsn = (0.5*self.crown_diameter_SN / self.crown_height) * h * np.sqrt(rnd)
                x = rew * np.cos(phi)
                z = rsn * np.sin(phi)
                y = self.crown_height-h
                all_pos.append([x, y, z])

        return all_pos

    def _generate_leaf_normal(self):
        '''
        Sphrical: 球形状
        Uniform:统一型
        Planophile：平面型
        Erectophile：竖直型
        Plagiophile：倾斜型
        Extremophile：极端型
        '''
        all_normals = []
        if self.leaf_angle_dist == LAD.SPHERICAL:
            for i in range(self.num_of_leaves):
                phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                theta = np.arccos(np.random.rand())  # randomly zenith angle
                rx = -np.sin(theta) * np.cos(phi)
                rz = np.sin(theta) * np.sin(phi)
                ry = np.cos(theta)
                all_normals.append([rx, ry, rz])
        if self.leaf_angle_dist == LAD.UNIFORM:
            for i in range(self.num_of_leaves):
                phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                theta = np.random.rand() * np.pi * 0.5  # randomly zenith angle
                rx = -np.sin(theta) * np.cos(phi)
                rz = np.sin(theta) * np.sin(phi)
                ry = np.cos(theta)
                all_normals.append([rx, ry, rz])
        if self.leaf_angle_dist == LAD.PLANOPHILE:
            while True:
                theta = np.random.rand() * np.pi * 0.5
                y = (2+2*np.cos(2*theta))/np.pi
                rnd_y = np.random.rand()*4/np.pi
                if rnd_y <= y:  # accept
                    phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                    rx = -np.sin(theta) * np.cos(phi)
                    rz = np.sin(theta) * np.sin(phi)
                    ry = np.cos(theta)
                    all_normals.append([rx, ry, rz])
                    if len(all_normals) == self.num_of_leaves:
                        break
        if self.leaf_angle_dist == LAD.ERECTOPHILE:  # 竖直型
            while True:
                theta = np.random.rand() * np.pi * 0.5
                y = (2-2*np.cos(2*theta))/np.pi
                rnd_y = np.random.rand()*4/np.pi
                if rnd_y <= y:  # accept
                    phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                    rx = -np.sin(theta) * np.cos(phi)
                    rz = np.sin(theta) * np.sin(phi)
                    ry = np.cos(theta)
                    all_normals.append([rx, ry, rz])
                    if len(all_normals) == self.num_of_leaves:
                        break
        if self.leaf_angle_dist == LAD.PLAGIOPHILE:  # 倾斜型
            while True:
                theta = np.random.rand() * np.pi * 0.5
                y = (2-2*np.cos(4*theta))/np.pi
                rnd_y = np.random.rand()*4/np.pi
                if rnd_y <= y:  # accept
                    phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                    rx = -np.sin(theta) * np.cos(phi)
                    rz = np.sin(theta) * np.sin(phi)
                    ry = np.cos(theta)
                    all_normals.append([rx, ry, rz])
                    if len(all_normals) == self.num_of_leaves:
                        break
        if self.leaf_angle_dist == LAD.EXTREMOPHILE:  # 极端
            while True:
                theta = np.random.rand() * np.pi * 0.5
                y = (2+2*np.cos(4*theta))/np.pi
                rnd_y = np.random.rand()*4/np.pi
                if rnd_y <= y:  # accept
                    phi = np.random.rand() * np.pi * 2  # randomly azimuth angle
                    rx = -np.sin(theta) * np.cos(phi)
                    rz = np.sin(theta) * np.sin(phi)
                    ry = np.cos(theta)
                    all_normals.append([rx, ry, rz])
                    if len(all_normals) == self.num_of_leaves:
                        break
        return all_normals

    @staticmethod
    def _M(axis, theta):
        return expm(np.cross(np.eye(3), axis / norm(axis) * theta))

    def _generate_single_leaf(self, leaf_pos, leaf_normal, leaf_length):
        leaf_side_length = leaf_length
        # generate leaf according to normal
        if self.leaf_shape == LeafShape.SQUARE:
            # First, find a arbitrary vector which is not parallel with normal
            # and do cross product, the resulting vector is in leaf plane
            arv = np.array([0, 0, 1])
            v = np.cross(leaf_normal, arv)
            v = v / np.linalg.norm(v)
            p1 = leaf_side_length * np.sqrt(2) * 0.5 * v + leaf_pos
            v = np.cross(leaf_normal, v)
            p2 = leaf_side_length * np.sqrt(2) * 0.5 * v + leaf_pos
            v = np.cross(leaf_normal, v)
            p3 = leaf_side_length * np.sqrt(2) * 0.5 * v + leaf_pos
            v = np.cross(leaf_normal, v)
            p4 = leaf_side_length * np.sqrt(2) * 0.5 * v + leaf_pos
            return [p1, p2, p3, p4]
        elif self.leaf_shape == LeafShape.DISK:  # leaf_side_length is leaf radius
            # First, find a arbitrary vector which is not parallel with normal
            # and do cross product, the resulting vector is in leaf plane
            pts = []
            rot_rad = np.pi*2/self.leaf_num_triangles
            arv = np.array([0, 0, 1])
            v0 = np.cross(leaf_normal, arv)
            v0 = v0 / np.linalg.norm(v0)
            p1 = leaf_side_length * v0 + leaf_pos  # 第一个点
            pts.append(p1)
            for i in range(0, self.leaf_num_triangles-1):
                m0 = CrownGenerator._M(np.array(leaf_normal), rot_rad*(i+1))
                newv = np.dot(m0, v0)
                newv = newv / np.linalg.norm(newv)
                newp = leaf_side_length * newv + leaf_pos  # 第一个点
                pts.append(newp)
            return pts
        else:
            print("Leaf shape is not supported.")

    def _calculate_leaf_length(self):
        if self.leaf_shape == LeafShape.SQUARE:
            return np.sqrt(self.single_leaf_area)
        if self.leaf_shape == LeafShape.DISK:
            theta = np.pi * 2 / self.leaf_num_triangles
            tri_leaf = self.single_leaf_area/self.leaf_num_triangles
            leaf_radius = np.sqrt(2*tri_leaf / np.sin(theta))
            return leaf_radius

    def generate_crown(self, dist_obj_path):
        all_pos = self._generate_leaf_pos()
        all_normal = self._generate_leaf_normal()
        f_out = open(dist_obj_path, "w")
        f_out.write("g leaves\n")
        trunk_start_index = 0
        leaf_length = self._calculate_leaf_length()
        h_of_first_branch = 0
        if self.has_trunk:
            h_of_first_branch = self.trunk_height
        for i in range(self.num_of_leaves):
            leaf_pos = all_pos[i]
            leaf_normal = all_normal[i]
            points = self._generate_single_leaf(leaf_pos, leaf_normal, leaf_length)
            if self.leaf_shape == LeafShape.SQUARE:
                p1, p2, p3, p4 = points
                f_out.write("v %.4f %.4f %.4f\n" % (p1[0], p1[1]+h_of_first_branch, p1[2]))
                f_out.write("v %.4f %.4f %.4f\n" % (p2[0], p2[1]+h_of_first_branch, p2[2]))
                f_out.write("v %.4f %.4f %.4f\n" % (p3[0], p3[1]+h_of_first_branch, p3[2]))
                f_out.write("v %.4f %.4f %.4f\n" % (p4[0], p4[1]+h_of_first_branch, p4[2]))
                trunk_start_index += 4
                f_out.write(
                    "f %d %d %d %d\n" % (i * 4 + 1, i * 4 + 2, i * 4 + 3, i * 4 + 4))
            if self.leaf_shape == LeafShape.DISK:
                points.append(leaf_pos)
                tot_pt_each_leaf = len(points)
                trunk_start_index += tot_pt_each_leaf
                for j in range(0, len(points)):
                    f_out.write("v %.4f %.4f %.4f\n" % (points[j][0], points[j][1] + h_of_first_branch, points[j][2]))
                for j in range(0, self.leaf_num_triangles-1):
                    f_out.write(
                        "f %d %d %d\n" % (i * tot_pt_each_leaf + j + 1,
                                          i * tot_pt_each_leaf + j + 2,
                                          i * tot_pt_each_leaf + tot_pt_each_leaf))
                f_out.write(
                    "f %d %d %d\n" % (i * tot_pt_each_leaf + self.leaf_num_triangles,
                                      i * tot_pt_each_leaf + 1,
                                      i * tot_pt_each_leaf + tot_pt_each_leaf))

        # trunk
        if self.has_trunk:
            points_lower = []
            points_upper = []
            f_out.write("g trunk\n")
            for i in range(0, 360, 30):
                angle_rad = np.radians(i)
                r = 0.5*self.dbh
                x = -r * np.cos(angle_rad)
                z = r * np.sin(angle_rad)
                points_lower.append([x, 0, z])
                points_upper.append([x, self.trunk_height, z])
            points_lower.append(points_lower[0])
            points_upper.append(points_upper[0])
            for i in range(0, 12):  # 12个面元
                f_out.write("v %.4f %.4f %.4f\n" % (points_lower[i][0], points_lower[i][1], points_lower[i][2]))
                f_out.write("v %.4f %.4f %.4f\n" % (points_lower[i+1][0], points_lower[i+1][1], points_lower[i+1][2]))
                f_out.write("v %.4f %.4f %.4f\n" % (points_upper[i+1][0], points_upper[i+1][1], points_upper[i+1][2]))
                f_out.write("v %.4f %.4f %.4f\n" % (points_upper[i][0], points_upper[i][1], points_upper[i][2]))
                f_out.write(
                    "f %d %d %d %d\n" % (trunk_start_index + 1,
                                         trunk_start_index + 2,
                                         trunk_start_index + 3,
                                         trunk_start_index + 4))
                trunk_start_index += 4
            #  trunk top
            for i in range(0, 12):  # 12 top triangles
                f_out.write(
                    "v %.4f %.4f %.4f\n" % (points_upper[i][0], points_upper[i][1], points_upper[i][2]))
                f_out.write(
                    "v %.4f %.4f %.4f\n" % (points_upper[i + 1][0], points_upper[i + 1][1], points_upper[i + 1][2]))
                f_out.write(
                    "v %.4f %.4f %.4f\n" % (0, self.trunk_height, 0))
                f_out.write(
                    "f %d %d %d\n" % (trunk_start_index + 1,
                                      trunk_start_index + 2,
                                      trunk_start_index + 3))
                trunk_start_index += 3
        f_out.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--crown_shape", help="Option: Ellipsoid, Cube, Cylinder, Cone", type=str, default="Ellipsoid")
    parser.add_argument('--crown_height', help="Unit: m", type=float, default=4)
    parser.add_argument("--crown_diameter_sn", help="Unit: m", type=float, default=2)
    parser.add_argument("--crown_diameter_ew", help="Unit: m", type=float, default=2)
    parser.add_argument("--trunk_height", help="Unit: m", type=float, default=3)
    parser.add_argument("--dbh", help="Diameter at breast height, Unit: m", type=float, default="0.2")
    parser.add_argument("--lad", help="Option:Spherical, Uniform, Planophile, Plagiophile, Erectophile, "
                                      "Extremophile", type=str, default="Spherical")
    parser.add_argument("--leaf_numbers", help="", type=int, default=10000)
    parser.add_argument("--leaf_shape", help="Option: Square, Disk", type=str, default="Square")
    parser.add_argument("--polygon_sides", help="Only for disk leaf", type=int, default=6)
    parser.add_argument("--single_leaf_area", help="Unit: Square meter", type=float, default=0.0025)
    parser.add_argument("--out_obj_path", help="", type=str, required=True)
    args = parser.parse_args()

    cg = CrownGenerator()
    cg.crown_shape = args.crown_shape
    cg.crown_height = args.crown_height
    cg.crown_diameter_SN = args.crown_diameter_sn
    cg.crown_diameter_EW = args.crown_diameter_ew
    if args.trunk_height > 0:
        cg.trunk_height = args.trunk_height
        cg.has_trunk = True
    else:
        cg.has_trunk = False
    cg.dbh = args.dbh
    cg.leaf_angle_dist = args.lad
    cg.num_of_leaves = args.leaf_numbers
    cg.leaf_shape = args.leaf_shape
    cg.leaf_num_triangles = args.polygon_sides
    cg.single_leaf_area = args.single_leaf_area
    cg.generate_crown(args.out_obj_path)