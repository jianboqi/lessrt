from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

@overload
def eval_1d(min: float, max: float, values: numpy.ndarray[numpy.float32], x: float) -> float:
    """
    Evaluate a cubic spline interpolant of a *uniformly* sampled 1D
    function
    
    The implementation relies on Catmull-Rom splines, i.e. it uses finite
    differences to approximate the derivatives at the endpoints of each
    spline segment.
    
    Template parameter ``Extrapolate``:
        Extrapolate values when ``x`` is out of range? (default:
        ``False``)
    
    Parameter ``min``:
        Position of the first node
    
    Parameter ``max``:
        Position of the last node
    
    Parameter ``values``:
        Array containing ``size`` regularly spaced evaluations in the
        range [``min``, ``max``] of the approximated function.
    
    Parameter ``size``:
        Denotes the size of the ``values`` array
    
    Parameter ``x``:
        Evaluation point
    
    Remark:
        The Python API lacks the ``size`` parameter, which is inferred
        automatically from the size of the input array.
    
    Remark:
        The Python API provides a vectorized version which evaluates the
        function for many arguments ``x``.
    
    Returns:
        The interpolated value or zero when ``Extrapolate=false`` and
        ``x`` lies outside of [``min``, ``max``]
    
    """
    ...

@overload
def eval_1d(nodes: numpy.ndarray[numpy.float32], values: numpy.ndarray[numpy.float32], x: float) -> float:
    """
    Evaluate a cubic spline interpolant of a *non*-uniformly sampled 1D
    function
    
    The implementation relies on Catmull-Rom splines, i.e. it uses finite
    differences to approximate the derivatives at the endpoints of each
    spline segment.
    
    Template parameter ``Extrapolate``:
        Extrapolate values when ``x`` is out of range? (default:
        ``False``)
    
    Parameter ``nodes``:
        Array containing ``size`` non-uniformly spaced values denoting
        positions the where the function to be interpolated was evaluated.
        They must be provided in *increasing* order.
    
    Parameter ``values``:
        Array containing function evaluations matched to the entries of
        ``nodes``.
    
    Parameter ``size``:
        Denotes the size of the ``nodes`` and ``values`` array
    
    Parameter ``x``:
        Evaluation point
    
    Remark:
        The Python API lacks the ``size`` parameter, which is inferred
        automatically from the size of the input array
    
    Remark:
        The Python API provides a vectorized version which evaluates the
        function for many arguments ``x``.
    
    Returns:
        The interpolated value or zero when ``Extrapolate=false`` and
        ``x`` lies outside of \a [``min``, ``max``]
    """
    ...

def eval_2d(nodes1: numpy.ndarray[numpy.float32], nodes2: numpy.ndarray[numpy.float32], values: numpy.ndarray[numpy.float32], x: float, y: float) -> float:
    """
    Evaluate a cubic spline interpolant of a uniformly sampled 2D function
    
    This implementation relies on a tensor product of Catmull-Rom splines,
    i.e. it uses finite differences to approximate the derivatives for
    each dimension at the endpoints of spline patches.
    
    Template parameter ``Extrapolate``:
        Extrapolate values when ``p`` is out of range? (default:
        ``False``)
    
    Parameter ``nodes1``:
        Arrays containing ``size1`` non-uniformly spaced values denoting
        positions the where the function to be interpolated was evaluated
        on the ``X`` axis (in increasing order)
    
    Parameter ``size1``:
        Denotes the size of the ``nodes1`` array
    
    Parameter ``nodes``:
        Arrays containing ``size2`` non-uniformly spaced values denoting
        positions the where the function to be interpolated was evaluated
        on the ``Y`` axis (in increasing order)
    
    Parameter ``size2``:
        Denotes the size of the ``nodes2`` array
    
    Parameter ``values``:
        A 2D floating point array of ``size1*size2`` cells containing
        irregularly spaced evaluations of the function to be interpolated.
        Consecutive entries of this array correspond to increments in the
        ``X`` coordinate.
    
    Parameter ``x``:
        ``X`` coordinate of the evaluation point
    
    Parameter ``y``:
        ``Y`` coordinate of the evaluation point
    
    Remark:
        The Python API lacks the ``size1`` and ``size2`` parameters, which
        are inferred automatically from the size of the input arrays.
    
    Returns:
        The interpolated value or zero when ``Extrapolate=false``tt> and
        ``(x,y)`` lies outside of the node range
    """
    ...

def eval_spline(f0: float, f1: float, d0: float, d1: float, t: float) -> float:
    """
    Compute the definite integral and derivative of a cubic spline that is
    parameterized by the function values and derivatives at the endpoints
    of the interval ``[0, 1]``.
    
    Parameter ``f0``:
        The function value at the left position
    
    Parameter ``f1``:
        The function value at the right position
    
    Parameter ``d0``:
        The function derivative at the left position
    
    Parameter ``d1``:
        The function derivative at the right position
    
    Parameter ``t``:
        The parameter variable
    
    Returns:
        The interpolated function value at ``t``
    """
    ...

