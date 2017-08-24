from session import *
import shutil
# combine file path for two parameters
def combine_file_path1(p1, p2):
    if p1[-1] != os.path.sep and p1[-1] != "/":
        p1 += os.path.sep
    return p1+p2

def combine_file_path(p1, p2):
    return os.path.join(p1, p2)

# combine file paths for several parameters
def combine_file_path_multi(*args):
    param_len = len(args)
    final_path = args[0]
    for i in range(1, param_len):
        final_path = combine_file_path(final_path, args[i])
    return final_path

def getFileList(dirpath, prefix):
    if not os.path.exists(dirpath):
        log("directory does not exists.")
    else:
        filelist = []
        for filename in os.listdir(dirpath):
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                if filename.startswith(prefix):
                    filelist.append(filename)
        return filelist
