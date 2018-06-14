import sys
# write imeadiately with flush
def log(*args):
    outstr = ""
    for i in args:
        outstr += str(i)
    # print(outstr.encode("utf-8").decode("gbk"))
    print(outstr)
    sys.stdout.flush()