def eval_spline_d(f0: float, f1: float, d0: float, d1: float, t: float) -> Tuple[float, float]:
    """
    Compute the value and derivative of a cubic spline that is
    parameterized by the function values and derivatives of the interval
    ``[0, 1]``.
    
    Parameter ``f0``:
        The function value at the left position
    
    Parameter ``f1``:
        The function value at the right position
    
    Parameter ``d0``:
        The function derivative at the left position
    
    Parameter ``d1``:
        The function derivative at the right position
    
    Parameter ``t``:
        The parameter variable
    
    Returns:
        The interpolated function value and its derivative at ``t``
    """
    ...

def eval_spline_i(f0: float, f1: float, d0: float, d1: float, t: float) -> Tuple[float, float]:
    """
    Compute the definite integral and value of a cubic spline that is
    parameterized by the function values and derivatives of the interval
    ``[0, 1]``.
    
    Parameter ``f0``:
        The function value at the left position
    
    Parameter ``f1``:
        The function value at the right position
    
    Parameter ``d0``:
        The function derivative at the left position
    
    Parameter ``d1``:
        The function derivative at the right position
    
    Returns:
        The definite integral and the interpolated function value at ``t``
    """
    ...

@overload
def eval_spline_weights(min: float, max: float, size: int, x: float) -> Tuple[bool, int, List[float]]:
    """
    Compute weights to perform a spline-interpolated lookup on a
    *uniformly* sampled 1D function.
    
    The implementation relies on Catmull-Rom splines, i.e. it uses finite
    differences to approximate the derivatives at the endpoints of each
    spline segment. The resulting weights are identical those internally
    used by sample_1d().
    
    Template parameter ``Extrapolate``:
        Extrapolate values when ``x`` is out of range? (default:
        ``False``)
    
    Parameter ``min``:
        Position of the first node
    
    Parameter ``max``:
        Position of the last node
    
    Parameter ``size``:
        Denotes the number of function samples
    
    Parameter ``x``:
        Evaluation point
    
    Parameter ``weights``:
        Pointer to a weight array of size 4 that will be populated
    
    Remark:
        In the Python API, the ``offset`` and ``weights`` parameters are
        returned as the second and third elements of a triple.
    
    Returns:
        A boolean set to ``True`` on success and ``False`` when
        ``Extrapolate=false`` and ``x`` lies outside of [``min``, ``max``]
        and an offset into the function samples associated with weights[0]
    
    """
    ...

@overload
def eval_spline_weights(nodes: numpy.ndarray[numpy.float32], x: float) -> Tuple[bool, int, List[float]]:
    """
    Compute weights to perform a spline-interpolated lookup on a
    *non*-uniformly sampled 1D function.
    
    The implementation relies on Catmull-Rom splines, i.e. it uses finite
    differences to approximate the derivatives at the endpoints of each
    spline segment. The resulting weights are identical those internally
    used by sample_1d().
    
    Template parameter ``Extrapolate``:
        Extrapolate values when ``x`` is out of range? (default:
        ``False``)
    
    Parameter ``nodes``:
        Array containing ``size`` non-uniformly spaced values denoting
        positions the where the function to be interpolated was evaluated.
        They must be provided in *increasing* order.
    
    Parameter ``size``:
        Denotes the size of the ``nodes`` array
    
    Parameter ``x``:
        Evaluation point
    
    Parameter ``weights``:
        Pointer to a weight array of size 4 that will be populated
    
    Remark:
        The Python API lacks the ``size`` parameter, which is inferred
        automatically from the size of the input array. The ``offset`` and
        ``weights`` parameters are returned as the second and third
        elements of a triple.
    
    Returns:
        A boolean set to ``True`` on success and ``False`` when
        ``Extrapolate=false`` and ``x`` lies outside of [``min``, ``max``]
        and an offset into the function samples associated with weights[0]
    """
    ...

@overload
def integrate_1d(min: float, max: float, values: numpy.ndarray[numpy.float32]) -> mitsuba.ArrayXf:
    """
    Computes a prefix sum of integrals over segments of a *uniformly*
    sampled 1D Catmull-Rom spline interpolant
    
    This is useful for sampling spline segments as part of an importance
    sampling scheme (in conjunction with sample_1d)
    
    Parameter ``min``:
        Position of the first node
    
    Parameter ``max``:
        Position of the last node
    
    Parameter ``values``:
        Array containing ``size`` regularly spaced evaluations in the
        range [``min``, ``max``] of the approximated function.
    
    Parameter ``size``:
        Denotes the size of the ``values`` array
    
    Parameter ``out``:
        An array with ``size`` entries, which will be used to store the
        prefix sum
    
    Remark:
        The Python API lacks the ``size`` and ``out`` parameters. The
        former is inferred automatically from the size of the input array,
        and ``out`` is returned as a list.
    
    """
    ...

