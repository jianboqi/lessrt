# coding: utf-8


# abstract class
class Element(object):
    def __init__(self):
        self._sim = None

    def set_sim(self, sim):
        self._sim = sim

    def get_sim(self):
        return self._sim