import shutil
import os

if os.path.exists("dist"):
    shutil.rmtree("dist")
os.system("pyinstaller less.py")
shutil.copytree("template","dist/less/template")
shutil.copytree("bin","dist/less/bin")
shutil.copytree("SpectralDB","dist/less/SpectralDB")
shutil.copy("const.conf","dist/less/")
shutil.copy("Imath.pyc", "dist/less/")