@overload
def integrate_1d(nodes: numpy.ndarray[numpy.float32], values: numpy.ndarray[numpy.float32]) -> mitsuba.ArrayXf:
    """
    Computes a prefix sum of integrals over segments of a *non*-uniformly
    sampled 1D Catmull-Rom spline interpolant
    
    This is useful for sampling spline segments as part of an importance
    sampling scheme (in conjunction with sample_1d)
    
    Parameter ``nodes``:
        Array containing ``size`` non-uniformly spaced values denoting
        positions the where the function to be interpolated was evaluated.
        They must be provided in *increasing* order.
    
    Parameter ``values``:
        Array containing function evaluations matched to the entries of
        ``nodes``.
    
    Parameter ``size``:
        Denotes the size of the ``values`` array
    
    Parameter ``out``:
        An array with ``size`` entries, which will be used to store the
        prefix sum
    
    Remark:
        The Python API lacks the ``size`` and ``out`` parameters. The
        former is inferred automatically from the size of the input array,
        and ``out`` is returned as a list.
    """
    ...

@overload
def invert_1d(min: float, max_: float, values: numpy.ndarray[numpy.float32], y: float, eps: float = 9.999999974752427e-07) -> float:
    """
    Invert a cubic spline interpolant of a *uniformly* sampled 1D
    function. The spline interpolant must be *monotonically increasing*.
    
    Parameter ``min``:
        Position of the first node
    
    Parameter ``max``:
        Position of the last node
    
    Parameter ``values``:
        Array containing ``size`` regularly spaced evaluations in the
        range [``min``, ``max``] of the approximated function.
    
    Parameter ``size``:
        Denotes the size of the ``values`` array
    
    Parameter ``y``:
        Input parameter for the inversion
    
    Parameter ``eps``:
        Error tolerance (default: 1e-6f)
    
    Returns:
        The spline parameter ``t`` such that ``eval_1d(..., t)=y``
    
    """
    ...

@overload
def invert_1d(nodes: numpy.ndarray[numpy.float32], values: numpy.ndarray[numpy.float32], y: float, eps: float = 9.999999974752427e-07) -> float:
    """
    Invert a cubic spline interpolant of a *non*-uniformly sampled 1D
    function. The spline interpolant must be *monotonically increasing*.
    
    Parameter ``nodes``:
        Array containing ``size`` non-uniformly spaced values denoting
        positions the where the function to be interpolated was evaluated.
        They must be provided in *increasing* order.
    
    Parameter ``values``:
        Array containing function evaluations matched to the entries of
        ``nodes``.
    
    Parameter ``size``:
        Denotes the size of the ``values`` array
    
    Parameter ``y``:
        Input parameter for the inversion
    
    Parameter ``eps``:
        Error tolerance (default: 1e-6f)
    
    Returns:
        The spline parameter ``t`` such that ``eval_1d(..., t)=y``
    """
    ...

@overload
def sample_1d(min: float, max: float, values: numpy.ndarray[numpy.float32], cdf: numpy.ndarray[numpy.float32], sample: float, eps: float = 9.999999974752427e-07) -> Tuple[float, float, float]:
    """
    Importance sample a segment of a *uniformly* sampled 1D Catmull-Rom
    spline interpolant
    
    Parameter ``min``:
        Position of the first node
    
    Parameter ``max``:
        Position of the last node
    
    Parameter ``values``:
        Array containing ``size`` regularly spaced evaluations in the
        range [``min``, ``max``] of the approximated function.
    
    Parameter ``cdf``:
        Array containing a cumulative distribution function computed by
        integrate_1d().
    
    Parameter ``size``:
        Denotes the size of the ``values`` array
    
    Parameter ``sample``:
        A uniformly distributed random sample in the interval ``[0,1]``
    
    Parameter ``eps``:
        Error tolerance (default: 1e-6f)
    
    Returns:
        1. The sampled position 2. The value of the spline evaluated at
        the sampled position 3. The probability density at the sampled
        position (which only differs from item 2. when the function does
        not integrate to one)
    
    """
    ...

@overload
def sample_1d(nodes: numpy.ndarray[numpy.float32], values: numpy.ndarray[numpy.float32], cdf: numpy.ndarray[numpy.float32], sample: float, eps: float = 9.999999974752427e-07) -> Tuple[float, float, float]:
    """
    Importance sample a segment of a *non*-uniformly sampled 1D Catmull-
    Rom spline interpolant
    
    Parameter ``nodes``:
        Array containing ``size`` non-uniformly spaced values denoting
        positions the where the function to be interpolated was evaluated.
        They must be provided in *increasing* order.
    
    Parameter ``values``:
        Array containing function evaluations matched to the entries of
        ``nodes``.
    
    Parameter ``cdf``:
        Array containing a cumulative distribution function computed by
        integrate_1d().
    
    Parameter ``size``:
        Denotes the size of the ``values`` array
    
    Parameter ``sample``:
        A uniformly distributed random sample in the interval ``[0,1]``
    
    Parameter ``eps``:
        Error tolerance (default: 1e-6f)
    
    Returns:
        1. The sampled position 2. The value of the spline evaluated at
        the sampled position 3. The probability density at the sampled
        position (which only differs from item 2. when the function does
        not integrate to one)
    """
    ...

