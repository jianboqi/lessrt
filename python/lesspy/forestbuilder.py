#coding:utf-8

#主要运行的命令
#from projManager import *

import sys,getopt
#from SceneGenerate import *
import random

opts,args = getopt.getopt(sys.argv[1:], "i:n:x:a:y:z:",["input=","number=","xstart=","xend=","ystart=","yend="])

for op,value in opts:
    if op in ("-i", "--input"): # run all
        inputfile = value
    if op in ("-x","--xstart"):
        xstart = float(value)
    if op in ("-a", "--xend"):
        xend = float(value)
    if op in ("-y", "--ystart"):
        ystart = float(value)
    if op in ("-z", "--yend"):
        yend = float(value)
    if op in ("-n", "--number"):
        num = int(value)
#根据tree_pos_file 定义的单木模型，随机生成树的位置
f = open(inputfile,'r')
objlist=[]
objtext=[]
idx=0
for line in f:
    if line.startswith("o"):
        idx += 1
        objtext.append(line)
f.close()
f = open(inputfile,'w')
for i in range(0,len(objtext)):
    f.write(objtext[i]+"\n")
treenum = idx-1
for i in range(0,num):
    x = random.uniform(xstart,xend)
    y = random.uniform(ystart,yend)
    treeId = random.randint(0,treenum)
    treestr = "i " + "%.4f"%x + " %.4f "%y + str(treeId)
    f.write(treestr + "\n")
f.close()

