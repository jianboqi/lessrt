# coding: utf-8
# 生产Batch模拟文件夹
import os
from Loger import log
from Constant import batch_folder, batch_List_name, batch_conf, current_rt_program, main_scene_xml_file, output_format, \
    BATCH_INFO_FILE, irradiance_file
from projManager import clear_scene_file_startswith, clear_param_file_startswith
import json
import argparse
from session import session
import itertools
from collections import OrderedDict
import shutil
from SceneGenerate import SceneGenerate
from SceneParser import SceneParser
import time
from RasterHelper import RasterHelper
import numpy as np
import subprocess


class BatchGenAndRun:
    def __init__(self, cfgFile, seqPath):
        self._cfgFile = cfgFile
        self.seqPath = seqPath
        self.seq_name = os.path.splitext(os.path.basename(self.seqPath))[0]

        self.batchTypesMap = self.read_param_types()

        self.parameter_file_list = None

    def read_param_types(self):
        currdir = os.path.split(os.path.realpath(__file__))[0]
        f = open(os.path.join(currdir, batch_conf), 'r')
        tmp_config = json.load(f)
        mapDict = dict()
        self.readBatchTypesMap(tmp_config, mapDict)
        return mapDict

    def readBatchTypesMap(self, cfg, mapDict):
        for k in cfg:
            if isinstance(cfg[k], dict):
                self.readBatchTypesMap(cfg[k], mapDict)
            else:
                mapDict[k] = cfg[k]

    def getTypedValue(self, key, value):
        ftype = self.batchTypesMap[key]
        if ftype == "double":
            return float(value)
        elif ftype == "int":
            return int(value)
        return value

    def read_config_file(self):
        f = open(self._cfgFile, 'r')
        tmp_config = json.load(f)
        return tmp_config

    def writeKey(self, cfg, key, value):
        for k in cfg:
            if k == key:
                cfg[k] = value
                break
            else:
                if isinstance(cfg[k], dict):
                    self.writeKey(cfg[k], key, value)
        return cfg

    def writeCfgFile(self, cfg, cfgfile_path):
        with open(cfgfile_path, 'w') as f:
            f.write(json.dumps(cfg, sort_keys=True, indent=4, separators=(',', ': ')))

    def parse_seq(self):
        clear_param_file_startswith(self.seq_name)
        # write seq info
        finfo = open(os.path.join(session.get_output_dir(), self.seq_name + BATCH_INFO_FILE), 'w')

        params = []
        f = open(self.seqPath, 'r')

        seq = json.load(f, object_pairs_hook=OrderedDict)
        groupNames = []
        for groupName in seq:
            groupParam = dict()
            groupNames.append(groupName)
            for paramName in seq[groupName]:  # in each group
                paramValue = seq[groupName][paramName]
                if paramValue.startswith(batch_List_name):
                    arr = paramValue.split(":", 1)
                    arr = arr[1].split(",")
                    index = 0
                    for data in arr:
                        if index not in groupParam:
                            groupParam[index] = dict()
                        groupParam[index][paramName] = data
                        index += 1
            # print groupParam
            params.append(groupParam)

        # mixture between group
        indexList = []
        for i in range(0, len(params)):
            groupLen = len(params[i])
            indexList.append(range(0, groupLen))
        totalIndex = 0
        combinations = list(itertools.product(*indexList))
        for combination in combinations:
            if len(combination) > 0:
                groupIndex = 0
                seq_input_file = os.path.join(session.get_input_dir(), self.seq_name + "_" + str(totalIndex) + ".json")
                finfo.write(self.seq_name + "_" + str(totalIndex) + " ")
                cfg = self.read_config_file()
                totalIndex += 1
                for paramValueIndex in combination:
                    for paramName in params[groupIndex][paramValueIndex]:
                        paraVal = params[groupIndex][paramValueIndex][paramName]
                        self.writeKey(cfg, paramName, self.getTypedValue(paramName, paraVal))
                        finfo.write(paramName + " " + paraVal + " ")
                    groupIndex += 1
                # write batch config file
                self.writeCfgFile(cfg, seq_input_file)
                finfo.write("\n")
        finfo.close()

    def compare_fun(self, ele):
        return float(os.path.splitext(ele)[0].rsplit('_', 1)[1])

    def sort_list(self, lists):
        return sorted(lists, key=self.compare_fun)

    def readParameterFileList(self):
        if self.parameter_file_list == None:
            self.parameter_file_list = []
            for filename in os.listdir(session.get_input_dir()):
                if filename.startswith(self.seq_name):
                    self.parameter_file_list.append(filename)
            self.parameter_file_list = self.sort_list(self.parameter_file_list)

    def generate_xml_from_all_seq(self):
        clear_scene_file_startswith(self.seq_name)
        SceneGenerate.write_range_num_for_RT(self._cfgFile)
        self.readParameterFileList()
        for filename in self.parameter_file_list:
            tcfgfile = os.path.join(session.get_input_dir(), filename)
            prifix = os.path.splitext(filename)[0] + "_"
            SceneGenerate.terr_generate(tcfgfile, prifix)

        if (len(self.parameter_file_list) > 0):
            SceneGenerate.generate_objects_file(self._cfgFile, self.seq_name + "_")
            SceneGenerate.forest_generate(self._cfgFile, self.seq_name + "_")
        log("INFO: Generating view and illuminations.")

        # 输出irridiance
        fi = open(os.path.join(session.get_output_dir(), self.seq_name + "_" + irradiance_file), 'w')
        sp = SceneParser()
        for filename in self.parameter_file_list:
            tcfgfile = os.path.join(session.get_input_dir(), filename)
            prifix = os.path.splitext(filename)[0]
            irrstr = sp.parse(tcfgfile, prifix + "_", self.seq_name + "_")
            fi.write(prifix + "\n" + irrstr + "\n")
        log("INFO: view and illuminations generated.")
        fi.close()

    def convert_npy_to_envi(self, cfg, distFile, output_format):
        data = np.load(distFile + ".npy")
        bandlist = cfg["sensor"]["bands"].split(",")
        RasterHelper.saveToHdr_no_transform(data, distFile, bandlist, output_format)
        os.remove(distFile + ".npy")

    def run_seq(self):
        currdir = os.path.split(os.path.realpath(__file__))[0]
        os.environ['PATH'] = currdir + '/bin/rt/' + current_rt_program + os.pathsep + os.environ['PATH']
        self.readParameterFileList()
        for filename in self.parameter_file_list:
            log("INFO: " + filename)
            tcfgfile = os.path.join(session.get_input_dir(), filename)
            prifix = os.path.splitext(filename)[0]
            f = open(tcfgfile, 'r')
            cfg = json.load(f)
            excuable = "lessrt"
            scene_path = session.get_scenefile_path()

            distFile = os.path.join(session.get_output_dir(), prifix)
            # parameter = " -o " + distFile
            scene_file_path = os.path.join(scene_path, prifix + "_" + main_scene_xml_file)
            # cmd = excuable + " " + os.path.join(scene_path, prifix+"_"+main_scene_xml_file) + parameter
            # os.system(cmd)
            cores = cfg["Advanced"]["number_of_cores"]
            if cfg["Advanced"]["network_sim"]:
                subprocess.call(
                    [excuable, scene_file_path, "-o", distFile, "-p", str(cores), "-s",
                     os.path.join(session.get_input_dir(), "server.txt")])
            else:
                subprocess.call([excuable, scene_file_path, "-o", distFile, "-p", str(cores)])
                # os.system(excuable + " " + scene_file_path + " " + "-o " + distFile + " -p " + str(cores))
                time.sleep(0.5)
            if output_format not in ("npy", "NPY"):
                if os.path.exists(distFile + ".npy"):
                    self.convert_npy_to_envi(cfg, distFile, output_format)
                if os.path.exists(distFile + "_downwelling.npy"):
                    self.convert_npy_to_envi(cfg, distFile + "_downwelling", output_format)
                if os.path.exists(distFile + "_upwelling.npy"):
                    self.convert_npy_to_envi(cfg, distFile + "_upwelling", output_format)
                if os.path.exists(distFile+"_4Components.npy"):
                    data = np.load(distFile+"_4Components.npy")
                    dshape = data.shape
                    if len(dshape) == 3:
                        data = data[:,:,0]
                    bandlist = []
                    RasterHelper.saveToHdr_no_transform(data, distFile+"_4Components", bandlist, output_format)
                    os.remove(distFile+"_4Components.npy")

    def clear_json_file(self):
        self.readParameterFileList()
        for filename in self.parameter_file_list:
            filepath = os.path.join(session.get_input_dir(), filename)
            os.remove(filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--batchPath', help="Batch file Path.")
    args = parser.parse_args()

    if args.batchPath:
        session.checkproj()
        cfgfile = session.get_config_file()
        bt = BatchGenAndRun(cfgfile, args.batchPath)
        # bt.createFolder()
        log("INFO: Begin to run Batch.")
        bt.parse_seq()
        bt.generate_xml_from_all_seq()
        bt.run_seq()
        bt.clear_json_file()
