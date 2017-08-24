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
for i in range(0,len(points_list),4):
	v12 = points_list[i+1]-points_list[i]
	v13 = points_list[i+2]-points_list[i]
	v14 = points_list[i+3]-points_list[i]
	cross123 = np.cross(v12,v13)
	s123 = math.sqrt(np.dot(cross123,cross123))/float(2.0)
	cross134 = np.cross(v13,v14)
	s134 = math.sqrt(np.dot(cross134,cross134))/float(2.0)
	singleArea = s123+s134
	totalsum = totalsum + singleArea
print totalsum