import sys
import os

import numpy as np

from waveformToPointConvertor import WaveformToPointConvertor

def toPoint(batch_file_path, record_file_path, output_file_path, number_of_bins):
	batch = np.loadtxt(batch_file_path)
	records = np.loadtxt(record_file_path)
	points = []
	convertor = WaveformToPointConvertor()

	if records.shape[0] % number_of_bins != 0:
		print('record incomplete % != 0 ' + batch_file_path)
		return

	for i in range(batch.shape[0]):
		convertor.init()
		
		# convertor.accumulation_filename = record_file_folder + str(i) + '.txt'
		convertor.origin = batch[i, 0:3]
		convertor.direction = batch[i, 3:6]

		convertor.pulse_index = i

		# convertor.load()
		if (i + 1) * number_of_bins > records.shape[0]:
			print('record incomplete ' + batch_file_path)
			return
		convertor.accumulation = records[i * number_of_bins : (i + 1) * number_of_bins, :]

		convertor.convert()
		points += convertor.points

	points = np.array(points)
	np.savetxt(output_file_path, points)

if __name__ == '__main__':
	number_of_bins = int(sys.argv[1])

	if not os.path.exists('Results/cloud/'):
		os.makedirs('Results/cloud/')
		print('make dir `Results/cloud/`')

	for i in os.listdir(os.path.join('Parameters/_scenefile/lidarbatch/')):
		print(i)
		if os.path.exists('Results/waveform/' + i + ".txt"):
			toPoint('Parameters/_scenefile/lidarbatch/' + i, 'Results/waveform/' + i + ".txt", 'Results/cloud/' + i + '.txt', number_of_bins)
