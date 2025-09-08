from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

def BSDFAdapter(bsdf_type, extra, wi=[0, 0, 1], uv=[0.5, 0.5], ctx=None):
    """
    
    Adapter to test BSDF sampling using the Chi^2 test.
    
    Parameter ``bsdf_type`` (string):
    Name of the BSDF plugin to instantiate.
    
    Parameter ``extra`` (string|dict):
    Additional XML used to specify the BSDF's parameters, or a Python
    dictionary as used by the ``load_dict`` routine.
    
    Parameter ``wi`` (array(3,)):
    Incoming direction, in local coordinates.
    
    """
    ...

class ChiSquareTest:
    """
        Implements Pearson's chi-square test for goodness of fit of a distribution
        to a known reference distribution.
    
        The implementation here specifically compares a Monte Carlo sampling
        strategy on a 2D (or lower dimensional) space against a reference
        distribution obtained by numerically integrating a probability density
        function over grid in the distribution's parameter domain.
    
        Parameter ``domain`` (object):
           An implementation of the domain interface (``SphericalDomain``, etc.),
           which transforms between the parameter and target domain of the
           distribution
    
        Parameter ``sample_func`` (function):
           An importance sampling function which maps an array of uniform variates
           of size ``[sample_dim, sample_count]`` to an array of ``sample_count``
           samples on the target domain.
    
        Parameter ``pdf_func`` (function):
           Function that is expected to specify the probability density of the
           samples produced by ``sample_func``. The test will try to collect
           sufficient statistical evidence to reject this hypothesis.
    
        Parameter ``sample_dim`` (int):
           Number of random dimensions consumed by ``sample_func`` per sample. The
           default value is ``2``.
    
        Parameter ``sample_count`` (int):
           Total number of samples to be generated. The test will have more
           evidence as this number tends to infinity. The default value is
           ``1000000``.
    
        Parameter ``res`` (int):
           Vertical resolution of the generated histograms. The horizontal
           resolution will be calculated as ``res * domain.aspect()``. The
           default value of ``101`` is intentionally an odd number to prevent
           issues with floating point precision at sharp boundaries that may
           separate the domain into two parts (e.g. top hemisphere of a sphere
           parameterization).
    
        Parameter ``ires`` (int):
           Number of horizontal/vertical subintervals used to numerically integrate
           the probability density over each histogram cell (using the trapezoid
           rule). The default value is ``4``.
    
        Parameter ``seed`` (int):
           Seed value for the PCG32 random number generator used in the histogram
           computation. The default value is ``0``.
    
        Notes:
    
        The following attributes are part of the public API:
    
        messages: string
            The implementation may generate a number of messages while running the
            test, which can be retrieved via this attribute.
    
        histogram: array
            The histogram array is populated by the ``tabulate_histogram()`` method
            and stored in this attribute.
    
        pdf: array
            The probability density function array is populated by the
            ``tabulate_pdf()`` method and stored in this attribute.
    
        p_value: float
            The p-value of the test is computed in the ``run()`` method and stored
            in this attribute.
        
    """

    def run(self, significance_level=0.01, test_count=1, quiet=False):
        """
        
        Run the Chi^2 test
        
        Parameter ``significance_level`` (float):
        Denotes the desired significance level (e.g. 0.01 for a test at the
        1% significance level)
        
        Parameter ``test_count`` (int):
        Specifies the total number of statistical tests run by the user.
        This value will be used to adjust the provided significance level
        so that the combination of the entire set of tests has the provided
        significance level.
        
        Returns → bool:
        ``True`` upon success, ``False`` if the null hypothesis was
        rejected.
        
        
        """
        ...

    def tabulate_histogram(self):
        """
        
        Invoke the provided sampling strategy many times and generate a
        histogram in the parameter domain. If ``sample_func`` returns a tuple
        ``(positions, weights)`` instead of just positions, the samples are
        considered to be weighted.
        
        """
        ...

    def tabulate_pdf(self):
        """
        
        Numerically integrate the provided probability density function over
        each cell to generate an array resembling the histogram computed by
        ``tabulate_histogram()``. The function uses the trapezoid rule over
        intervals discretized into ``self.ires`` separate function evaluations.
        
        """
        ...

    ...

def EmitterAdapter(emitter_type, extra):
    """
    
    Adapter to test Emitter sampling using the Chi^2 test.
    
    Parameter ``emitter_type`` (string):
    Name of the emitter plugin to instantiate.
    
    Parameter ``extra`` (string|dict):
    Additional XML used to specify the emitter's parameters, or a Python
    dictionary as used by the ``load_dict`` routine.
    
    """
    ...

class LineDomain:
    """
     The identity map on the line.
    """

    def aspect(self): ...
    def bounds(self): ...
    def map_backward(self, p): ...
    def map_forward(self, p): ...
    ...

def MicrofacetAdapter(md_type, alpha, sample_visible=False):
    """
    
    Adapter for testing microfacet distribution sampling techniques
    (separately from BSDF models, which are also tested)
    
    """
    ...

def PhaseFunctionAdapter(phase_type, extra, wi=[0, 0, 1], ctx=None):
    """
    
    Adapter to test phase function sampling using the Chi^2 test.
    
    Parameter ``phase_type`` (string):
    Name of the phase function plugin to instantiate.
    
    Parameter ``extra`` (string|dict):
    Additional XML used to specify the phase function's parameters, or a
    Python dictionary as used by the ``load_dict`` routine.
    
    Parameter ``wi`` (array(3,)):
    Incoming direction, in local coordinates.
    
    """
    ...

class PlanarDomain:
    """
    The identity map on the plane
    """

    def aspect(self): ...
    def bounds(self): ...
    def map_backward(self, p): ...
    def map_forward(self, p): ...
    ...

def SpectrumAdapter(value):
    """
    
    Adapter which permits testing 1D spectral power distributions using the
    Chi^2 test.
    
    """
    ...

class SphericalDomain:
    """
    Maps between the unit sphere and a [cos(theta), phi] parameterization.
    """

    def aspect(self): ...
    def bounds(self): ...
    def map_backward(self, p): ...
    def map_forward(self, p): ...
    ...

