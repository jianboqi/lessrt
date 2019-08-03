class JsonToXmlConvertor:
	def __init__(self):
		self.json_filename = ''
		self.xml_folder = ''
		self.xml_filename = ''
		self.doc = None

	def convert(self):
		pass

	def save(self):
		with open(self.xml_filename, 'w', encoding='utf-8') as fh:
			self.doc.writexml(fh,indent='', addindent='\t', newl='\n', encoding='utf-8')

		# xm = self.doc.toprettyxml()
		# with open(self.xml_filename, 'w') as f:
		# 	f.write(xm)
