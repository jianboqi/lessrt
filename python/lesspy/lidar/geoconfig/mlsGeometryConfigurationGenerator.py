import numpy as np

from geometryConfigurationGenerator import GeometryConfigurationGenerator
from tlsGeometryConfigurationGenerator import TlsGeometryConfigurationGenerator

class MlsGeometryConfigurationGenerator(GeometryConfigurationGenerator):
	def __init__(self):
		self.x = 15
		self.y = 2
		self.z = 15
		self.zenith = 0  # axis zenith
		self.azimuth = 0  # axis azimuth

		self.n = 1  # number of lines

		self.zenithInterval = 1
		self.azimuthInterval = 1

	def run(self):
		tls = TlsGeometryConfigurationGenerator()
		

	def rotate():
		pass

