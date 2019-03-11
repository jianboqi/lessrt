import shutil,os
if os.path.exists('config.py'):
	os.remove('config.py')
shutil.copy('config-linux.py','config.py')
os.system("scons -j6")

# build cpp and copy the file to python folder
print "copying files..."
from distutils.dir_util import copy_tree
if not os.path.exists('../../python/lesspy/bin/rt/lessrt'):
	os.makedirs('../../python/lesspy/bin/rt/lessrt')
copy_tree("dist-linux","../../python/lesspy/bin/rt/lessrt")

# copy libs of linux to the folder lessrt
copy_tree("../../Utility/libs_linux/ubuntu16_04","../../python/lesspy/bin/rt/lessrt")
print "finished."
