import shutil,os
if os.path.exits('config.py'):
	os.remove('config.py')
shutil.copy('config-win.py','config.py')
os.system("scons -j6")
print "copying files..."
from distutils.dir_util import copy_tree
copy_tree("dist","../../python/lesspy/bin/rt/lessrt")
print "finished."

