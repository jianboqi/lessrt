Windows: [![Build status](https://ci.appveyor.com/api/projects/status/alfpva8jgm657835?svg=true)](https://ci.appveyor.com/project/jianboqi/lessrt)
&nbsp;&nbsp;Linux: [![Build status](https://ci.appveyor.com/api/projects/status/so72g2kelkpwclhc?svg=true)](https://ci.appveyor.com/project/jianboqi/lessrt-ipr8k)

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

## Papers
If you use this model, please cite:

Qi, J., Xie, D., Yin, T., Yan, G., Gastellu-Etchegorry, J.-P., Li, L., Zhang, W., Mu, X., Norford, L.K., 2019. **LESS: LargE-Scale remote sensing data and image simulation framework over heterogeneous 3D scenes.** Remote Sensing of Environment. 221, 695–706. (https://www.sciencedirect.com/science/article/pii/S0034425718305443)


