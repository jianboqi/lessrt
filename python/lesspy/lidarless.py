import time
import sys
import os

from Loger import log
import subprocess
from session import *

def run_waveform():
	currdir = os.path.split(os.path.realpath(__file__))[0]
	rt_dir = os.path.join(currdir + '/bin/rt/' + current_rt_program)
	os.environ['PATH'] = rt_dir + os.pathsep + os.environ['PATH']

	excuable = 'lessrt'
	xml_filename = 'lidar_main.xml'

	scene_file_path = os.path.join(session.get_scenefile_path(), xml_filename)

	distFile = os.path.join(session.get_output_dir(), "waveform")

	command = [excuable, scene_file_path, '-o', distFile]
	log('INFO: ', command)
	subprocess.call(command)

def run_block(integrator_type):
	currdir = os.path.split(os.path.realpath(__file__))[0]
	rt_dir = os.path.join(currdir + '/bin/rt/' + current_rt_program)
	os.environ['PATH'] = rt_dir + os.pathsep + os.environ['PATH']

	excuable = 'lessrt'
	xml_filename = 'lidar_main.xml'

	scene_file_path = os.path.join(session.get_scenefile_path(), xml_filename)

	distFile = os.path.join(session.get_output_dir(), integrator_type)

	if not os.path.exists(distFile):
		os.makedirs(distFile)
		print('make output dir: ' + distFile)

	for i in os.listdir(os.path.join(session.get_scenefile_path(), 'lidarbatch')):
		# command = [excuable, '-D', 'batchFile=' + '"' + str(i) + '"', '-o', distFile, scene_file_path]
		command = 'lessrt -D integratorType="' + integrator_type + '" -D batchFile="' + i + '" -o ' + distFile + ' ' + scene_file_path
		log('INFO: ', command)
		subprocess.call(command)

if __name__ == '__main__':
	# run_waveform()
	if (len(sys.argv) < 2):
		print("Usage: %s <integrator type>", sys.argv[0], file=sys.stderr)
		sys.exit(-1)

	run_block(sys.argv[1])
