from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

def beckmann_to_square(v: mitsuba.cuda_ad_spectral.Vector3f, alpha: mitsuba.Float) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_uniform_cone
    """
    ...

def bilinear_to_square(v00: mitsuba.Float, v10: mitsuba.Float, v01: mitsuba.Float, v11: mitsuba.Float, sample: mitsuba.cuda_ad_spectral.Point2f) -> Tuple[mitsuba.cuda_ad_spectral.Point2f, mitsuba.Float]:
    """
    Inverse of square_to_bilinear
    """
    ...

def cosine_hemisphere_to_square(v: mitsuba.cuda_ad_spectral.Vector3f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_cosine_hemisphere
    """
    ...

def interval_to_linear(v0: mitsuba.Float, v1: mitsuba.Float, sample: mitsuba.Float) -> mitsuba.Float:
    """
    Importance sample a linear interpolant
    
    Given a linear interpolant on the unit interval with boundary values
    ``v0``, ``v1`` (where ``v1`` is the value at ``x=1``), warp a
    uniformly distributed input sample ``sample`` so that the resulting
    probability distribution matches the linear interpolant.
    """
    ...

def interval_to_nonuniform_tent(a: mitsuba.Float, b: mitsuba.Float, c: mitsuba.Float, d: mitsuba.Float) -> mitsuba.Float:
    """
    Warp a uniformly distributed sample on [0, 1] to a nonuniform tent
    distribution with nodes ``{a, b, c}``
    """
    ...

def interval_to_tangent_direction(n: mitsuba.cuda_ad_spectral.Normal3f, sample: mitsuba.Float) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Warp a uniformly distributed sample on [0, 1] to a direction in the
    tangent plane
    """
    ...

def interval_to_tent(sample: mitsuba.Float) -> mitsuba.Float:
    """
    Warp a uniformly distributed sample on [0, 1] to a tent distribution
    """
    ...

def linear_to_interval(v0: mitsuba.Float, v1: mitsuba.Float, sample: mitsuba.Float) -> mitsuba.Float:
    """
    Inverse of interval_to_linear
    """
    ...

def square_to_beckmann(sample: mitsuba.cuda_ad_spectral.Point2f, alpha: mitsuba.Float) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Warp a uniformly distributed square sample to a Beckmann distribution
    """
    ...

def square_to_beckmann_pdf(v: mitsuba.cuda_ad_spectral.Vector3f, alpha: mitsuba.Float) -> mitsuba.Float:
    """
    Probability density of square_to_beckmann()
    """
    ...

def square_to_bilinear(v00: mitsuba.Float, v10: mitsuba.Float, v01: mitsuba.Float, v11: mitsuba.Float, sample: mitsuba.cuda_ad_spectral.Point2f) -> Tuple[mitsuba.cuda_ad_spectral.Point2f, mitsuba.Float]:
    """
    Importance sample a bilinear interpolant
    
    Given a bilinear interpolant on the unit square with corner values
    ``v00``, ``v10``, ``v01``, ``v11`` (where ``v10`` is the value at
    (x,y) == (0, 0)), warp a uniformly distributed input sample ``sample``
    so that the resulting probability distribution matches the linear
    interpolant.
    
    The implementation first samples the marginal distribution to obtain
    ``y``, followed by sampling the conditional distribution to obtain
    ``x``.
    
    Returns the sampled point and PDF for convenience.
    """
    ...

