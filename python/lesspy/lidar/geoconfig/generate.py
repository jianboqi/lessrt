import os
import numpy as np
import json
import generateTlsGeometryConfiguration
import generateAlsGeometryConfiguration

print('Start')

LIDAR_CONFIG_PATH = 'lidar.conf'

c = {}
with open(LIDAR_CONFIG_PATH, 'r') as f:
    c = json.load(f)

platform = c['platform']

if platform['type'] == 'TLS':
    generateTlsGeometryConfiguration.generate(platform)
elif platform['type'] == 'ALS':
	generateAlsGeometryConfiguration.generate(platform)

if not os.path.exists('_scenefile/lidarbatch/'):
    os.makedirs('_scenefile/lidarbatch/')
    print('make dir `_scenefile/lidarbatch/`')


# split lidarbatch
N = 2000000

d = np.loadtxt('_scenefile/lidarbatch.txt')

l = 0
i = 0
while l < d.shape[0]:
    r = np.min([l + N, d.shape[0]])
    b = d[l : r, :]
    np.savetxt('_scenefile/lidarbatch/' + str(i), b)
    i += 1
    l += N

print('End')
