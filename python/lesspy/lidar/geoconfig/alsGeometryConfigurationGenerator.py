import numpy as np

from geometryConfigurationGenerator import GeometryConfigurationGenerator


class AlsGeometryConfigurationGenerator(GeometryConfigurationGenerator):
    def __init__(self):
        self.altitude = 20
        self.azimuth = 0
        self.width = 40
        self.startX = 0
        self.startY = -20
        self.endX = 0
        self.endY = 20
        self.azimuthInterval = 0.5  # m
        self.rangeInterval = 0.4  # m

        self.results = []
        
    def run(self):

        l = np.sqrt((self.startX - self.endX)**2 + (self.startY - self.endY)**2)
        n = int(l / self.azimuthInterval)
        originX = np.linspace(self.startX, self.endX, n)
        originY = np.linspace(self.startY, self.endY, n)

        # originX = np.linspace(self.startX, self.endX, np.abs(self.startX - self.endX) / self.azimuthInterval / np.cos(slope))
        # originY = np.linspace(self.startY, self.endY, np.abs(self.startY - self.endY) / self.azimuthInterval / np.sin(slope))

        t = np.linspace(-self.width / 2, self.width / 2, int(self.width / self.rangeInterval))

        xs = self.startX - (self.endY - self.startY) / l * t
        ys = self.startY + (self.endX - self.startX) / l * t

        # get direction
        ds = np.array(list(map(lambda x, y: np.array([x - self.startX, y - self.startY, -self.altitude]), xs, ys)))
        # normalize
        ds = np.array(list(map(lambda d: d / np.linalg.norm(d), ds)))


        for ox, oy in zip(originX, originY):
            for d in ds:
                result = np.array([ox, self.altitude, oy, d[0], d[2], d[1]])
                self.results.append(result)












