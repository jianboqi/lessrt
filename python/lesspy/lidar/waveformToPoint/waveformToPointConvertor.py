import numpy as np


class WaveformToPointConvertor:
	def __init__(self):
		self.accumulation_filename = ""
		# self.output_filename = ""

		self.dt_mes = 1e-9  # sec

		self.accumulation = None

		self.origin = np.zeros(3)
		self.direction = np.array([0, 1, 0])

		self.points = []

		self.pulse_index = 0

	def init(self):
		self.points = []


	def convert(self):
		distances = self.accumulation[:, 0]
		accumulated_weights = self.accumulation[:, 1:]
		pulse = self.get_pulse()

		waveform = self.convolve(accumulated_weights, pulse)
		local_maximums = self.find_local_maximum_2d(waveform)

		# get distance and weight of point
		records = []
		for d, ws, ms in zip(distances, accumulated_weights, local_maximums):
			# TODO: spectrum
			# ms.shape[0]
			for j in range(1):
				if ms[j]:
					record = [d / 2, ws[j], j, self.pulse_index]
					records.append(record)

		# get point
		for r in records:
			point = self.origin + self.direction * r[0]
			point = np.hstack([point, r[1:]])
			self.points.append(point)

	def load(self):
		self.accumulation = np.loadtxt(self.accumulation_filename)
		self.init()

	def save(self):
		pass

	def get_pulse(self):
		numberOfSigma = 3
		relativePower = 0.5
		durationAtRelativePower = 2.0  # half pulse duration at relative power [ns]
		sigmaPulse = durationAtRelativePower / np.sqrt(2.0) / np.sqrt(-np.log(relativePower))
		n = int(np.round((2 * numberOfSigma * sigmaPulse / (self.dt_mes * 1e9) - 1) / 2))
		x = np.linspace(-numberOfSigma * sigmaPulse, numberOfSigma * sigmaPulse, 2 * n + 1)
		pulse = np.exp(-0.5 * x * x / (sigmaPulse * sigmaPulse))
		pulse = pulse / np.sum(pulse)

		return pulse

	def convolve(self, f, p):
		r = np.zeros(f.shape)
		for i in range(f.shape[1]):
			r[:, i] = np.convolve(f[:, i], p, 'same')
		return r

	def find_local_maximum_2d(self, f):
		r = np.zeros(f.shape)
		for i in range(f.shape[1]):
			r[:, i] = self.find_local_maximum(f[:, i])
		return r

	def find_local_maximum(self, f):
		r = np.zeros(f.shape[0])
		if f.shape[0] < 3:
			return r
		for i in range(1, f.shape[0] - 1):
			r[i] = bool((f[i] > f[i - 1]) and (f[i] > f[i + 1]))
		return r
