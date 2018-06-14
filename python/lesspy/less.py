#coding:utf-8

#主要运行的命令
from projManager import newproj, new_sequencer, clear_input, save_proj_as
import os
import json
from SceneGenerate import SceneGenerate
from SceneParser import SceneParser
import Simulation
from session import session
from Viewer3d import threeDView
import argparse
from Loger import log
import time
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--new', help="Initialize a new simulation.", action='store_true')
parser.add_argument('--newseq', help="New sequence.")
parser.add_argument('-s','--saveas', help="save simulation to other places.")
parser.add_argument('-v', '--version', help="Version.", action='store_true')
parser.add_argument('-p', '--cores', help="Number of cores.", type=int, default=-1)
parser.add_argument('-r', '--run', help="Run a simulation. n: normal mode, s: sequencer mode, m: multiple scene at the"
                                        "same time.",
                    metavar=('mode', 'value'), nargs="*")
parser.add_argument('-g', '--generate', help="Generate scene file. a/all: generate all scene file."
                                             "t/terrain: generate terrain."
                                             "f/forest: generate forest."
                                             "v/view: generate view/sun geometry file.", metavar=('mode', 'value'),
                    nargs="*")
args = parser.parse_args()

# initialize new project
if args.new:
    newproj()

if args.run is not None:
    mode = args.run[0]
    session.checkproj()
    config_file_path = session.get_config_file()
    f = open(config_file_path, 'r')
    cfg = json.load(f)
    if mode == "n":
        Simulation.do_simulation_multi_spectral(args.cores)

if args.generate is not None:
    gvalue = args.generate[0]
    session.checkproj()
    cfgfile = session.get_config_file()
    # generate all
    if gvalue in ("a", "all"):
        clear_input("forest")
        clear_input("terrain")
        SceneGenerate.write_range_num_for_RT(cfgfile)
        SceneGenerate.terr_generate(cfgfile)
        SceneGenerate.generate_objects_file(cfgfile)
        SceneGenerate.forest_generate(cfgfile)
        sp = SceneParser()
        irrstr = sp.parse(cfgfile)
        sp.write_irr_to_file(irrstr)
    if gvalue in ("v", "view"):
        sp = SceneParser()
        irrstr = sp.parse(cfgfile)
        sp.write_irr_to_file(irrstr)


    # combine forest generation and terrain generation
    if gvalue in ("s", "scene"):
        SceneGenerate.write_range_num_for_RT(cfgfile)
        clear_input("terrain")
        SceneGenerate.terr_generate(cfgfile)
        clear_input("forest")
        SceneGenerate.generate_objects_file(cfgfile)
        SceneGenerate.forest_generate(cfgfile)
    if gvalue in ("t", 'terrain'):
        SceneGenerate.write_range_num_for_RT(cfgfile)
        clear_input("terrain")
        SceneGenerate.terr_generate(cfgfile)
    if gvalue in ("f", "forest"):
        SceneGenerate.write_range_num_for_RT(cfgfile)
        clear_input("forest")
        SceneGenerate.generate_objects_file(cfgfile)
        SceneGenerate.forest_generate(cfgfile)
    if gvalue in ("m", "m3d"):
        SceneGenerate.write_range_num_for_RT(cfgfile)
        clear_input("terrain")
        SceneGenerate.terr_generate(cfgfile)
        threeDView.forest_generate_according_tree_pos_file_for3d(cfgfile)

if args.version:
    log("LESS Simulation Program(V1.0), Developed by Jianbo Qi, Beijing Normal University.")

if args.newseq is not None:
    value = args.newseq
    session.checkproj()
    new_sequencer(value)

if args.saveas is not None:
    oldproj_path = args.saveas
    save_proj_as(oldproj_path)