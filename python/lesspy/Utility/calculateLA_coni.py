#coding:utf8

#统计单木的叶面积
import glob
import numpy as np
import math
files = glob.glob("*_leaf.obj")
leaffilepath = files[0]
f = open(leaffilepath,'r')
points_list=[]
isStart = False
for line in f:
	if line[0:2] == "v ":
		isStart = True
		arr = line.split(" ")
		point = np.array([float(arr[1]),float(arr[2]),float(arr[3])])
		points_list.append(point)
	elif isStart == True:
		break
#统计计算
totalsum = 0.0
for i in range(0,len(points_list),8):
	v12 = points_list[i+1]-points_list[i]
	v16 = points_list[i+5]-points_list[i]
	v15 = points_list[i+4]-points_list[i]
	v23 = points_list[i+2]-points_list[i+1]
	v27 = points_list[i+6]-points_list[i+1]
	v26 = points_list[i+5]-points_list[i+1]
	v34 = points_list[i+3]-points_list[i+2]
	v38 = points_list[i+7]-points_list[i+2]
	v37 = points_list[i+6]-points_list[i+2]

	cross126 = np.cross(v12,v16)
	s126 = math.sqrt(np.dot(cross126,cross126))/2

	cross165 = np.cross(v16,v15)
	s165 = math.sqrt(np.dot(cross165,cross165))/2

	cross237 = np.cross(v23,v27)
	s237 = math.sqrt(np.dot(cross237,cross237))/2

	cross276 = np.cross(v26,v27)
	s276 = math.sqrt(np.dot(cross276,cross276))/2

	cross348 = np.cross(v34,v38)
	s348 = math.sqrt(np.dot(cross348,cross348))/2

	cross387 = np.cross(v37,v38)
	s387 = math.sqrt(np.dot(cross387,cross387))/2



	singleArea = (s126+s165+s237+s276+s348+s387)/2
	totalsum = totalsum + singleArea
print(totalsum)