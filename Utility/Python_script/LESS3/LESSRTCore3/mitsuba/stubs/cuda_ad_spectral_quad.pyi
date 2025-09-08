from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

def chebyshev(n: int) -> mitsuba.Float:
    """
    Computes the Chebyshev nodes, i.e. the roots of the Chebyshev
    polynomials of the first kind
    
    The output array contains positions on the interval :math:`[-1, 1]`.
    
    Parameter ``n``:
        Desired number of points
    """
    ...

def composite_simpson(n: int) -> Tuple[mitsuba.Float, mitsuba.Float]:
    """
    Computes the nodes and weights of a composite Simpson quadrature rule
    with the given number of evaluations.
    
    Integration is over the interval :math:`[-1, 1]`, which will be split
    into :math:`(n-1) / 2` sub-intervals with overlapping endpoints. A
    3-point Simpson rule is applied per interval, which is exact for
    polynomials of degree three or less.
    
    Parameter ``n``:
        Desired number of evaluation points. Must be an odd number bigger
        than 3.
    
    Returns:
        A tuple (nodes, weights) storing the nodes and weights of the
        quadrature rule.
    """
    ...

def composite_simpson_38(n: int) -> Tuple[mitsuba.Float, mitsuba.Float]:
    """
    Computes the nodes and weights of a composite Simpson 3/8 quadrature
    rule with the given number of evaluations.
    
    Integration is over the interval :math:`[-1, 1]`, which will be split
    into :math:`(n-1) / 3` sub-intervals with overlapping endpoints. A
    4-point Simpson rule is applied per interval, which is exact for
    polynomials of degree four or less.
    
    Parameter ``n``:
        Desired number of evaluation points. Must be an odd number bigger
        than 3.
    
    Returns:
        A tuple (nodes, weights) storing the nodes and weights of the
        quadrature rule.
    """
    ...

def gauss_legendre(n: int) -> Tuple[mitsuba.Float, mitsuba.Float]:
    """
    Computes the nodes and weights of a Gauss-Legendre quadrature (aka
    "Gaussian quadrature") rule with the given number of evaluations.
    
    Integration is over the interval :math:`[-1, 1]`. Gauss-Legendre
    quadrature maximizes the order of exactly integrable polynomials
    achieves this up to degree :math:`2n-1` (where :math:`n` is the number
    of function evaluations).
    
    This method is numerically well-behaved until about :math:`n=200` and
    then becomes progressively less accurate. It is generally not a good
    idea to go much higher---in any case, a composite or adaptive
    integration scheme will be superior for large :math:`n`.
    
    Parameter ``n``:
        Desired number of evaluation points
    
    Returns:
        A tuple (nodes, weights) storing the nodes and weights of the
        quadrature rule.
    """
    ...

def gauss_lobatto(n: int) -> Tuple[mitsuba.Float, mitsuba.Float]:
    """
    Computes the nodes and weights of a Gauss-Lobatto quadrature rule with
    the given number of evaluations.
    
    Integration is over the interval :math:`[-1, 1]`. Gauss-Lobatto
    quadrature is preferable to Gauss-Legendre quadrature whenever the
    endpoints of the integration domain should explicitly be included. It
    maximizes the order of exactly integrable polynomials subject to this
    constraint and achieves this up to degree :math:`2n-3` (where
    :math:`n` is the number of function evaluations).
    
    This method is numerically well-behaved until about :math:`n=200` and
    then becomes progressively less accurate. It is generally not a good
    idea to go much higher---in any case, a composite or adaptive
    integration scheme will be superior for large :math:`n`.
    
    Parameter ``n``:
        Desired number of evaluation points
    
    Returns:
        A tuple (nodes, weights) storing the nodes and weights of the
        quadrature rule.
    """
    ...

