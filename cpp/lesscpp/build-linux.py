import shutil,os
shutil.copy('config-linux.py','config.py')
os.system("scons -j6")