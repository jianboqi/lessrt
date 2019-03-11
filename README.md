Windows: [![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/github/jianboqi/lessrt?branch=master&svg=true)](https://ci.appveyor.com/project/jianboqi/lessrt)&nbsp;&nbsp;Linux: [![Build status](https://ci.appveyor.com/api/projects/status/so72g2kelkpwclhc?svg=true)](https://ci.appveyor.com/project/jianboqi/lessrt-ipr8k)

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

Please refer to http://lessrt.org/


## Todo

* [ ] Integrate a plane-parallel atmosphere model
  * [x] A plane-parallel medium has been implemented.
  * [ ] Need a atmosphere database which stores parameters of different type of atmosphere (maybe from Modtran)
* [x] Release under linux
  * [x] Find a solution to package all into a installer for different linux distributions.


## For developers
The whole model (including GUI) is written with C++, Python and JavaFX. JavaFX is responsible for GUI, and Python is used to develop all util tools (e.g., image format conversion), since it has numerious of  third-party libraries available. C++ is for writting calculating radiative transfer Core for high performance, and this part is mainly based on an open source renderer [Mitsuba](https://www.mitsuba-renderer.org/). Mitsuba provides an flexible framwork to develop customer plugins and do parallel computing.


