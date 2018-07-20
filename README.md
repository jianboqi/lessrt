[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/k7j5d9v81qjm69j6?svg=true)](https://ci.appveyor.com/project/jianboqi/lessrt)

LESS is a 3D radiative transfer model which can simulate large-scale spectral images and remote sensing data.

![Image of LESS example](http://jianboqi.github.io/img/lessExample1.jpg)

## Features

* Simulating spectral images
* Simulating perspetive and fisheye camera images
* Simulating multiangle BRF (bidirectinal reflectance factor)
* Albedo simulation
* Thermal infrared image simulation
* Upwelling and downwelling radiation simulation over rugged terrains with realistic trees
* ...

## Usage
### Windows:

Currently, a windows installer are provided: http://lessrt.org/download-less/

### Linux

All the components (GUI, Rdiative transfer core) have been sucessfully compiled under linux (ubuntu, centos),
but the packaging into a simple installer is not finished. We are working on that.

## Todo

* [ ] Integrate a plane-parallel atmosphere model
  * [x] A plane-parallel medium has been implemented.
  * [ ] Need a atmosphere database which stores parameters of different type of atmosphere (maybe from Modtran)
* [ ] Release under linux
  * [ ] Find a solution to package all into a installer for different linux distributions.


## For developers
The whole model (including GUI) is written with C++, Python and JavaFX. JavaFX is responsible for GUI, and Python is used to develop all util tools (e.g., image format conversion), since it has numerious of  third-party libraries available. C++ is for writting calculating radiative transfer Core for high performance, and this part is mainly based on an open source renderer [Mitsuba](https://www.mitsuba-renderer.org/). Mitsuba provides an flexible framwork to develop customer plugins and do parallel computing.

The basic relationship between all these components (GUI, Radiative Transfer Core and tools) are as follow:

