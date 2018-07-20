# compile py to pyc for lessgui

import glob, os, shutil


#delete pyc first
files = glob.iglob(os.path.join("./", "*.pyc"))
for file in files:
    if os.path.isfile(file):
        os.remove(file)

# os.system(r"d:\Python36\python -m compileall -b .")


# copy to
files = glob.iglob(os.path.join("./", "*.py"))
for file in files:
    if os.path.isfile(file):
        shutil.copy2(file, "../../build/LessPy")

if os.path.exists("../../build/LessPy/bin"):
    shutil.rmtree("../../build/LessPy/bin")
shutil.copytree("bin","../../build/LessPy/bin")
if os.path.exists("../../build/LessPy/SpectralDB"):
    shutil.rmtree("../../build/LessPy/SpectralDB")
shutil.copytree("SpectralDB","../../build/LessPy/SpectralDB")
if os.path.exists("../../build/LessPy/Utility"):
    shutil.rmtree("../../build/LessPy/Utility")
shutil.copytree("Utility","../../build/LessPy/Utility")
shutil.copy("const.conf","../../build/LessPy")
shutil.copy("default.conf","../../build/LessPy")
shutil.copy("batch.conf","../../build/LessPy")