def square_to_bilinear_pdf(v00: mitsuba.Float, v10: mitsuba.Float, v01: mitsuba.Float, v11: mitsuba.Float, sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.Float: ...
def square_to_cosine_hemisphere(sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Sample a cosine-weighted vector on the unit hemisphere with respect to
    solid angles
    """
    ...

def square_to_cosine_hemisphere_pdf(v: mitsuba.cuda_ad_spectral.Vector3f) -> mitsuba.Float:
    """
    Density of square_to_cosine_hemisphere() with respect to solid angles
    """
    ...

def square_to_rough_fiber(sample: mitsuba.cuda_ad_spectral.Point3f, wi: mitsuba.cuda_ad_spectral.Vector3f, tangent: mitsuba.cuda_ad_spectral.Vector3f, kappa: mitsuba.Float) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Warp a uniformly distributed square sample to a rough fiber
    distribution
    """
    ...

def square_to_rough_fiber_pdf(v: mitsuba.cuda_ad_spectral.Vector3f, wi: mitsuba.cuda_ad_spectral.Vector3f, tangent: mitsuba.cuda_ad_spectral.Vector3f, kappa: mitsuba.Float) -> mitsuba.Float:
    """
    Probability density of square_to_rough_fiber()
    """
    ...

def square_to_std_normal(v: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Sample a point on a 2D standard normal distribution. Internally uses
    the Box-Muller transformation
    """
    ...

def square_to_std_normal_pdf(v: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.Float: ...
def square_to_tent(sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Warp a uniformly distributed square sample to a 2D tent distribution
    """
    ...

def square_to_tent_pdf(v: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.Float:
    """
    Density of square_to_tent per unit area.
    """
    ...

def square_to_uniform_cone(v: mitsuba.cuda_ad_spectral.Point2f, cos_cutoff: mitsuba.Float) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Uniformly sample a vector that lies within a given cone of angles
    around the Z axis
    
    Parameter ``cos_cutoff``:
        Cosine of the cutoff angle
    
    Parameter ``sample``:
        A uniformly distributed sample on :math:`[0,1]^2`
    """
    ...

def square_to_uniform_cone_pdf(v: mitsuba.cuda_ad_spectral.Vector3f, cos_cutoff: mitsuba.Float) -> mitsuba.Float:
    """
    Density of square_to_uniform_cone per unit area.
    
    Parameter ``cos_cutoff``:
        Cosine of the cutoff angle
    """
    ...

def square_to_uniform_disk(sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Uniformly sample a vector on a 2D disk
    """
    ...

def square_to_uniform_disk_concentric(sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Low-distortion concentric square to disk mapping by Peter Shirley
    """
    ...

def square_to_uniform_disk_concentric_pdf(p: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.Float:
    """
    Density of square_to_uniform_disk per unit area
    """
    ...

def square_to_uniform_disk_pdf(p: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.Float:
    """
    Density of square_to_uniform_disk per unit area
    """
    ...

def square_to_uniform_hemisphere(sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Uniformly sample a vector on the unit hemisphere with respect to solid
    angles
    """
    ...

def square_to_uniform_hemisphere_pdf(v: mitsuba.cuda_ad_spectral.Vector3f) -> mitsuba.Float:
    """
    Density of square_to_uniform_hemisphere() with respect to solid angles
    """
    ...

def square_to_uniform_sphere(sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Uniformly sample a vector on the unit sphere with respect to solid
    angles
    """
    ...

def square_to_uniform_sphere_pdf(v: mitsuba.cuda_ad_spectral.Vector3f) -> mitsuba.Float:
    """
    Density of square_to_uniform_sphere() with respect to solid angles
    """
    ...

def square_to_uniform_spherical_lune(sample: mitsuba.cuda_ad_spectral.Point2f, n1: mitsuba.cuda_ad_spectral.Normal3f, n2: mitsuba.cuda_ad_spectral.Normal3f) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Uniformly sample a direction in the two spherical lunes defined by the
    valid boundary directions of two touching faces defined by their
    normals ``n1`` and ``n2``.
    """
    ...

def square_to_uniform_spherical_lune_pdf(d: mitsuba.cuda_ad_spectral.Vector3f, n1: mitsuba.cuda_ad_spectral.Normal3f, n2: mitsuba.cuda_ad_spectral.Normal3f) -> mitsuba.Float:
    """
    Density of square_to_uniform_spherical_lune() w.r.t. solid angles
    """
    ...

def square_to_uniform_square_concentric(sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Low-distortion concentric square to square mapping (meant to be used
    in conjunction with another warping method that maps to the sphere)
    """
    ...

def square_to_uniform_triangle(sample: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Convert an uniformly distributed square sample into barycentric
    coordinates
    """
    ...

def square_to_uniform_triangle_pdf(p: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.Float:
    """
    Density of square_to_uniform_triangle per unit area.
    """
    ...

def square_to_von_mises_fisher(sample: mitsuba.cuda_ad_spectral.Point2f, kappa: mitsuba.Float) -> mitsuba.cuda_ad_spectral.Vector3f:
    """
    Warp a uniformly distributed square sample to a von Mises Fisher
    distribution
    """
    ...

def square_to_von_mises_fisher_pdf(v: mitsuba.cuda_ad_spectral.Vector3f, kappa: mitsuba.Float) -> mitsuba.Float:
    """
    Probability density of square_to_von_mises_fisher()
    """
    ...

def tangent_direction_to_interval(n: mitsuba.cuda_ad_spectral.Normal3f, dir: mitsuba.cuda_ad_spectral.Vector3f) -> mitsuba.Float:
    """
    Inverse of uniform_to_tangent_direction
    """
    ...

def tent_to_interval(value: mitsuba.Float) -> mitsuba.Float:
    """
    Warp a tent distribution to a uniformly distributed sample on [0, 1]
    """
    ...

def tent_to_square(value: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Warp a uniformly distributed square sample to a 2D tent distribution
    """
    ...

def uniform_cone_to_square(v: mitsuba.cuda_ad_spectral.Vector3f, cos_cutoff: mitsuba.Float) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_uniform_cone
    """
    ...

def uniform_disk_to_square(p: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_uniform_disk
    """
    ...

def uniform_disk_to_square_concentric(p: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_uniform_disk_concentric
    """
    ...

def uniform_hemisphere_to_square(v: mitsuba.cuda_ad_spectral.Vector3f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_uniform_hemisphere
    """
    ...

def uniform_sphere_to_square(sample: mitsuba.cuda_ad_spectral.Vector3f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_uniform_sphere
    """
    ...

def uniform_spherical_lune_to_square(d: mitsuba.cuda_ad_spectral.Vector3f, n1: mitsuba.cuda_ad_spectral.Normal3f, n2: mitsuba.cuda_ad_spectral.Normal3f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_uniform_spherical_lune
    """
    ...

def uniform_triangle_to_square(p: mitsuba.cuda_ad_spectral.Point2f) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping square_to_uniform_triangle
    """
    ...

def von_mises_fisher_to_square(v: mitsuba.cuda_ad_spectral.Vector3f, kappa: mitsuba.Float) -> mitsuba.cuda_ad_spectral.Point2f:
    """
    Inverse of the mapping von_mises_fisher_to_square
    """
    ...

