# coding: utf-8
import os
from LSBoundingBox import LSBoundingBox
from random import random
from math import cos, sin, floor, sqrt, pi, ceil


class OBJHelper(object):

    @staticmethod
    def get_obj_bound(obj_path):
        bound_box = LSBoundingBox()
        f = open(obj_path)
        for line in f:
            if line.startswith("v"):
                (x, y, z) = list(map(lambda xx: float(xx), line[1:].strip().split(" ")))
                if x < bound_box.minX:
                    bound_box.minX = x
                if y < bound_box.minY:
                    bound_box.minY = y
                if z < bound_box.minZ:
                    bound_box.minZ = z
                if x > bound_box.maxX:
                    bound_box.maxX = x
                if y > bound_box.maxY:
                    bound_box.maxY = y
                if z > bound_box.maxZ:
                    bound_box.maxZ = z
        f.close()
        return bound_box


    @staticmethod
    def seperate_obj(obj_path, translate_to_origin="no"):
        vertice = []
        facets = {}
        f = open(obj_path)
        curr_group = "group"
        for line in f:
            if line.startswith("v"):
                vertice.append(list(map(lambda x: float(x), line[1:].strip().split(" "))))
            if line.startswith("g"):
                curr_group = line[1:].strip()
                facets[curr_group] = []
            if line.startswith("f"):
                if curr_group not in facets:
                    facets[curr_group] = []
                else:
                    facets[curr_group].append(line)
        f.close()

        # translate
        if translate_to_origin == "xyz" or translate_to_origin == "xy":
            offsetx, offsety, offsetz = 0, 0, 0
            bound_box = LSBoundingBox()
            for (x, y, z) in vertice:
                if x < bound_box.minX:
                    bound_box.minX = x
                if y < bound_box.minY:
                    bound_box.minY = y
                if z < bound_box.minZ:
                    bound_box.minZ = z
                if x > bound_box.maxX:
                    bound_box.maxX = x
                if y > bound_box.maxY:
                    bound_box.maxY = y
                if z > bound_box.maxZ:
                    bound_box.maxZ = z
            offsetx = -0.5 * (bound_box.minX + bound_box.maxX)
            offsey = bound_box.minY
            offsetz = -0.5 * (bound_box.minZ + bound_box.maxZ)
            if translate_to_origin == "xy":
                offsey = 0
            for i in range(len(vertice)):
                vertice[i][0] = vertice[i][0] + offsetx
                vertice[i][1] = vertice[i][1] + offsety
                vertice[i][2] = vertice[i][2] + offsetz

        dirpath, tmpfilename = os.path.split(obj_path)
        shotname, extension = os.path.splitext(tmpfilename)
        group_paths = []
        for group_name in facets:
            new_facets_indice = [-1 for i in range(len(vertice))]
            new_num = 1
            group_obj_file_path = os.path.join(dirpath, shotname + "_" + group_name + ".obj")
            group_paths.append(group_obj_file_path)
            f = open(group_obj_file_path, "w")
            f.write("g " + group_name + "\n")
            group_facets = facets[group_name]
            for facetstr in group_facets:
                arr = facetstr[1:].strip().split(" ")
                indice = list(map(lambda x: int(x.split("/")[0]), arr))
                new_indice = [-1 for i in range(len(indice))]
                for i in range(len(indice)):
                    index = indice[i]
                    v = vertice[index-1]
                    if new_facets_indice[index-1] == -1:
                        f.write("v %f %f %f\n" % (v[0], v[1], v[2]))
                        new_facets_indice[index - 1] = new_num
                        new_indice[i] = new_num
                        new_num = new_num + 1
                    else:
                        new_indice[i] = new_facets_indice[index-1]
                f.write("f " + ' '.join(list(map(lambda x: str(x), new_indice))) + "\n")
            f.close()
        return group_paths


def euclidean_distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return sqrt(dx * dx + dy * dy)


class SamplingUtils:
    @staticmethod
    def poisson_disc_samples(width, height, r, k=5, distance=euclidean_distance, random=random):
        tau = 2 * pi
        cellsize = r / sqrt(2)

        grid_width = int(ceil(width / cellsize))
        grid_height = int(ceil(height / cellsize))
        grid = [None] * (grid_width * grid_height)

        def grid_coords(p):
            return int(floor(p[0] / cellsize)), int(floor(p[1] / cellsize))

        def fits(p, gx, gy):
            yrange = list(range(max(gy - 2, 0), min(gy + 3, grid_height)))
            for x in range(max(gx - 2, 0), min(gx + 3, grid_width)):
                for y in yrange:
                    g = grid[x + y * grid_width]
                    if g is None:
                        continue
                    if distance(p, g) <= r:
                        return False
            return True

        p = width * random(), height * random()
        queue = [p]
        grid_x, grid_y = grid_coords(p)
        grid[grid_x + grid_y * grid_width] = p

        while queue:
            qi = int(random() * len(queue))
            qx, qy = queue[qi]
            queue[qi] = queue[-1]
            queue.pop()
            for _ in range(k):
                alpha = tau * random()
                d = r * sqrt(3 * random() + 1)
                px = qx + d * cos(alpha)
                py = qy + d * sin(alpha)
                if not (0 <= px < width and 0 <= py < height):
                    continue
                p = (px, py)
                grid_x, grid_y = grid_coords(p)
                if not fits(p, grid_x, grid_y):
                    continue
                queue.append(p)
                grid[grid_x + grid_y * grid_width] = p
        return [p for p in grid if p is not None]


if __name__ == "__main__":
    print(OBJHelper.seperate_obj(r"D:\LESS\app\Database\3D_Objects\Trees\RAMI\ww_10.obj", translate_to_origin="xy"))

