from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

RayEpsilon = ...
"Convert a string or number to a floating point number, if possible."
ShadowEpsilon = ...
"Convert a string or number to a floating point number, if possible."
ShapeEpsilon = ...
"Convert a string or number to a floating point number, if possible."
def chi2(arg0: mitsuba.ArrayXf64, arg1: mitsuba.ArrayXf64, arg2: float) -> Tuple[float, int, int, int]:
    """
    Compute the Chi^2 statistic and degrees of freedom of the given arrays
    while pooling low-valued entries together
    
    Given a list of observations counts (``obs[i]``) and expected
    observation counts (``exp[i]``), this function accumulates the Chi^2
    statistic, that is, ``(obs-exp)^2 / exp`` for each element ``0, ...,
    n-1``.
    
    Minimum expected cell frequency. The Chi^2 test statistic is not
    useful when when the expected frequency in a cell is low (e.g. less
    than 5), because normality assumptions break down in this case.
    Therefore, the implementation will merge such low-frequency cells when
    they fall below the threshold specified here. Specifically, low-valued
    cells with ``exp[i] < pool_threshold`` are pooled into larger groups
    that are above the threshold before their contents are added to the
    Chi^2 statistic.
    
    The function returns the statistic value, degrees of freedom, below-
    threshold entries and resulting number of pooled regions.
    """
    ...

def find_interval(size: int, pred: Callable[[int], bool]) -> int:
    """
    Find an interval in an ordered set
    
    This function performs a binary search to find an index ``i`` such
    that ``pred(i)`` is ``True`` and ``pred(i+1)`` is ``False``, where
    ``pred`` is a user-specified predicate that monotonically decreases
    over this range (i.e. max one ``True`` -> ``False`` transition).
    
    The predicate will be evaluated exactly <tt>floor(log2(size)) + 1<tt>
    times. Note that the template parameter ``Index`` is automatically
    inferred from the supplied predicate, which takes an index or an index
    vector of type ``Index`` as input argument and can (optionally) take a
    mask argument as well. In the vectorized case, each vector lane can
    use different predicate. When ``pred`` is ``False`` for all entries,
    the function returns ``0``, and when it is ``True`` for all cases, it
    returns <tt>size-2<tt>.
    
    The main use case of this function is to locate an interval (i, i+1)
    in an ordered list.
    
    ```
    float my_list[] = { 1, 1.5f, 4.f, ... };
    
    UInt32 index = find_interval(
        sizeof(my_list) / sizeof(float),
        [](UInt32 index, dr::mask_t<UInt32> active) {
            return dr::gather<Float>(my_list, index, active) < x;
        }
    );
    ```
    """
    ...

def is_power_of_two(arg0: int) -> bool:
    """
    Check whether the provided integer is a power of two
    """
    ...

@overload
def legendre_p(l: int, x: float) -> float:
    """
    Evaluate the l-th Legendre polynomial using recurrence
    
    """
    ...

@overload
def legendre_p(l: int, m: int, x: float) -> float:
    """
    Evaluate the l-th Legendre polynomial using recurrence
    """
    ...

def legendre_pd(l: int, x: float) -> Tuple[float, float]:
    """
    Evaluate the l-th Legendre polynomial and its derivative using
    recurrence
    """
    ...

def legendre_pd_diff(l: int, x: float) -> Tuple[float, float]:
    """
    Evaluate the function legendre_pd(l+1, x) - legendre_pd(l-1, x)
    """
    ...

def linear_to_srgb(arg0: float) -> float:
    """
    Applies the sRGB gamma curve to the given argument.
    """
    ...

def morton_decode2(m: int) -> mitsuba.Array2u: ...
def morton_decode3(m: int) -> mitsuba.Array3u: ...
def morton_encode2(v: mitsuba.Array2u) -> int: ...
def morton_encode3(v: mitsuba.Array3u) -> int: ...
def rlgamma(a, x):
    """
    Regularized lower incomplete gamma function based on CEPHES
    """
    ...

def round_to_power_of_two(arg0: int) -> int:
    """
    Round an unsigned integer to the next integer power of two
    """
    ...

def solve_quadratic(a: float, b: float, c: float) -> Tuple[bool, float, float]:
    """
    Solve a quadratic equation of the form a*x^2 + b*x + c = 0.
    
    Returns:
        ``True`` if a solution could be found
    """
    ...

def srgb_to_linear(arg0: float) -> float:
    """
    Applies the inverse sRGB gamma curve to the given argument.
    """
    ...

def ulpdiff(arg0: float, arg1: float) -> float:
    """
    Compare the difference in ULPs between a reference value and another
    given floating point number
    """
    ...

