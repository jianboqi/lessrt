import argparse

# x left y up
parser = argparse.ArgumentParser()
parser.add_argument("-shape", help="Is sequencer mode or not.")
parser.add_argument("-resolution",type=float, help="Is sequencer mode or not.")
parser.add_argument("-width",type=int, help="width.")
parser.add_argument("-height",type=int, help="height.")
parser.add_argument("-dist", help="Destination obj file.")
args = parser.parse_args()

if args.shape == "rectangle":
    resolution = args.resolution
    XSize = args.width
    YSize = args.height
    xExtend = XSize * resolution
    yExtend = YSize * resolution

    f = open(args.dist, 'w')
    for i in range(0, YSize + 1):
        for j in range(0, XSize + 1):
            x = " %.4f " % (0.5 * xExtend - j * resolution)
            z = " %.4f " % (0.5 * yExtend - i * resolution)
            if i < YSize and j < XSize:
                datavalue = " %.1f" % 0
            else:
                datavalue = " %.4f" % 0

            fstr = "v " + x + datavalue + z + "\n"
            f.write(fstr)

    for i in range(0, YSize):
        for j in range(0, XSize):
            p1 = i * (XSize + 1) + j + 1
            p2 = (i + 1) * (XSize + 1) + j + 1
            p3 = (i + 1) * (XSize + 1) + j + 1 + 1
            p4 = i * (XSize + 1) + j + 1 + 1
            fstr = "f " + str(p1) + " " + str(p2) + " " + str(p3) + " " + str(p4) + "\n"
            f.write(fstr)
    f.close()