#coding:utf-8
import sys,getopt
from session import *
import os, shutil
from FileHelper import *
from Loger import log

def newproj():
    # create a indicator
    session.new_proj_indicator()
    if not os.path.exists(input_dir):
        os.mkdir(input_dir) # input
    os.mkdir(combine_file_path(input_dir, tmp_scene_file_dir)) # input/_scenefile
    # currdir = os.path.split(os.path.realpath(__file__))[0]
    # shutil.copy(combine_file_path(currdir,template_input), input_dir)
    os.mkdir(output_dir)
    log("Succeed: ", os.path.realpath(os.path.curdir))


#save current proj as new proj
def save_proj_as(oldprojectPath):
    session.new_proj_indicator()
    shutil.copytree(combine_file_path(oldprojectPath,input_dir),input_dir)
    os.mkdir(output_dir)
    log("Succeed save as: ", os.path.realpath(os.path.curdir))

# create sequencer
def new_sequencer(seq_name):
    seq_file = combine_file_path(os.getcwd(),seq_name+".conf")
    f = open(seq_file, 'w')
    f.write("{\n  \"seq1\" : {\n     \"obs_azimuth\" :\"LIST:0,30,60,90,120,150,180,210,240,270,300,330\"\n    },\n"
            "  \"seq2\" : {\n     \"obs_zenith\" :\"LIST:0,5,15,20,25,30,35,40,45,50,55,60,65,70\"\n    }\n}")
    f.close()
    log("Succeed.")

# clear input directores
def clear_input(type):
    if type=="forest":
        scene_dir = session.get_scenefile_path()
        if os.path.exists(combine_file_path(scene_dir,object_scene_file)):
            os.remove(combine_file_path(scene_dir,object_scene_file))
        for filename in os.listdir(scene_dir):
            filepath = combine_file_path(scene_dir,filename)
            if os.path.isfile(filepath):
                if filename.startswith(forest_scene_file)\
                        or (False and os.path.splitext(filename)[1] == ".serialized"):
                    os.remove(filepath)
    if type=="terrain":
        scene_dir = session.get_scenefile_path()
        terr_path = combine_file_path(scene_dir, terr_scene_file)
        if os.path.exists(terr_path):
            os.remove(terr_path)

def clear_scene_file_startswith(prifix):
    scene_dir = session.get_scenefile_path()
    for filename in os.listdir(scene_dir):
        filepath = os.path.join(scene_dir, filename)
        if filename.startswith(prifix) or os.path.splitext(filename)[1] == ".serialized":
            os.remove(filepath)

def clear_param_file_startswith(prifix):
    scene_dir = session.get_input_dir()
    for filename in os.listdir(scene_dir):
        filepath = os.path.join(scene_dir, filename)
        if filename.startswith(prifix):
            os.remove(filepath)