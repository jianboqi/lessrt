# compile py to pyc for lessgui

import glob, os, shutil

#delete pyc first
files = glob.iglob(os.path.join("./", "*.pyc"))
for file in files:
    if os.path.isfile(file):
        os.remove(file)

os.system("python -m compileall .")

# copy to
files = glob.iglob(os.path.join("./", "*.pyc"))
for file in files:
    if os.path.isfile(file):
        shutil.copy2(file, "../LessPyc")

if os.path.exists("../LessPyc/bin"):
    shutil.rmtree("../LessPyc/bin")
    shutil.copytree("bin","../LessPyc/bin")
if os.path.exists("../LessPyc/SpectralDB"):
    shutil.rmtree("../LessPyc/SpectralDB")
    shutil.copytree("SpectralDB","../LessPyc/SpectralDB")
if os.path.exists("../LessPyc/Utility"):
    shutil.rmtree("../LessPyc/Utility")
    shutil.copytree("Utility","../LessPyc/Utility")
else:
    shutil.copytree("Utility", "../LessPyc/Utility")
shutil.copy("const.conf","../LessPyc")
shutil.copy("default.conf","../LessPyc")
shutil.copy("batch.conf","../LessPyc")