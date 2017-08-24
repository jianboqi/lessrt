from projManager import *

import sys,getopt
from toolUtility import *
opts,args = getopt.getopt(sys.argv[1:], "p:",["product="])

for op,value in opts:
    if op in ("-p", "--product"): # run all
        if value in ["BRF","brf"]:
            generate_brf()

