from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

class Adam(Optimizer):
    """
        Implements the Adam optimizer presented in the paper *Adam: A Method for
        Stochastic Optimization* by Kingman and Ba, ICLR 2015.
    
        When optimizing many variables (e.g. a high resolution texture) with
        momentum enabled, it may be beneficial to restrict state and variable
        updates to the entries that received nonzero gradients in the current
        iteration (``mask_updates=True``).
        In the context of differentiable Monte Carlo simulations, many of those
        variables may not be observed at each iteration, e.g. when a surface is
        not visible from the current camera. Gradients for unobserved variables
        will remain at zero by default.
        If we do not take special care, at each new iteration:
    
        1. Momentum accumulated at previous iterations (potentially very noisy)
           will keep being applied to the variable.
        2. The optimizer's state will be updated to incorporate ``gradient = 0``,
           even though it is not an actual gradient value but rather lack of one.
    
        Enabling ``mask_updates`` avoids these two issues. This is similar to
        `PyTorch's SparseAdam optimizer <https://pytorch.org/docs/1.9.0/generated/torch.optim.SparseAdam.html>`_.
        
    """

    def items(self): ...
    def keys(self): ...
    def reset(self, key):
        """
        Zero-initializes the internal state associated with a parameter
        """
        ...

    def set_learning_rate(self, lr) -> None:
        """
        
        Set the learning rate.
        
        Parameter ``lr`` (``float``, ``dict``):
        The new learning rate. A ``dict`` can be provided instead to
        specify the learning rate for specific parameters.
        
        """
        ...

    def step(self):
        """
        Take a gradient step
        """
        ...

    ...

class Optimizer:
    """
        Base class of all gradient-based optimizers.
        
    """

    def items(self): ...
    def keys(self): ...
    def reset(self, key):
        """
        
        Resets the internal state associated with a parameter, if any (e.g. momentum).
        
        """
        ...

    def set_learning_rate(self, lr) -> None:
        """
        
        Set the learning rate.
        
        Parameter ``lr`` (``float``, ``dict``):
        The new learning rate. A ``dict`` can be provided instead to
        specify the learning rate for specific parameters.
        
        """
        ...

    ...

class SGD(Optimizer):
    """
        Implements basic stochastic gradient descent with a fixed learning rate
        and, optionally, momentum :cite:`Sutskever2013Importance` (0.9 is a typical
        parameter value for the ``momentum`` parameter).
    
        The momentum-based SGD uses the update equation
    
        .. math::
    
            v_{i+1} = \mu \cdot v_i +  g_{i+1}
    
        .. math::
            p_{i+1} = p_i + \varepsilon \cdot v_{i+1},
    
        where :math:`v` is the velocity, :math:`p` are the positions,
        :math:`\varepsilon` is the learning rate, and :math:`\mu` is
        the momentum parameter.
        
    """

    def items(self): ...
    def keys(self): ...
    def reset(self, key):
        """
        Zero-initializes the internal state associated with a parameter
        """
        ...

    def set_learning_rate(self, lr) -> None:
        """
        
        Set the learning rate.
        
        Parameter ``lr`` (``float``, ``dict``):
        The new learning rate. A ``dict`` can be provided instead to
        specify the learning rate for specific parameters.
        
        """
        ...

    def step(self):
        """
        Take a gradient step
        """
        ...

    ...

def contextmanager(func):
    """
    @contextmanager decorator.
    
    Typical usage:
    
    @contextmanager
    def some_generator(<arguments>):
    <setup>
    try:
    yield <value>
    finally:
    <cleanup>
    
    This makes this:
    
    with some_generator(<arguments>) as <variable>:
    <body>
    
    equivalent to this:
    
    <setup>
    try:
    <variable> = <value>
    <body>
    finally:
    <cleanup>
    
    """
    ...

