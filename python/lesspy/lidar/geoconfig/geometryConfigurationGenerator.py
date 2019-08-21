import numpy as np

class GeometryConfigurationGenerator:
	def __init__(self):
		self.output_file_path = ""
		self.results = []

	def run(self):
		pass

	def save(self):
		np.savetxt(self.output_file_path, np.array(self.results))
