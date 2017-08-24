import sys
# write imeadiately with flush
def log(*args):
    outstr = ""
    for i in args:
        outstr += str(i)
    print outstr
    sys.stdout.flush()