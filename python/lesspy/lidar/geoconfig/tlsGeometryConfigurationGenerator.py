import numpy as np

from geometryConfigurationGenerator import GeometryConfigurationGenerator


class TlsGeometryConfigurationGenerator(GeometryConfigurationGenerator):
	def __init__(self):
		self.x = 0  # m
		self.y = 0  # m
		self.z = 1  # m
		self.zenith = 64  # deg
		self.zenithRange = 60  # deg
		self.zenithInterval = 1  # deg
		self.azimuth = 135  # deg
		self.azimuthRange = 90  # deg
		self.azimuthInterval = 1  # deg

		self.results = []

	def run(self):
		zenithAngle = self.zenith - self.zenithRange / 2 + np.linspace(0, self.zenithRange, self.zenithRange / self.zenithInterval, False)
		azimuthAngle = self.azimuth - self.azimuthRange / 2 + np.linspace(0, self.azimuthRange, self.azimuthRange / self.azimuthInterval, False)
		zenithAngle = np.deg2rad(zenithAngle)
		azimuthAngle = np.deg2rad(azimuthAngle)
		
		for z in zenithAngle:
			for a in azimuthAngle:
				# u = np.sin(z) * np.cos(a)
				# v = np.sin(z) * np.sin(a)
				# w = np.cos(z)
				# result = np.array([self.x, self.y, self.z, u, v, w])
				u = np.sin(z) * np.sin(a)
				v = np.cos(z)
				w = np.sin(z) * np.cos(a)
				result = np.array([self.x, self.y, self.z, u, v, w])
				self.results.append(result)
