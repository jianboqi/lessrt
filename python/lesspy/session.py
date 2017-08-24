#coding:utf-8

from Constant import *
import json
from FileHelper import *
from Loger import log
class session:

    # check current dir is a valid project or not
    @staticmethod
    def checkproj():
        curr_dir = os.getcwdu()
        check_file = curr_dir + os.sep + less_identifier
        if not os.path.exists(check_file):
            log("This directory is not a valid simulation")
            sys.exit(0)


    @staticmethod
    def new_proj_indicator():
        curr_dir = os.getcwdu()
        check_file = curr_dir + os.sep + less_identifier
        if os.path.exists(check_file):
            log("This directory is already a less simulation")
            sys.exit(0)
        else:
            os.mkdir(check_file)

    #

    @staticmethod
    def is_forest_generated():
        scene_dir = session.get_scenefile_path()
        for filename in os.listdir(scene_dir):
            filepath = combine_file_path_multi(scene_dir,filename)
            if os.path.isfile(filepath):
                if filename.startswith(forest_scene_file):
                    return True
        return False

    @staticmethod
    def get_scenefile_path():
        curr_dir = os.getcwdu()
        check_file = os.path.join(curr_dir, input_dir, tmp_scene_file_dir)
        return check_file

    @staticmethod
    def get_scenefile_path_according_to_basedir(project_dir):
        scene_file = os.path.join(project_dir, input_dir, tmp_scene_file_dir)
        return scene_file

    @staticmethod
    def get_input_dir():
        curr_dir = os.getcwdu()
        check_file = combine_file_path(curr_dir, input_dir)
        return check_file

    @staticmethod
    def get_output_dir():
        curr_dir = os.getcwdu()
        output_dir1 = combine_file_path(curr_dir, output_dir)
        return output_dir1


    @staticmethod
    def get_config_file():
        curr_dir = os.getcwdu()
        config_file_path = combine_file_path_multi(curr_dir, input_dir, config_file)
        return config_file_path

    # # 读取状态信息
    # @staticmethod
    # def getState(statename):
    #     f = open(session_file, 'r')
    #     session = json.load(f)
    #     return session[statename]
    #
    # @staticmethod
    # def setState(statename,value):
    #     f = open(session_file, 'r')
    #     session = json.load(f)
    #     session[statename] = value
    #     with open(session_file, 'w') as f:
    #         json.dump(session, f)




