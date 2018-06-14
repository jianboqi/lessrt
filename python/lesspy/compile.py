# compile py to pyc for lessgui

import glob, os, shutil


#delete pyc first
files = glob.iglob(os.path.join("./", "*.pyc"))
for file in files:
    if os.path.isfile(file):
        os.remove(file)

os.system(r"d:\Python36\python -m compileall -b .")
# compileall.compile_dir("./")

# copy to
files = glob.iglob(os.path.join("./", "*.pyc"))
for file in files:
    if os.path.isfile(file):
        shutil.copy2(file, "../../build/LessPyc")

if os.path.exists("../../build/LessPyc/bin"):
    shutil.rmtree("../../build/LessPyc/bin")
shutil.copytree("bin","../../build/LessPyc/bin")
if os.path.exists("../../build/LessPyc/SpectralDB"):
    shutil.rmtree("../../build/LessPyc/SpectralDB")
shutil.copytree("SpectralDB","../../build/LessPyc/SpectralDB")
if os.path.exists("../../build/LessPyc/Utility"):
    shutil.rmtree("../../build/LessPyc/Utility")
shutil.copytree("Utility","../../build/LessPyc/Utility")
shutil.copy("const.conf","../../build/LessPyc")
shutil.copy("default.conf","../../build/LessPyc")
shutil.copy("batch.conf","../../build/LessPyc")