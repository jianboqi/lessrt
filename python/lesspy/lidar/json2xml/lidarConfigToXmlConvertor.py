import os

from jsonToXmlConvertor import JsonToXmlConvertor
from xml.dom import minidom
import json


MITSUBA_VERSION = '0.5.0'
TYPE = '$integratorType'


class LidarConfigToXmlConvertor(JsonToXmlConvertor):

	def create_node(self, tag, **kwargs):
		doc = minidom.Document()
		node = doc.createElement(tag)
		for k in kwargs:
			node.setAttribute(k, kwargs[k])
		return node

	def create_name_value_node(self, label, name, value):
		doc = minidom.Document()
		node = doc.createElement(label)
		node.setAttribute('name', name)
		node.setAttribute('value', value)
		return node	

	def get_scene_node(self):
		doc = minidom.Document()
		node = doc.createElement('scene')
		node.setAttribute('version', MITSUBA_VERSION)
		return node

	def get_integrator_node(self):
		doc = minidom.Document()
		node = doc.createElement('integrator')
		node.setAttribute('type', TYPE)
		return node

	def add_node_to_integrator(self, integrator):
		c = {}	    
		with open(self.json_filename, 'r') as f:
			c = json.load(f)

		beam = c['beam']
		device = c['device']
		platform = c['platform']

		# integrator.setAttribute('type', platform['type'].replace(' ', ''))
		integrator.appendChild(self.create_name_value_node('string', 'type', platform['type']))
		integrator.appendChild(self.create_name_value_node('string', 'batchFile', '$batchFile'))

		# beam
		beam_int_attributes = ['axialDivision', 'maxOrder']
		for k in beam_int_attributes:
			integrator.appendChild(self.create_name_value_node('integer', k, str(beam[k])))

		# device
		device_float_attributes = ['fractionAtRadius', 'footprintHalfAngle', 'halfFov', 'pulseEnergy', 'acquisitionPeriod', 'sensorArea', 'halfPulseDurationAtHalfPeak', 'halfDurationNumberOfSigma']
		for k in device_float_attributes:
			integrator.appendChild(self.create_name_value_node('float', k, str(device[k])))

		# platform
		mono_pulse_float_attributes = ['x', 'y', 'z', 'zenith', 'azimuth', 'minRange', 'maxRange']
		als_float_attributes = ['altitude', 'platformAzimuth', 'swathWidth', 'startX', 'startY', 'endX', 'endY', 'azimuthResolution', 'rangeResolution', 'savedUpper', 'savedLower']
		tls_float_attributes = ['x', 'y', 'z', 'centerZenith', 'deltaZenith', 'resolutionZenith', 'centerAzimuth', 'deltaAzimuth', 'resolutionAzimuth', 'minRange', 'maxRange']
		mls_float_attributes = ['x', 'y', 'z', 'axisZenith', 'axisAzimuth', 'resolutionZenith', 'resolutionAzimuth', 'minRange', 'maxRange']
		mls_int_attributes = ['numberOfLines']

		if platform['type'] == 'Mono Pulse':
			for k in mono_pulse_float_attributes:
				integrator.appendChild(self.create_name_value_node('float', k, str(platform[k])))
		elif platform['type'] == 'ALS':
			for k in als_float_attributes:
				integrator.appendChild(self.create_name_value_node('float', k, str(platform[k])))

			integrator.appendChild(self.create_name_value_node('float', 'minRange', str(float(platform['altitude']) - float(platform['savedUpper']))))
			integrator.appendChild(self.create_name_value_node('float', 'maxRange', str(float(platform['altitude']) + float(platform['savedLower']))))

		elif platform['type'] == 'TLS':
			for k in tls_float_attributes:
				integrator.appendChild(self.create_name_value_node('float', k, str(platform[k])))
		elif platform['type'] == 'MLS':
			for k in mls_float_attributes:
				integrator.appendChild(self.create_name_value_node('float', k, str(platform[k])))
			for k in mls_int_attributes:
				integrator.appendChild(self.create_name_value_node('float', k, str(platform[k])))

	def convert(self):
		self.doc = minidom.Document()
		# add scene node
		scene = self.get_scene_node()
		self.doc.appendChild(scene)
		# add integrator node
		integrator = self.get_integrator_node()
		scene.appendChild(integrator)
		# add sub node and attribute
		self.add_node_to_integrator(integrator)
		# include
		scene.appendChild(self.create_node('include', filename='terrain.xml'))
		scene.appendChild(self.create_node('include', filename='object.xml'))
		# 		# include forest
		forests = self.get_file_list('forest')
		for f in forests:
			scene.appendChild(self.create_node('include', filename=f))

	def get_file_list(self, substring):
		if not os.path.exists(self.xml_folder):
			return []
		else:
			file_list = []
			for filename in os.listdir(self.xml_folder):
				file_path = os.path.join(self.xml_folder, filename)
				if os.path.isfile(file_path):
					if filename.find(substring) != -1:
						print(substring)
						file_list.append(filename)
			return file_list
