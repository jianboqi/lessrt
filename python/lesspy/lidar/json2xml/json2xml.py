from lidarConfigToXmlConvertor import LidarConfigToXmlConvertor


LIDAR_CONFIG_PATH = 'lidar.conf'
XML_FOLDER = '_scenefile/'
LIDAR_SCENE_PATH = XML_FOLDER + 'lidar_main.xml'

convertor = LidarConfigToXmlConvertor()
convertor.json_filename = LIDAR_CONFIG_PATH
convertor.xml_folder = XML_FOLDER
convertor.xml_filename = LIDAR_SCENE_PATH

convertor.convert()
convertor.save()

