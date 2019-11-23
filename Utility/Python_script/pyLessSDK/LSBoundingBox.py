# coding: utf-8


class LSBoundingBox(object):
    def __init__(self):
        self.minX = float('Inf')
        self.minY = float('Inf')
        self.minZ = float('Inf')
        self.maxX = float('-Inf')
        self.maxY = float('-Inf')
        self.maxZ = float('-Inf')

        self.child_bounding_box = []

    def reset(self):
        self.minX = float('Inf')
        self.minY = float('Inf')
        self.minZ = float('Inf')
        self.maxX = float('-Inf')
        self.maxY = float('-Inf')
        self.maxZ = float('-Inf')

    def add_child(self, bound):
        self.child_bounding_box.append(bound)
        self.update_bounding_box()

    def update_bounding_box(self):
        self.reset()
        for i in range(len(self.child_bounding_box)):
            child = self.child_bounding_box[i]
            self.minX = min(self.minX, child.minX)
            self.minY = min(self.minY, child.minY)
            self.minZ = min(self.minZ, child.minZ)
            self.maxX = max(self.maxX, child.maxX)
            self.maxY = max(self.maxY, child.maxY)
            self.maxZ = max(self.maxZ, child.maxZ)

    def to_string(self):
        total_str = ""
        for i in range(len(self.child_bounding_box)):
            child_bound_box = self.child_bounding_box[i]
            total_str += str(child_bound_box.minX) + " "
            total_str += str(child_bound_box.minY) + " "
            total_str += str(child_bound_box.minZ) + " "
            total_str += str(child_bound_box.maxX) + " "
            total_str += str(child_bound_box.maxY) + " "
            total_str += str(child_bound_box.maxZ) + " "
        return total_str.strip()

    @staticmethod
    def merge(bound1, bound2):
        new_bound_box = LSBoundingBox()
        new_bound_box.minX = min(bound1.minX, bound2.minX)
        new_bound_box.minY = min(bound1.minY, bound2.minY)
        new_bound_box.minZ = min(bound1.minZ, bound2.minZ)
        new_bound_box.maxX = max(bound1.maxX, bound2.maxX)
        new_bound_box.maxY = max(bound1.maxY, bound2.maxY)
        new_bound_box.maxZ = max(bound1.maxZ, bound2.maxZ)
        return new_bound_box
