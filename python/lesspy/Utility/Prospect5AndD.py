
import argparse
from pyPro4Sail import ProspectD
import math

parser = argparse.ArgumentParser()
parser.add_argument("--wl", help="wavelength string",type=str)
parser.add_argument('--isProspect5',action='store_true', help='is Prospect5?')
parser.add_argument("--N", help="N.",type=float)
parser.add_argument("--Car", help="Car.",type=float)
parser.add_argument("--BP", help="BP.",type=float)
parser.add_argument("--Cm", help="Cm.",type=float)
parser.add_argument("--Cab", help="Cab.",type=float)
parser.add_argument("--Anth", help="Anth.",type=float)
parser.add_argument("--Cw", help="Cw.",type=float)
args = parser.parse_args()

wl = args.wl # nm
isProspect5 = args.isProspect5
N = args.N
Car = args.Car
BP = args.BP
Cm = args.Cm
Cab = args.Cab
Anth = args.Anth
Cw = args.Cw

if isProspect5:
    ws, rs, ts = ProspectD.Prospect5(N,Cab,Car,BP, Cw, Cm)
else:
    ws, rs, ts = ProspectD.ProspectD(N,Cab,Car,BP,Cw,Cm,Anth)

arr = wl.split(",")
reflectances = []
transmittances = []
r,t = 0,0
for wavelengthStr in arr:
    wavelength = float(wavelengthStr)
    # interpolation
    if wavelength <= 400:
        r, t = rs[0], ts[0]
    elif wavelength >= 2500:
        r, t = rs[2500], ts[2500]
    else:
        wavelength_int = math.floor(wavelength)
        extra = wavelength - wavelength_int
        left_r = rs[wavelength_int-400]
        right_r = rs[wavelength_int-400+1]
        k = (right_r-left_r)
        r = k*extra+left_r

        left_t = ts[wavelength_int-400]
        right_t = ts[wavelength_int-400+1]
        k = right_t-left_t
        t = k*extra+left_t

    reflectances.append("%.4f"%r)
    transmittances.append("%.4f"%t)
print("PROSPECT5D:"+','.join(reflectances)+";"+','.join(transmittances))