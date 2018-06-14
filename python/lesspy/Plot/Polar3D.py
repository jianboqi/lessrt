#coding: utf-8
from mpl_toolkits.mplot3d import Axes3D

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.mlab import griddata

def plot3D(zenithAngle, azimuthAngle, BRF):
    zenithAngle = np.radians(zenithAngle)
    azimuthAngle = np.radians(azimuthAngle)
    X, Y = BRF * np.sin(zenithAngle) * np.cos(azimuthAngle), BRF * np.sin(zenithAngle) * np.sin(azimuthAngle)
    Z = BRF * np.cos(zenithAngle)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(X, Y, Z, cmap=plt.cm.YlGnBu_r)
    plt.show()

def plot2D(alues, azimuths, zeniths, filled=True, colorbarlabel=""):
    azimuths = np.radians(azimuths)

    azimuthGrid = np.linspace(0, 2*np.pi, 100)
    zenithGrid = np.linspace(0, 90, 100)
    zi = griddata(azimuths, zeniths, alues, azimuthGrid, zenithGrid, interp='linear')
    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    # ax.set_theta_zero_location("N")
    # ax.set_theta_direction(-1)
    cax = ax.contourf(azimuthGrid, zenithGrid, zi, 20, cmap="jet")
    plt.show()


def plot_polar_contour(values, azimuths, zeniths, filled=True, colorbarlabel=""):
    """Plot a polar contour plot, with 0 degrees at the North.
    Arguments:
    * ``values`` -- A list (or other iterable - eg. a NumPy array) of the values to plot on the contour plot (the `z` values)
    * ``azimuths`` -- A list of azimuths (in degrees)
    * ``zeniths`` -- A list of zeniths (that is, radii)
    * ``filled`` -- (Optional) Whether to plot a filled contour plot, or just the contours (defaults to filled)
    * ``yaxislabel`` -- (Optional) The label to use for the colorbar
    * ``colorbarlabel`` -- (Optional) The label to use on the color bar shown with the plot
    The shapes of these lists are important, and are designed for a particular use case (but should be more generally useful).
    The values list should be `len(azimuths) * len(zeniths)` long with data for the first azimuth for all the zeniths, then
    the second azimuth for all the zeniths etc.
    This is designed to work nicely with data that is produced using a loop as follows::
      values = []
      for azimuth in azimuths:
        for zenith in zeniths:
          # Do something and get a result
          values.append(result)
    After that code the azimuths, zeniths and values lists will be ready to be passed into this function.
    """


    theta = np.radians(azimuths)
    zeniths = np.array(zeniths)

    values = np.array(values)
    values = values.reshape(len(azimuths), len(zeniths))

    r, theta = np.meshgrid(zeniths, np.radians(azimuths))
    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    if filled:
        cax = ax.contourf(theta, r, values, 30)
    else:
        cax = ax.contour(theta, r, values, 30)
    cb = fig.colorbar(cax)
    cb.set_label(colorbarlabel)

    return fig, ax, cax



dataPath = r"E:\Coding\Mitsuba\simulations\ForwardPathTracing\forwarPathtracingTest\Parameters\_scenefile\main_BRF.txt"

f = open(dataPath)

index = 0
zenithAngle=[]
azimuthAngle=[]
BRF = []
for line in f:
    if index > 0:
        arr = line.strip().replace("\n","").split(" ")
        zenithAngle.append(float(arr[0]))
        azimuthAngle.append(float(arr[1]))
        BRF.append(float(arr[3]))
    index += 1

zenithAngle = np.array(zenithAngle)
azimuthAngle = np.array(azimuthAngle)
BRF = np.array(BRF)

plot3D(zenithAngle,azimuthAngle, BRF)
plot2D(BRF, azimuthAngle, zenithAngle)
