import os
import sys

class CSFtools:
    def __init__(self):
        self.parentPath = os.path.split(os.path.realpath(__file__))[0]

    def fullPath(self,script_name):
        return os.path.join(self.parentPath, script_name)

    def getPyExePath(self):
        return sys.executable

    def command(self,script):
        return self.getPyExePath()+ " " + self.fullPath(script)

    def parse_params(self, params):
        if len(params)%2 != 0:
            print "Parameter number is not correct."
        cmdstr = ""
        for i in range(0, len(params),2):
            param_name = params[i]
            param_value = params[i+1]
            cmdstr += param_name + " " + str(param_value) + " "
        return  cmdstr

    def csfground(self, params):
        cmdstr = self.parse_params(params)
        os.system(self.command("csfground.py " + cmdstr))

    def csfdem(self, params):
        cmdstr = self.parse_params(params)
        os.system(self.command("csfdem.py "+cmdstr))

    def csfnormalize(self, params):
        cmdstr = self.parse_params(params)
        os.system(self.command("csfnormalize.py " + cmdstr))

    def csfclassify(self, params):
        cmdstr = self.parse_params(params)
        os.system(self.command("csfclassify.py " + cmdstr))

    def csfcrown(self, params):
        cmdstr = self.parse_params(params)
        os.system(self.command("csfcrown.py " + cmdstr))

    def csflai(self, params):
        cmdstr = self.parse_params(params)
        os.system(self.command("csflai.py " + cmdstr))

    def csfheight(self, params):
        cmdstr = self.parse_params(params)
        os.system(self.command("csfheight.py " + cmdstr))