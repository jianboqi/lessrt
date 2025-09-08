from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import drjit
import drjit as dr

class ADFlag:
    """
    Members:
    
      ClearNone
    
      ClearEdges
    
      ClearInput
    
      ClearInterior
    
      ClearVertices
    
      Default
    """

    def __init__(self: drjit.ADFlag, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    ClearEdges = 1
    """
      ClearEdges
    """
    ClearInput = 2
    """
      ClearInput
    """
    ClearInterior = 4
    """
      ClearInterior
    """
    ClearNone = 0
    """
      ClearNone
    """
    ClearVertices = 6
    """
      ClearVertices
    """
    Default = 7
    """
      Default
    """

    ...

class ADMode:
    """
    Members:
    
      Primal
    
      Forward
    
      Backward
    """

    def __init__(self: drjit.ADMode, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Backward = 2
    """
      Backward
    """
    Forward = 1
    """
      Forward
    """
    Primal = 0
    """
      Primal
    """

    ...

class AllocType:
    """
    Members:
    
      Host
    
      HostAsync
    
      HostPinned
    
      Device
    """

    def __init__(self: drjit.AllocType, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Device = 3
    """
      Device
    """
    Host = 0
    """
      Host
      HostAsync
      HostPinned
    """
    HostAsync = 1
    """
      HostAsync
    """
    HostPinned = 2
    """
      HostPinned
    """

    ...

class ArrayBase:
    label = ...

    def assign(self, other): ...
    ...

class CustomOp:
    """
        Base class to implement custom differentiable operations.
    
        Dr.Jit can compute derivatives of builtin operations in both forward and reverse
        mode. In some cases, it may be useful or even necessary to tell Dr.Jit how a
        particular operation should be differentiated.
    
        This can be achieved by extending this class, overwriting callback functions
        that will later be invoked when the AD backend traverses the associated node in
        the computation graph. This class also provides a convenient way of stashing
        temporary results during the original function evaluation that can be accessed
        later on as part of forward or reverse-mode differentiation.
    
        Look at the section on :ref:`AD custom operations <custom-op>` for more detailed
        information.
    
        A class that inherits from this class should override a few methods as done in
        the code snippet below. :py:func:`dr.custom` can then be used to evaluate the
        custom operation and properly attach it to the AD graph.
    
        .. code-block::
    
            class MyCustomOp(dr.CustomOp):
                def eval(self, *args):
                    # .. evaluate operation ..
    
                def forward(self):
                    # .. compute forward-mode derivatives ..
    
                def backward(self):
                    # .. compute backward-mode derivatives ..
    
                def name(self):
                    return "MyCustomOp[]"
    
            dr.custom(MyCustomOp, *args)
        
    """

    def add_input(self, value):
        """
        
        Register an implicit input dependency of the operation on an AD variable.
        
        This function should be called by the ``eval()`` implementation when an
        operation has a differentiable dependence on an input that is not an
        input argument (e.g. a private instance variable).
        
        Args:
        value (object): variable this operation depends on implicitly.
        
        """
        ...

    def add_output(self, value):
        """
        
        Register an implicit output dependency of the operation on an AD variable.
        
        This function should be called by the
        ef eval() implementation when an
        operation has a differentiable dependence on an output that is not an
        return value of the operation (e.g. a private instance variable).
        
        Args:
        value (object): variable this operation depends on implicitly.
        
        """
        ...

    def backward(self):
        """
        
        Evaluated backward-mode derivatives.
        
        .. danger::
        
        This method must be overriden, no default implementation provided.
        
        """
        ...

    def eval(self, *args):
        """
        
        eval(self, *args) -> object
        Evaluate the custom function in primal mode.
        
        The inputs will be detached from the AD graph, and the output *must* also be
        detached.
        
        .. danger::
        
        This method must be overriden, no default implementation provided.
        
        """
        ...

    def forward(self):
        """
        
        Evaluated forward-mode derivatives.
        
        .. danger::
        
        This method must be overriden, no default implementation provided.
        
        """
        ...

    def grad_in(self, name):
        """
        
        Access the gradient associated with the input argument ``name`` (fwd. mode AD).
        
        Args:
        name (str): name associated to an input variable (e.g. keyword argument).
        
        Returns:
        object: the gradient value associated with the input argument.
        
        """
        ...

    def grad_out(self):
        """
        
        Access the gradient associated with the output argument (backward mode AD).
        
        Returns:
        object: the gradient value associated with the output argument.
        
        """
        ...

    def name(self):
        """
        
        Return a descriptive name of the ``CustomOp`` instance.
        
        The name returned by this method is used in the GraphViz output.
        
        If not overriden, this method returns ``"CustomOp[unnamed]"``.
        
        """
        ...

    def set_grad_in(self, name, value):
        """
        
        Accumulate a gradient value into an input argument (backward mode AD).
        
        Args:
        name (str): name associated to the input variable (e.g. keyword argument).
        value (object): gradient value to accumulate.
        
        """
        ...

    def set_grad_out(self, value):
        """
        
        Accumulate a gradient value into the output argument (forward mode AD).
        
        Args:
        value (object): gradient value to accumulate.
        
        """
        ...

    ...

DEBUG = ...
"""
bool(x) -> bool

Returns True when the argument x is true, False otherwise.
The builtins True and False are the only two instances of the class bool.
The class bool is a subclass of the class int, and cannot be subclassed.
"""
Dynamic = ...
"""
int([x]) -> integer
int(x, base=10) -> integer

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is a number, return x.__int__().  For floating point
numbers, this truncates towards zero.

If x is not a number or if base is given, then x must be a string,
bytes, or bytearray instance representing an integer literal in the
given base.  The literal can be preceded by '+' or '-' and be surrounded
by whitespace.  The base defaults to 10.  Valid bases are 0 and 2-36.
Base 0 means to interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
"""
class Exception:
    ...

class FilterMode:
    """
    Members:
    
      Nearest
    
      Linear
    """

    def __init__(self: drjit.FilterMode, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Linear = 1
    """
      Linear
    """
    Nearest = 0
    """
      Nearest
    """

    ...

class JitBackend:
    """
    Members:
    
      CUDA
    
      LLVM
    """

    def __init__(self: drjit.JitBackend, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    CUDA = 1
    """
      CUDA
    """
    LLVM = 2
    """
      LLVM
    """

    ...

class JitFlag:
    """
    Members:
    
      ConstProp
    
      ValueNumbering
    
      LoopRecord
    
      LoopOptimize
    
      VCallRecord
    
      VCallDeduplicate
    
      VCallOptimize
    
      VCallInline
    
      ForceOptiX
    
      Recording
    
      PrintIR
    
      LaunchBlocking
    
      ADOptimize
    
      KernelHistory
    
      AtomicReduceLocal
    
      Default
    """

    def __init__(self: drjit.JitFlag, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    ADOptimize = 8192
    """
      ADOptimize
    """
    AtomicReduceLocal = 16384
    """
      AtomicReduceLocal
    """
    ConstProp = 1
    """
      ConstProp
    """
    Default = 24703
    """
      Default
    """
    ForceOptiX = 256
    """
      ForceOptiX
    """
    KernelHistory = 2048
    """
      KernelHistory
    """
    LaunchBlocking = 4096
    """
      LaunchBlocking
    """
    LoopOptimize = 8
    """
      LoopOptimize
    """
    LoopRecord = 4
    """
      LoopRecord
    """
    PrintIR = 1024
    """
      PrintIR
    """
    Recording = 512
    """
      Recording
    """
    VCallDeduplicate = 32
    """
      VCallDeduplicate
    """
    VCallInline = 128
    """
      VCallInline
    """
    VCallOptimize = 64
    """
      VCallOptimize
    """
    VCallRecord = 16
    """
      VCallRecord
    """
    ValueNumbering = 2
    """
      ValueNumbering
    """

    ...

class KernelType:
    """
    Members:
    
      JIT
    
      Reduce
    
      VCallReduce
    
      Other
    """

    def __init__(self: drjit.KernelType, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    JIT = 0
    """
      JIT
    """
    Other = 3
    """
      Other
    """
    Reduce = 1
    """
      Reduce
    """
    VCallReduce = 2
    """
      VCallReduce
    """

    ...

class LogLevel:
    """
    Members:
    
      Disable
    
      Error
    
      Warn
    
      Info
    
      InfoSym
    
      Debug
    
      Trace
    """

    def __init__(self: drjit.LogLevel, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Debug = 5
    """
      Debug
    """
    Disable = 0
    """
      Disable
    """
    Error = 1
    """
      Error
    """
    Info = 3
    """
      Info
      InfoSym
    """
    InfoSym = 4
    """
      InfoSym
    """
    Trace = 6
    """
      Trace
    """
    Warn = 2
    """
      Warn
    """

    ...

class ReduceOp:
    """
    Members:
    
      Nothing
    
      Add
    
      Mul
    
      Min
    
      Max
    
      And
    
      Or
    """

    def __init__(self: drjit.ReduceOp, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Add = 1
    """
      Add
    """
    And = 5
    """
      And
    """
    Max = 4
    """
      Max
    """
    Min = 3
    """
      Min
    """
    Mul = 2
    """
      Mul
    """
    Nothing = 0
    """
      Nothing
    """
    Or = 6
    """
      Or
    """

    ...

class Scope:
    def __init__(self: drjit.Scope, arg0: str) -> None: ...
    ...

class VarType:
    """
    Members:
    
      Void
    
      Bool
    
      Int8
    
      UInt8
    
      Int16
    
      UInt16
    
      Int32
    
      UInt32
    
      Int64
    
      UInt64
    
      Pointer
    
      Float16
    
      Float32
    
      Float64
    """

    def __init__(self: drjit.VarType, value: int) -> None: ...
    NumPy = ...
    Size = ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Bool = 1
    """
      Bool
    """
    Float16 = 11
    """
      Float16
    """
    Float32 = 12
    """
      Float32
    """
    Float64 = 13
    """
      Float64
    """
    Int16 = 4
    """
      Int16
    """
    Int32 = 6
    """
      Int32
    """
    Int64 = 8
    """
      Int64
    """
    Int8 = 2
    """
      Int8
    """
    Pointer = 10
    """
      Pointer
    """
    UInt16 = 5
    """
      UInt16
    """
    UInt32 = 7
    """
      UInt32
    """
    UInt64 = 9
    """
      UInt64
    """
    UInt8 = 3
    """
      UInt8
    """
    Void = 0
    """
      Void
    """

    ...

class WrapMode:
    """
    Members:
    
      Repeat
    
      Clamp
    
      Mirror
    """

    def __init__(self: drjit.WrapMode, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Clamp = 1
    """
      Clamp
    """
    Mirror = 2
    """
      Mirror
    """
    Repeat = 0
    """
      Repeat
    """

    ...

def abs(arg, /):
    """
    
    abs(arg, /)
    Compute the absolute value of the provided input.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    float | int | drjit.ArrayBase: Absolute value of the input)
    
    """
    ...

def abs_dot(a, b):
    """
    
    abs_dot(arg0, arg1, /) -> float | int | drjit.ArrayBase
    Computes the absolute value of dot product of two arrays.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg0 (list | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    arg1 (list | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Absolute value of the dot product of inputs
    
    """
    ...

def accum_grad(dst, src):
    """
    
    Accumulate into the gradient of a variable.
    
    Broadcasting is applied to the gradient value if necessary and possible to match
    the type of the input variable.
    
    Args:
    dst (object): An arbitrary Dr.Jit array, tensor,
    :ref:`custom data structure <custom-struct>`, sequences, or mapping.
    
    src (object): An arbitrary Dr.Jit array, tensor,
    :ref:`custom data structure <custom-struct>`, sequences, or mapping.
    
    """
    ...

def acos(arg, /):
    """
    
    acos(arg, /)
    Arccosine approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Arccosine of the input
    
    """
    ...

def acosh(arg, /):
    """
    
    acosh(arg, /)
    Hyperbolic arccosine approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Hyperbolic arccosine of the input
    
    """
    ...

def ad_whos() -> None: ...
def ad_whos_str() -> str: ...
def all(arg, /):
    """
    
    all(arg, /) -> bool | drjit.ArrayBase
    Computes whether all input elements evaluate to ``True``.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Boolean array
    
    """
    ...

def all_nested(arg, /):
    """
    
    all_nested(arg, /) -> bool
    Iterates :py:func:`all` until the type of the return value no longer
    changes. This can be used to reduce a nested mask array into a single
    value.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Boolean
    
    """
    ...

def allclose(a, b, rtol=1e-05, atol=1e-08, equal_nan=False):
    """
    
    Returns ``True`` if two arrays are element-wise equal within a given error
    tolerance.
    
    The function considers both absolute and relative error thresholds. Specifically
    **a** and **b** are considered equal if all elements satisfy
    
    .. math::
    |a - b| \le |b| \cdot \mathrm{rtol} + \mathrm{atol}.
    
    Args:
    a (object): A Dr.Jit array or other kind of numeric sequence type.
    
    b (object): A Dr.Jit array or other kind of numeric sequence type.
    
    rtol (float): A relative error threshold. The default is :math:`10^{-5}`.
    
    atol (float): An absolute error threshold. The default is :math:`10^{-8}`.
    
    equal_nan (bool): If **a** and **b** *both* contain a *NaN* (Not a Number) entry,
    should they be considered equal? The default is ``False``.
    
    Returns:
    bool: The result of the comparison.
    
    """
    ...

def and_(a, b): ...
def any(arg, /):
    """
    
    any(arg, /) -> bool | drjit.ArrayBase
    Computes whether any of the input elements evaluate to ``True``.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Boolean array
    
    """
    ...

def any_nested(arg, /):
    """
    
    any_nested(arg, /) -> bool
    Iterates :py:func:`any` until the type of the return value no longer
    changes. This can be used to reduce a nested mask array into a single
    value.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Boolean
    
    """
    ...

def arange(dtype, start=None, stop=None, step=1):
    """
    
    This function generates an integer sequence on the interval [``start``,
    ``stop``) with step size ``step``, where ``start`` = 0 and ``step`` = 1 if not
    specified.
    
    Args:
    dtype (type): Desired Dr.Jit array type. The ``dtype`` must refer to a
    dynamically sized 1D Dr.Jit array such as :py:class:`drjit.scalar.ArrayXu`
    or :py:class:`drjit.cuda.Float`.
    
    start (int): Start of the interval. The default value is `0`.
    
    stop/size (int): End of the interval (not included). The name of this
    parameter differs between the two provided overloads.
    
    step (int): Spacing between values. The default value is `1`.
    
    Returns:
    object: The computed sequence of type ``dtype``.
    
    """
    ...

def arg(arg, /):
    """
    
    Return the argument of a complex Dr.Jit array.
    
    When the provided array isn't an instance of :py:class:`drjit.Complex`, this
    function assumes that the input array represents the real part of a complex
    variable.
    
    Args:
    arg (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | drjit.ArrayBase: Argument of the complex input array
    
    """
    ...

def asin(arg, /):
    """
    
    asin(arg, /)
    Arcsine approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Arcsine of the input
    
    """
    ...

def asinh(arg, /):
    """
    
    asinh(arg, /)
    Hyperbolic arcsine approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Hyperbolic arcsine of the input
    
    """
    ...

def atan(arg, /):
    """
    
    atan(arg, /)
    Arctangent approximation
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Arctangent of the input
    
    """
    ...

def atan2(a, b, /):
    """
    
    atan2(y, x, /)
    Arctangent of two values
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    y (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    x (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Arctangent of ``y``/``x``, using the argument signs to
    determine the quadrant of the return value
    
    """
    ...

def atanh(arg, /):
    """
    
    atanh(arg, /)
    Hyperbolic arctangent approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Hyperbolic arctangent of the input
    
    """
    ...

def backward(arg, flags=ADFlag.Default):
    """
    
    Backward propagate gradients from a provided Dr.Jit differentiable array.
    
    An exception will be raised when the provided array doesn't have gradient tracking
    enabled or if it isn't an instance of a Dr.Jit differentiable array type.
    
    This function is an alias of :py:func:`drjit.backward_from`.
    
    Args:
    arg (object): A Dr.Jit differentiable array instance.
    
    flags (ADFlag | int): flags to control what should and should not be
    destructed during the traversal. The default value is ``ADFlag.Default``.
    
    """
    ...

def backward_from(arg, flags=ADFlag.Default):
    """
    
    Backward propagates gradients from a provided Dr.Jit differentiable array.
    
    An exception will be raised when the provided array doesn't have gradient tracking
    enabled or if it isn't an instance of a Dr.Jit differentiable array type.
    
    Args:
    arg (object): A Dr.Jit differentiable array instance.
    
    flags (ADFlag | int): flags to control what should and should not be
    destructed during the traversal. The default value is ``ADFlag.Default``.
    
    """
    ...

def backward_to(*args, flags=ADFlag.Default):
    """
    
    Backward propagate gradients to a set of provided Dr.Jit differentiable arrays.
    
    Internally, the AD computational graph will be first traversed *forward* to find
    all potential source of gradient for the provided array. Then only the backward
    gradient propagation traversal takes place.
    
    The ``flags`` argument should be provided as a keyword argument for this function.
    
    An exception will be raised when the provided array doesn't have gradient tracking
    enabled or if it isn't an instance of a Dr.Jit differentiable array type.
    
    Args:
    *args (tuple): A variable-length list of Dr.Jit differentiable array, tensor,
    :ref:`custom data structure <custom-struct>`, sequences, or mapping.
    
    flags (ADFlag | int): flags to control what should and should not be
    destructed during the traversal. The default value is ``ADFlag.Default``.
    
    Returns:
    object: the gradient value associated to the output variables.
    
    """
    ...

def binary_search(start, end, pred):
    """
    
    Perform binary search over a range given a predicate ``pred``, which
    monotonically decreases over this range (i.e. max one ``True`` -> ``False``
    transition).
    
    Given a (scalar) ``start`` and ``end`` index of a range, this function
    evaluates a predicate ``floor(log2(end-start) + 1)`` times with index
    values on the interval [start, end] (inclusive) to find the first index
    that no longer satisfies it. Note that the template parameter ``Index`` is
    automatically inferred from the supplied predicate. Specifically, the
    predicate takes an index array as input argument. When ``pred`` is ``False``
    for all entries, the function returns ``start``, and when it is ``True`` for
    all cases, it returns ``end``.
    
    The following code example shows a typical use case: ``data`` contains a
    sorted list of floating point numbers, and the goal is to map floating
    point entries of ``x`` to the first index ``j`` such that ``data[j] >= threshold``
    (and all of this of course in parallel for each vector element).
    
    .. code-block::
    
    dtype = dr.llvm.Float
    data = dtype(...)
    threshold = dtype(...)
    
    index = dr.binary_search(
    0, len(data) - 1,
    lambda index: dr.gather(dtype, data, index) < threshold
    )
    
    Args:
    start (int): Starting index for the search range
    end (int): Ending index for the search range
    pred (function): The predicate function to be evaluated
    
    Returns:
    Index array resulting from the binary search
    
    """
    ...

def block_sum(value, size):
    """
    
    Sum over elements within blocks
    
    This function adds all elements of contiguous blocks of size ``size``
    in the input array ``value`` and writes them to the returned array.
    For example, ``a, b, c, d, e, f`` turns into ``a+b, c+d, e+f`` when
    ``size == 2``. The length of the input array must be a multiple of ``size``.
    
    Args:
    arg (drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    size (int): size of the block
    
    Returns:
    Sum over elements within blocks
    
    """
    ...

def bool_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into a *boolean* version with
    the same element size.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3i64`), it
    returns an *boolean* version (e.g. :py:class:`drjit.cuda.Array3b64`).
    
    2. When the input isn't a type, it returns ``bool_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``bool``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def cbrt(arg, /):
    """
    
    cbrt(arg, /)
    Evaluate the cube root of the provided input.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Cube root of the input
    
    """
    ...

def ceil(arg, /):
    """
    
    ceil(arg, /)
    Evaluate the ceiling, i.e. the smallest integer >= arg.
    
    The function does not convert the type of the input array. A separate
    cast is necessary when integer output is desired.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Ceiling of the input
    
    """
    ...

def clamp(value, min, max, /):
    """
    
    Clip the provided input to the given interval.
    
    This function is equivalent :py:func:`drjit.clamp`.
    
    Args:
    value (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    min (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    max (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | drjit.ArrayBase: Clipped input
    
    """
    ...

def clip(value, min, max, /):
    """
    
    Clip the provided input to the given interval.
    
    This function is equivalent to
    
    .. code-block::
    
    dr.maximum(dr.minimum(value, max), min)
    
    Dr.Jit also defines :py:func:`drjit.clamp` as an alias of this function.
    
    Args:
    value (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    min (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    max (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | drjit.ArrayBase: Clipped input
    
    """
    ...

def compress(mask, /):
    """
    
    compress(arg, /) -> int | drjit.ArrayBase
    Compress a mask into an array of nonzero indices.
    
    This function takes an boolean array as input and then returns an unsigned
    32-bit integer array containing the indices of nonzero entries.
    
    It can be used to reduce a stream to a subset of active entries via the
    following recipe:
    
    .. code-box:: python
    
    # Input: an active mask and several arrays data_1, data_2, ...
    dr.schedule(active, data_1, data_2, ...)
    indices = dr.compress(active)
    data_1 = dr.gather(type(data_1), data_1, indices)
    data_2 = dr.gather(type(data_2), data_2, indices)
    # ...
    
    There is some conceptual overlap between this function and
    :py:func:`drjit.cscatter_inc()`, which can likewise be used to reduce a
    stream to a smaller subset of active items. Please see the documentation of
    t :py:func:`drjit.cscatter_inc()` for details.
    
    .. danger::
    This function internally performs a synchronization step.
    
    Args:
    arg (bool | drjit.ArrayBase): A Python or Dr.Jit boolean type
    
    Returns:
    Array of nonzero indices
    
    """
    ...


from .stubs import config as config

def conj(arg, /):
    """
    
    Return the complex conjugate of a provided Dr.Jit array.
    
    When the provided array isn't an instance of :py:class:`drjit.Complex` or
    :py:class:`drjit.Quaternion`, this function returns the input unchanged.
    
    Args:
    arg (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | drjit.ArrayBase: Real part of the input array
    
    """
    ...

def copysign(a, b, /):
    """
    
    copysign(arg0, arg1, /)
    Copy the sign of ``arg1`` to ``arg0` element-wise.
    
    Args:
    arg0 (int | float | drjit.ArrayBase): A Python or Dr.Jit array to change the sign of
    arg1 (int | float | drjit.ArrayBase): A Python or Dr.Jit array to copy the sign from
    
    Returns:
    float | int | drjit.ArrayBase: The values of ``arg0`` with the sign of ``arg1``
    
    """
    ...

def cos(arg, /):
    """
    
    cos(arg, /)
    Cosine approximation based on the CEPHES library.
    
    The implementation of this function is designed to achieve low error on the
    domain :math:`|x| < 8192` and will not perform as well beyond this range. See
    the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU").
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Cosine of the input
    
    """
    ...

def cosh(arg, /):
    """
    
    cosh(arg, /)
    Hyperbolic cosine approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Hyperbolic cosine of the input
    
    """
    ...

def cot(arg):
    """
    
    cot(arg, /)
    Cotangent approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Cotangent of the input
    
    """
    ...

def count(arg, /):
    """
    
    count(arg, /) -> int | drjit.ArrayBase
    Efficiently computes the number of entries whose boolean values
    are ``True``, i.e.
    
    .. code-block:: python
    
    (value[0] ? 1 : 0) + ... (value[Size - 1] ? 1 : 0)
    
    For 1D arrays, ``count()`` returns a result of type ``int``. For
    multidimensional arrays, the horizontal reduction is performed over the
    *outermost* dimension.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit boolean type
    
    Returns:
    Number of entries whose mask bits are turned on
    
    """
    ...

def cross(a, b, /):
    """
    
    Returns the cross-product of the two input 3D arrays
    
    Args:
    arg0 (list | drjit.ArrayBase): A Python or Dr.Jit 3D type
    arg1 (list | drjit.ArrayBase): A Python or Dr.Jit 3D type
    
    Returns:
    Cross-product of the two input 3D arrays
    
    """
    ...

def csc(arg, /):
    """
    
    csc(arg, /)
    Cosecant approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Cosecant of the input
    
    """
    ...


from .stubs import cuda as cuda

def cumsum(value):
    """
    
    Compute an cumulative sum (aka. inclusive prefix sum) of the 1D input array.
    
    This function wraps :cpp:func:`drjit.prefix_sum` and is implemented as
    
    .. code-block:: python
    
    return prefix_sum(value, exclusive=False)
    
    """
    ...

def custom(cls, *args, **kwargs):
    """
    
    Evaluate a custom differentiable operation (see :py:class:`CustomOp`).
    
    Look at the section on :ref:`AD custom operations <custom-op>` for more detailed
    information.
    
    """
    ...

def deg2rad(arg, /):
    """
    
    deg2rad(arg, /) -> float | drjit.ArrayBase
    Convert angles from degrees to radians.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    The equivalent angle in radians.
    
    """
    ...

def depth_v(arg, /):
    """
    
    depth_v(arg, /)
    Return the depth of the provided Dr.Jit array instance or type
    
    For example, an array consisting of floating point values (for example,
    :py:class:`drjit.scalar.Array3f`) has depth ``1``, while an array consisting of
    sub-arrays (e.g., :py:class:`drjit.cuda.Array3f`) has depth ``2``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    int: Returns the depth of the input, if it is a Dr.Jit array instance or
    type. Returns ``0`` for all other inputs.
    
    """
    ...

def det(m, /):
    """
    
    det(arg, /)
    Compute the determinant of the provided Dr.Jit matrix.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    Returns:
    drjit.ArrayBase: The determinant value of the input matrix
    
    """
    ...

def detach(arg, preserve_type=True):
    """
    
    Transforms the input variable into its non-differentiable version (*detaches* it
    from the AD computational graph).
    
    This function is able to traverse data-structures such a sequences, mappings or
    :ref:`custom data structure <custom-struct>` and applies the transformation to the
    underlying variables.
    
    When the input variable isn't a Dr.Jit differentiable array, it is returned as it is.
    
    While the type of the returned array is preserved by default, it is possible to
    set the ``preserve_type`` argument to false to force the returned type to be
    non-differentiable.
    
    Args:
    arg (object): An arbitrary Dr.Jit array, tensor,
    :ref:`custom data structure <custom-struct>`, sequence, or mapping.
    
    preserve_type (bool): Defines whether the returned variable should preserve
    the type of the input variable.
    Returns:
    object: The detached variable.
    
    """
    ...

def detached_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into an non-differentiable version.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a differentiable Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.ad.Array3f`), it
    returns a non-differentiable version (e.g. :py:class:`drjit.cuda.Array3f`).
    
    2. When the input isn't a type, it returns ``detached_t(type(arg))``.
    
    3. When the input type is non-differentiable or not a Dr.Jit array type, the function returns it unchanged.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...


from .stubs import detail as detail

def device(value=None):
    """
    
    Return the CUDA device ID associated with the current thread. (-1 if CPU)
    
    """
    ...

def device_count() -> int: ...
def diag(a, /):
    """
    
    diag(arg, /)
    Returns the diagonal matrix of the provided Dr.Jit matrix.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    Returns:
    drjit.ArrayBase: The diagonal matrix of the input matrix
    
    """
    ...

def diff_array_t(a):
    """
    
    Converts the provided Dr.Jit array/tensor type into a differentiable version.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3f`), it
    returns a *differentiable* version (e.g. :py:class:`drjit.cuda.ad.Array3f`).
    
    2. When the input isn't a type, it returns ``diff_array_t(type(arg))``.
    
    3. When the input is is a list or a tuple, it recursively call ``diff_array_t`` over all elements.
    
    4. When the input is not a Dr.Jit array or type, the function throws an exception.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def disable_grad(*args):
    """
    
    Disable gradient tracking for the provided variables.
    
    This function accepts a variable-length list of arguments and processes it
    as follows:
    
    - It recurses into sequences (``tuple``, ``list``, etc.)
    - It recurses into the values of mappings (``dict``, etc.)
    - It recurses into the fields of :ref:`custom data structures <custom-struct>`.
    
    During recursion, the function disables gradient tracking for all Dr.Jit arrays.
    For every other types, this function won't do anything.
    
    Args:
    *args (tuple): A variable-length list of Dr.Jit array instances,
    :ref:`custom data structures <custom-struct>`, sequences, or mappings.
    
    """
    ...

def dispatch(instances, func, *args):
    """
    
    Dispatches a call to the given function on an array of instances of a class
    registered to the Dr.Jit registry. The provided function is assumed to take
    at least one argument that will represent the individual instance of the
    class this function is recorded on.
    
    This routine can be used to perform dynamic dispatch to Python methods of
    instances. The code generation underlying Dr.Jit will transform arbitrary
    sequences of such method calls into unified functions in the generated code.
    In other words, a single dispatch call that calls two methods is potentially
    significantly faster than two separate dispatches.
    
    .. code-block:: python
    
    pointers = ... # Dr.Jit pointer array type
    
    def func(self, arg):
    v = self.foo() # call foo() on a single instance at a time
    return v + arg
    
    arg = dr.llvm.Float([1.0, 2.0, 3.0, 4.0])
    
    res = dr.dispatch(pointers, func, arg)
    
    Args:
    instances (drjit.ArrayBase): array of pointers to instances to dispatch
    the given function on.
    func (dict): function to dispatch on all instances.
    args (tuple): the arguments to pass to the function.
    
    Returns:
    object: the result of the function evaluated for the given instances.
    
    """
    ...

def dot(a, b, /):
    """
    
    dot(arg0, arg1, /) -> float | int | drjit.ArrayBase
    Computes the dot product of two arrays.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg0 (list | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    arg1 (list | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Dot product of inputs
    
    """
    ...

e = ...
"Convert a string or number to a floating point number, if possible."
def empty(dtype, shape=1):
    """
    
    Return an uninitialized Dr.Jit array of the desired type and shape.
    
    This function can create uninitialized buffers of various types. It is
    essentially a wrapper around CPU/GPU variants of ``malloc()`` and produces
    arrays filled with uninitialized/undefined data. It should only be used in
    combination with a subsequent call to an operation like
    :py:func:`drjit.scatter()` that overwrites the array contents with valid data.
    
    The ``dtype`` parameter can be used to request:
    
    - A Dr.Jit array type like :py:class:`drjit.cuda.Array2f`. When ``shape``
    specifies a sequence, it must be compatible with static dimensions of the
    ``dtype``. For example, ``dr.empty(dr.cuda.Array2f, shape=(3, 100))`` fails,
    since the leading dimension is incompatible with
    :py:class:`drjit.cuda.Array2f`. When ``shape`` is an integer, it specifies
    the size of the last (dynamic) dimension, if available.
    
    - A tensorial type like :py:class:`drjit.scalar.TensorXf`. When ``shape``
    specifies a sequence (list/tuple/..), it determines the tensor rank and
    shape. When ``shape`` is an integer, the function creates a rank-1 tensor of
    the specified size.
    
    - A :ref:`custom data structure <custom-struct>`. In this case,
    :py:func:`drjit.empty()` will invoke itself recursively to allocate memory
    for each field of the data structure.
    
    - A scalar Python type like ``int``, ``float``, or ``bool``. The ``shape``
    parameter is ignored in this case, and the function returns a
    zero-initialized result (there is little point in instantiating uninitialized
    versions of scalar Python types).
    
    Args:
    dtype (type): Desired Dr.Jit array type, Python scalar type, or
    :ref:`custom data structure <custom-struct>`.
    
    shape (Sequence[int] | int): Shape of the desired array
    
    Returns:
    object: An instance of type ``dtype`` with arbitrary/undefined contents.
    
    """
    ...

def enable_grad(*args):
    """
    
    Enable gradient tracking for the provided variables.
    
    This function accepts a variable-length list of arguments and processes it
    as follows:
    
    - It recurses into sequences (``tuple``, ``list``, etc.)
    - It recurses into the values of mappings (``dict``, etc.)
    - It recurses into the fields of :ref:`custom data structures <custom-struct>`.
    
    During recursion, the function enables gradient tracking for all Dr.Jit arrays.
    For every other types, this function won't do anything.
    
    Args:
    *args (tuple): A variable-length list of Dr.Jit array instances,
    :ref:`custom data structures <custom-struct>`, sequences, or mappings.
    
    """
    ...

def enqueue(mode, *args):
    """
    
    Enqueues variable for the subsequent AD traversal.
    
    In Dr.Jit, the process of automatic differentiation is split into two parts:
    
    1. Discover and enqueue the variables to be considered as inputs during the
    subsequent AD traversal.
    2. Traverse the AD graph starting from the enqueued variables to propagate the
    gradients towards the output variables (e.g. leaf in the AD graph).
    
    
    This function handles the first part can operate in different modes depending on
    the specified ``mode``:
    
    - ``ADMode.Forward``: the provided ``value`` will be considered as input during
    the subsequent AD traversal.
    
    - ``ADMode.Backward``: a traversal of the AD graph starting from the provided
    ``value`` will take place to find all potential source of gradients and
    enqueue them.
    
    For example, a typical chain of operations to forward propagate the gradients
    from ``a`` to ``b`` would look as follow:
    
    .. code-block::
    
    a = dr.llvm.ad.Float(1.0)
    dr.enable_grad(a)
    b = f(a) # some computation involving `a`
    dr.set_gradient(a, 1.0)
    dr.enqueue(dr.ADMode.Forward, a)
    dr.traverse(dr.llvm.ad.Float, dr.ADMode.Forward)
    grad = dr.grad(b)
    
    It could be the case that ``f(a)`` involves other differentiable variables that
    already contain some gradients. In this situation we can use ``ADMode.Backward``
    to discover and enqueue them before the traversal.
    
    .. code-block::
    
    a = dr.llvm.ad.Float(1.0)
    dr.enable_grad(a)
    b = f(a, ...) # some computation involving `a` and some hidden variables
    dr.set_gradient(a, 1.0)
    dr.enqueue(dr.ADMode.Backward, b)
    dr.traverse(dr.llvm.ad.Float, dr.ADMode.Forward)
    grad = dr.grad(b)
    
    Dr.Jit also provides a higher level API that encapsulate this logic in a few
    different functions:
    
    - :py:func:`drjit.forward_from`, :py:func:`drjit.forward`, :py:func:`drjit.forward_to`
    - :py:func:`drjit.backward_from`, :py:func:`drjit.backward`, :py:func:`drjit.backward_to`
    
    Args:
    mode (ADMode): defines the enqueuing mode (backward or forward)
    
    *args (tuple): A variable-length list of Dr.Jit array instances, tensors,
    :ref:`custom data structures <custom-struct>`, sequences, or mappings.
    
    """
    ...

def epsilon(t):
    """
    
    Returns the machine epsilon.
    
    The machine epsilon gives an upper bound on the relative approximation
    error due to rounding in floating point arithmetic.
    
    Args:
    t (type): Python or Dr.Jit type determining whether to consider 32 or 64
    bits floating point precision.
    
    Returns:
    float: machine epsilon
    
    """
    ...

def eq(a, b):
    """
    
    Return the element-wise comparison of the two arguments
    
    This function falls back to ``==`` when none of the arguments are Dr.Jit
    arrays.
    
    Args:
    a (object): Input array.
    
    b (object): Input array.
    
    Returns:
    object: Output array, element-wise comparison of ``a`` and ``b``
    
    """
    ...

def erf(arg, /):
    """
    
    Evaluates the error function defined as
    
    .. math::
    
    \mathrm{erf}(x)=\frac{2}{\sqrt{\pi}}\int_0^x e^{-t^2}\,\mathrm{d}t.
    
    Requires a real-valued input array ``x``.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Value of the error function at the input value
    
    """
    ...

def erfinv(arg, /):
    """
    
    Evaluates the inverse of the error function :py:func:`drjit.erf`.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Value of the inverse of the error function at the input value
    
    """
    ...

def euler_to_quat(a, /):
    """
    
    euler_to_quat(arg, /)
    Converts Euler angles into a Dr.Jit quaternion.
    
    The order for input Euler angles must be XYZ.
    
    Args:
    arg (drjit.ArrayBase): A 3D Dr.Jit array type
    
    Returns:
    drjit.ArrayBase: A Dr.Jit quaternion representing the input Euler angles.
    
    """
    ...

def eval(*args):
    """
    
    Immediately evaluate the provided JIT variable(s)
    
    This function immediately invokes Dr.Jit's LLVM or CUDA backends to compile and
    then execute a kernel containing the *trace* of the specified variables,
    turning them into an explicit memory-based representation. The generated
    kernel(s) will also include previously scheduled computation. The function
    :py:func:`drjit.eval()` internally calls :py:func:`drjit.schedule()`---specifically,
    
    .. code-block::
    
    dr.eval(arg_1, arg_2, ...)
    
    is equivalent to
    
    .. code-block::
    
    dr.schedule(arg_1, arg_2, ...)
    dr.eval()
    
    Variable evaluation happens automatically as needed, hence it is rare that a
    user would need to call this function explicitly. Explicit evaluation can
    slightly improve performance in certain cases (the documentation of
    :py:func:`drjit.schedule()` shows an example of such a use case.)
    
    This function accepts a variable-length keyword argument and processes it
    as follows:
    
    - It recurses into sequences (``tuple``, ``list``, etc.)
    - It recurses into the values of mappings (``dict``, etc.)
    - It recurses into the fields of :ref:`custom data structures <custom-struct>`.
    
    During recursion, the function gathers all unevaluated Dr.Jit arrays. Evaluated
    arrays and incompatible types are ignored.
    
    Args:
    *args (tuple): A variable-length list of Dr.Jit array instances,
    :ref:`custom data structures <custom-struct>`, sequences, or mappings.
    The function will recursively traverse data structures to discover all
    Dr.Jit arrays.
    
    Returns:
    bool: ``True`` if a variable was evaluated, ``False`` if the operation did
    not do anything.
    
    """
    ...

def exp(arg, /):
    """
    
    exp(arg, /)
    Natural exponential approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU").
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Natural exponential of the input
    
    """
    ...

def exp2(arg, /):
    """
    
    exp2(arg, /)
    Base-2 exponential approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU").
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Base-2 exponential of the input
    
    """
    ...

def flag(arg0: drjit.JitFlag) -> int: ...
def flags() -> int: ...
def float32_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into an 32 bit floating point version.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3u`), it
    returns a *32 bit floating point* version (e.g. :py:class:`drjit.cuda.Array3f`).
    
    2. When the input isn't a type, it returns ``float32_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``float``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def float64_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into an 64 bit floating point version.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3u`), it
    returns a *64 bit floating point* version (e.g. :py:class:`drjit.cuda.Array3f64`).
    
    2. When the input isn't a type, it returns ``float64_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``float``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def float_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into a *floating point*
    version with the same element size.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3u64`), it
    returns an *floating point* version (e.g. :py:class:`drjit.cuda.Array3f64`).
    
    2. When the input isn't a type, it returns ``float_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``float``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def floor(arg, /):
    """
    
    floor(arg, /)
    Evaluate the floor, i.e. the largest integer <= arg.
    
    The function does not convert the type of the input array. A separate
    cast is necessary when integer output is desired.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Floor of the input
    
    """
    ...

def flush_kernel_cache() -> None: ...
def flush_malloc_cache() -> None: ...
def fma(a, b, c, /):
    """
    
    fma(arg0, arg1, arg2, /)
    Perform a *fused multiply-add* (FMA) operation.
    
    Given arguments ``arg0``, ``arg1``, and ``arg2``, this operation computes
    ``arg0`` * ``arg1`` + ``arg2`` using only one final rounding step. The
    operation is not only more accurate, but also more efficient, since FMA maps to
    a native machine instruction on platforms targeted by Dr.Jit.
    
    While FMA is traditionally a floating point operation, Dr.Jit also implements
    FMA for integer arrays and maps it onto dedicated instructions provided by the
    backend if possible (e.g. ``mad.lo.*`` for CUDA/PTX).
    
    Args:
    arg0 (float | drjit.ArrayBase): First multiplication operand
    arg1 (float | drjit.ArrayBase): Second multiplication operand
    arg2 (float | drjit.ArrayBase): Additive operand
    
    Returns:
    float | drjit.ArrayBase: Result of the FMA operation
    
    """
    ...

def forward(arg, flags=ADFlag.Default):
    """
    
    Forward propagates gradients from a provided Dr.Jit differentiable array.
    
    This function will first see the gradient value of the provided variable to ``1.0``
    before executing the AD graph traversal.
    
    An exception will be raised when the provided array doesn't have gradient tracking
    enabled or if it isn't an instance of a Dr.Jit differentiable array type.
    
    This function is an alias of :py:func:`drjit.forward_from`.
    
    Args:
    arg (object): A Dr.Jit differentiable array instance.
    
    flags (ADFlag | int): flags to control what should and should not be
    destructed during the traversal. The default value is ``ADFlag.Default``.
    
    """
    ...

def forward_from(arg, flags=ADFlag.Default):
    """
    
    Forward propagates gradients from a provided Dr.Jit differentiable array.
    
    This function will first see the gradient value of the provided variable to ``1.0``
    before executing the AD graph traversal.
    
    An exception will be raised when the provided array doesn't have gradient tracking
    enabled or if it isn't an instance of a Dr.Jit differentiable array type.
    
    Args:
    arg (object): A Dr.Jit differentiable array instance.
    
    flags (ADFlag | int): flags to control what should and should not be
    destructed during the traversal. The default value is ``ADFlag.Default``.
    
    """
    ...

def forward_to(*args, flags=ADFlag.Default):
    """
    
    Forward propagates gradients to a set of provided Dr.Jit differentiable arrays.
    
    Internally, the AD computational graph will be first traversed backward to find
    all potential source of gradient for the provided array. Then only the forward
    gradient propagation traversal takes place.
    
    The ``flags`` argument should be provided as a keyword argument for this function.
    
    An exception will be raised when the provided array doesn't have gradient tracking
    enabled or if it isn't an instance of a Dr.Jit differentiable array type.
    
    Args:
    *args (tuple): A variable-length list of Dr.Jit differentiable array, tensor,
    :ref:`custom data structure <custom-struct>`, sequences, or mapping.
    
    flags (ADFlag | int): flags to control what should and should not be
    destructed during the traversal. The default value is ``ADFlag.Default``.
    
    Returns:
    object: the gradient value associated to the output variables.
    
    """
    ...

four_pi = ...
"Convert a string or number to a floating point number, if possible."
def frob(a, /):
    """
    
    frob(arg, /)
    Returns the squared Frobenius norm of the provided Dr.Jit matrix.
    
    The squared Frobenius norm is defined as the sum of the squares of its elements:
    
    .. math::
    
    \sum_{i=1}^m \sum_{j=1}^n a_{i j}^2
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    Returns:
    drjit.ArrayBase: The squared Frobenius norm of the input matrix
    
    """
    ...

def full(dtype, value, shape=1):
    """
    
    Return a constant-valued instance of the desired type and shape
    
    This function can create constant-valued instances of various types. In
    particular, ``dtype`` can be:
    
    - A Dr.Jit array type like :py:class:`drjit.cuda.Array2f`. When ``shape``
    specifies a sequence, it must be compatible with static dimensions of the
    ``dtype``. For example, ``dr.full(dr.cuda.Array2f, value=1.0, shape=(3,
    100))`` fails, since the leading dimension is incompatible with
    :py:class:`drjit.cuda.Array2f`. When ``shape`` is an integer, it specifies
    the size of the last (dynamic) dimension, if available.
    
    - A tensorial type like :py:class:`drjit.scalar.TensorXf`. When ``shape``
    specifies a sequence (list/tuple/..), it determines the tensor rank and
    shape. When ``shape`` is an integer, the function creates a rank-1 tensor of
    the specified size.
    
    - A :ref:`custom data structure <custom-struct>`. In this case,
    :py:func:`drjit.full()` will invoke itself recursively to initialize
    each field of the data structure.
    
    - A scalar Python type like ``int``, ``float``, or ``bool``. The ``shape``
    parameter is ignored in this case.
    
    Args:
    dtype (type): Desired Dr.Jit array type, Python scalar type, or
    :ref:`custom data structure <custom-struct>`.
    
    value (object): An instance of the underlying scalar type
    (``float``/``int``/``bool``, etc.) that will be used to initialize the
    array contents.
    
    shape (Sequence[int] | int): Shape of the desired array
    
    Returns:
    object: A instance of type ``dtype`` filled with ``value``
    
    """
    ...

def gather(dtype, source, index, active=True):
    """
    
    Gather values from a flat array or nested data structure
    
    This function performs a *gather* (i.e., indirect memory read) from
    ``source`` at position ``index``. It expects a ``dtype`` argument and will
    return an instance of this type. The optional ``active`` argument can be
    used to disable some of the components, which is useful when not all indices
    are valid; the corresponding output will be zero in this case.
    
    This operation can be used in the following different ways:
    
    1. When ``dtype`` is a 1D Dr.Jit array like :py:class:`drjit.llvm.ad.Float`,
    this operation implements a parallelized version of the Python array
    indexing expression ``source[index]`` with optional masking. Example:
    
    .. code-block::
    
    source = dr.cuda.Float([...])
    index = dr.cuda.UInt([...]) # Note: negative indices are not permitted
    result = dr.gather(dtype=type(source), source=source, index=index)
    
    2. When ``dtype`` is a more complex type (e.g. a :ref:`custom source structure <custom-struct>`,
    nested Dr.Jit array, tuple, list, dictionary, etc.), the behavior depends:
    
    - When ``type(source)`` matches ``dtype``, the the gather operation threads
    through entries and invokes itself recursively. For example, the gather
    operation in
    
    .. code-block::
    
    result = dr.cuda.Array3f(...)
    index = dr.cuda.UInt([...])
    result = dr.gather(dr.cuda.Array3f, source, index)
    
    is equivalent to
    
    .. code-block::
    
    result = dr.cuda.Array3f(
    dr.gather(dr.cuda.Float, source.x, index),
    dr.gather(dr.cuda.Float, source.y, index),
    dr.gather(dr.cuda.Float, source.z, index)
    )
    
    - Otherwise, the operation reconstructs the requested ``dtype`` from a flat
    ``source`` array, using C-style ordering with a suitably modified
    ``index``. For example, the gather below reads 3D vectors from a 1D
    array.
    
    
    .. code-block::
    
    source = dr.cuda.Float([...])
    index = dr.cuda.UInt([...])
    result = dr.gather(dr.cuda.Array3f, source, index)
    
    and is equivalent to
    
    .. code-block::
    
    result = dr.cuda.Vector3f(
    dr.gather(dr.cuda.Float, source, index*3 + 0),
    dr.gather(dr.cuda.Float, source, index*3 + 1),
    dr.gather(dr.cuda.Float, source, index*3 + 2)
    )
    
    .. danger::
    
    The indices provided to this operation are unchecked. Out-of-bounds
    reads are undefined behavior (if not disabled via the ``active``
    parameter) and may crash the application. Negative indices are not
    permitted.
    
    Args:
    dtype (type): The desired output type (typically equal to ``type(source)``,
    but other variations are possible as well, see the description above.)
    
    source (object): The object from which data should be read (typically a
    1D Dr.Jit array, but other variations are possible as well, see the
    description above.)
    
    index (object): a 1D dynamic unsigned 32-bit Dr.Jit array (e.g.,
    :py:class:`drjit.scalar.ArrayXu` or :py:class:`drjit.cuda.UInt`)
    specifying gather indices. Dr.Jit will attempt an implicit conversion
    if another type is provided. active
    
    (object): an optional 1D dynamic Dr.Jit mask array (e.g.,
    :py:class:`drjit.scalar.ArrayXb` or :py:class:`drjit.cuda.Bool`)
    specifying active components. Dr.Jit will attempt an implicit
    conversion if another type is provided. The default is `True`.
    
    Returns:
    object: An instance of type ``dtype`` containing the result of the gather operation.
    
    """
    ...

def get_cmake_dir(): ...
def grad(arg, preserve_type=True):
    """
    
    Return the gradient value associated to a given variable.
    
    When the variable doesn't have gradient tracking enabled, this function
    returns ``0``.
    
    For all input variables that are not Dr.Jit arrays or mapping and sequences,
    thi function returns ``None``.
    
    Args:
    arg (object): An arbitrary Dr.Jit array, tensor,
    :ref:`custom data structure <custom-struct>`, sequences, or mapping.
    
    preserve_type (bool): Defines whether the returned variable should
    preserve the type of the input variable.
    
    Returns:
    object: the gradient value associated to the input variable.
    
    """
    ...

def grad_enabled(*args):
    """
    
    Return whether gradient tracking is enabled on any of the given variables.
    
    Args:
    *args (tuple): A variable-length list of Dr.Jit array instances,
    :ref:`custom data structures <custom-struct>`, sequences, or mappings.
    The function will recursively traverse data structures to discover all
    Dr.Jit arrays.
    
    Returns:
    bool: ``True`` if any variable has gradient tracking enabled, ``False`` otherwise.
    
    """
    ...

def graphviz(as_str=False):
    """
    
    Assembles a graphviz diagram for the computational graph trace by the JIT.
    
    Args:
    as_str (bool): whether the function should return the graphviz object as
    a string representation or not.
    
    Returns:
    object: the graphviz obj (or its string representation).
    
    """
    ...

def graphviz_ad(as_str=False):
    """
    
    Assembles a graphviz diagram for the computational graph trace by the AD system.
    
    Args:
    as_str (bool): whether the function should return the graphviz object as
    a string representation or not.
    
    Returns:
    object: the graphviz obj (or its string representation).
    
    """
    ...

def has_backend(arg0: drjit.JitBackend) -> int: ...
def hypot(a, b):
    """
    
    Computes :math:`\sqrt{x^2+y^2}` while avoiding overflow and underflow.
    
    Args:
    arg (list | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Hypotenuse value
    
    """
    ...

def identity(dtype, size=1):
    """
    
    Return the identity array of the desired type and size
    
    This function can create identity instances of various types. In
    particular, ``dtype`` can be:
    
    - A Dr.Jit matrix type (like :py:class:`drjit.cuda.Matrix4f`).
    
    - A Dr.Jit complex type (like :py:class:`drjit.cuda.Quaternion4f`).
    
    - Any other Dr.Jit array type. In this case this function is equivalent to ``full(dtype, 1, size)``
    
    - A scalar Python type like ``int``, ``float``, or ``bool``. The ``size``
    parameter is ignored in this case.
    
    Args:
    dtype (type): Desired Dr.Jit array type, Python scalar type, or
    :ref:`custom data structure <custom-struct>`.
    
    value (object): An instance of the underlying scalar type
    (``float``/``int``/``bool``, etc.) that will be used to initialize the
    array contents.
    
    size (int): Size of the desired array | matrix
    
    Returns:
    object: The identity array of type ``dtype`` of size ``size``
    
    """
    ...

def imag(arg, /):
    """
    
    Return the imaginary part of a complex Dr.Jit array.
    
    When the provided array isn't an instance of :py:class:`drjit.Complex` or
    :py:class:`drjit.Quaternion`, this function returns the input unchanged.
    
    Args:
    arg (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | drjit.ArrayBase: Imaginary part of the input array
    
    """
    ...

inf = ...
"Convert a string or number to a floating point number, if possible."
def int32_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into a *signed 32 bit*
    version.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3f`), it
    returns an *signed 32 bit* version (e.g. :py:class:`drjit.cuda.Array3i`).
    
    2. When the input isn't a type, it returns ``int32_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``int``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def int64_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into an *signed 64 bit* version.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3f`), it
    returns an *signed 64 bit* version (e.g. :py:class:`drjit.cuda.Array3i64`).
    
    2. When the input isn't a type, it returns ``int64_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``int``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def int_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into a *signed integer*
    version with the same element size.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3f64`), it
    returns an *signed integer* version (e.g. :py:class:`drjit.cuda.Array3u64`).
    
    2. When the input isn't a type, it returns ``int_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``int``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

inv_four_pi = ...
"Convert a string or number to a floating point number, if possible."
inv_log_two = ...
"Convert a string or number to a floating point number, if possible."
inv_pi = ...
"Convert a string or number to a floating point number, if possible."
inv_sqrt_four_pi = ...
"Convert a string or number to a floating point number, if possible."
inv_sqrt_pi = ...
"Convert a string or number to a floating point number, if possible."
inv_sqrt_two = ...
"Convert a string or number to a floating point number, if possible."
inv_sqrt_two_pi = ...
"Convert a string or number to a floating point number, if possible."
inv_two_pi = ...
"Convert a string or number to a floating point number, if possible."
def inverse(arg, /):
    """
    
    inverse(arg, /)
    Returns the inverse matrix of the provided Dr.Jit matrix.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    Returns:
    drjit.ArrayBase: The inverse matrix of the input matrix
    
    """
    ...

def inverse_transpose(m, /):
    """
    
    inverse_transpose(arg, /)
    Returns the inverse transpose of the provided Dr.Jit matrix.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    Returns:
    drjit.ArrayBase: The inverse transposed matrix
    
    """
    ...

def is_arithmetic_v(arg, /):
    """
    
    is_arithmetic_v(arg, /)
    Check whether the input array instance or type is an arithmetic Dr.Jit array
    or a Python ``int`` or ``float`` value/type.
    
    Note that a mask type (e.g. ``bool``, :py:class:`drjit.scalar.Array2b`, etc.)
    is *not* considered to be arithmetic.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents an arithmetic Dr.Jit array or
    Python ``int`` or ``float`` instance or type.
    
    """
    ...

def is_array_v(arg, /):
    """
    
    is_array_v(arg, /)
    Check if the input is a Dr.Jit array instance or type
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` or type(``arg``) is a Dr.Jit array type, and ``False`` otherwise
    
    """
    ...

def is_complex_v(arg, /):
    """
    
    is_complex_v(arg, /)
    Check whether the input is a Dr.Jit array instance or type representing a complex number.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if the test was successful, and ``False`` otherwise.
    
    """
    ...

def is_cuda_v(arg, /):
    """
    
    is_cuda_v(arg, /)
    Check whether the input is a Dr.Jit CUDA array instance or type.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents an array type from the
    ``drjit.cuda.*`` namespace, and ``False`` otherwise.
    
    """
    ...

def is_diff_v(arg, /):
    """
    
    is_diff_v(arg, /)
    Check whether the input is a differentiable Dr.Jit array instance or type.
    
    Note that this is a type-based statement that is unrelated to mathematical
    differentiability. For example, the integral type :py:class:`drjit.cuda.ad.Int`
    from the CUDA AD namespace satisfies ``is_diff_v(..) = 1``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents an array type from the
    ``drjit.[cuda/llvm].ad.*`` namespace, and ``False`` otherwise.
    
    """
    ...

def is_dynamic_array_v(a): ...
def is_dynamic_v(a): ...
def is_float_v(arg, /):
    """
    
    is_float_v(arg, /)
    Check whether the input array instance or type is a Dr.Jit floating point array
    or a Python ``float`` value/type.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents a Dr.Jit floating point array or
    Python ``float`` instance or type.
    
    """
    ...

def is_integral_v(arg, /):
    """
    
    is_integral_v(arg, /)
    Check whether the input array instance or type is an integral Dr.Jit array
    or a Python ``int`` value/type.
    
    Note that a mask array is not considered to be integral.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents an integral Dr.Jit array or
    Python ``int`` instance or type.
    
    """
    ...

def is_iterable_v(a): ...
def is_jit_v(arg, /):
    """
    
    is_jit_v(arg, /)
    Check whether the input array instance or type represents a type that
    undergoes just-in-time compilation.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents an array type from the
    ``drjit.cuda.*`` or ``drjit.llvm.*`` namespaces, and ``False`` otherwise.
    
    """
    ...

def is_llvm_v(arg, /):
    """
    
    is_llvm_v(arg, /)
    Check whether the input is a Dr.Jit LLVM array instance or type.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents an array type from the
    ``drjit.llvm.*`` namespace, and ``False`` otherwise.
    
    """
    ...

def is_mask_v(arg, /):
    """
    
    is_mask_v(arg, /)
    Check whether the input array instance or type is a Dr.Jit mask array or a
    Python ``bool`` value/type.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents a Dr.Jit mask array or Python ``bool``
    instance or type.
    
    """
    ...

def is_matrix_v(arg, /):
    """
    
    is_matrix_v(arg, /)
    Check whether the input is a Dr.Jit array instance or type representing a matrix.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if the test was successful, and ``False`` otherwise.
    
    """
    ...

def is_quaternion_v(arg, /):
    """
    
    is_quaternion_v(arg, /)
    Check whether the input is a Dr.Jit array instance or type representing a quaternion.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if the test was successful, and ``False`` otherwise.
    
    """
    ...

def is_signed_v(arg, /):
    """
    
    is_signed_v(arg, /)
    Check whether the input array instance or type is an signed Dr.Jit array
    or a Python ``int`` or ``float`` value/type.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents an signed Dr.Jit array or
    Python ``int`` or ``float`` instance or type.
    
    """
    ...

def is_special_v(arg, /):
    """
    
    is_special_v(arg, /)
    Check whether the input is a *special* Dr.Jit array instance or type.
    
    A *special* array type requires precautions when performing arithmetic
    operations like multiplications (complex numbers, quaternions, matrices).
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if the test was successful, and ``False`` otherwise.
    
    """
    ...

def is_static_array_v(a): ...
def is_struct_v(arg, /):
    """
    
    is_struct_v(arg, /)
    Check if the input is a Dr.Jit-compatible data structure
    
    Custom data structures can be made compatible with various Dr.Jit operations by
    specifying a ``DRJIT_STRUCT`` member. See the section on :ref:`custom data
    structure <custom-struct>` for details. This type trait can be used to check
    for the existence of such a field.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` has a ``DRJIT_STRUCT`` member
    
    """
    ...

def is_tensor_v(arg, /):
    """
    
    is_tensor_v(arg, /)
    Check whether the input is a Dr.Jit array instance or type representing a tensor.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if the test was successful, and ``False`` otherwise.
    
    """
    ...

def is_texture_v(a): ...
def is_unsigned_v(arg, /):
    """
    
    is_unsigned_v(arg, /)
    Check whether the input array instance or type is an unsigned integer Dr.Jit
    array or a Python ``bool`` value/type (masks and boolean values are also
    considered to be unsigned).
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    bool: ``True`` if ``arg`` represents an unsigned Dr.Jit array or
    Python ``bool`` instance or type.
    
    """
    ...

def is_vector_v(a): ...
def isfinite(arg, /):
    """
    
    Performs an element-wise test that checks whether values are finite and not
    equal to *NaN* (Not a Number)
    
    Args:
    arg (object): A Dr.Jit array or other kind of numeric sequence type.
    
    Returns:
    :py:func:`mask_t(arg) <mask_t>`: A mask value describing the result of the test
    
    """
    ...

def isinf(arg, /):
    """
    
    Performs an element-wise test for positive or negative infinity
    
    Args:
    arg (object): A Dr.Jit array or other kind of numeric sequence type.
    
    Returns:
    :py:func:`mask_t(arg) <mask_t>`: A mask value describing the result of the test
    
    """
    ...

def isnan(arg, /):
    """
    
    Performs an element-wise test for *NaN* (Not a Number) values
    
    Args:
    arg (object): A Dr.Jit array or other kind of numeric sequence type.
    
    Returns:
    :py:func:`mask_t(arg) <mask_t>`: A mask value describing the result of the test.
    
    """
    ...

def isolate_grad(when=True):
    """
    
    Context manager to temporarily isolate outside world from AD traversals.
    
    Dr.Jit provides isolation boundaries to postpone AD traversals steps leaving a
    specific scope. For instance this function is used internally to implement
    differentiable loops and polymorphic calls.
    
    """
    ...

def kernel_history(types: list = []) -> list: ...
def kernel_history_clear() -> None: ...
def label(arg):
    """
    
    Returns the label of a given Dr.Jit array.
    
    Args:
    arg (object): a Dr.Jit array instance.
    
    Returns:
    str: the label of the given variable.
    
    """
    ...

def largest(t):
    """
    
    Returns the largest normalized floating point value.
    
    Args:
    t (type): Python or Dr.Jit type determining whether to consider 32 or 64
    bits floating point precision.
    
    Returns:
    float: largest normalized floating point value
    
    """
    ...

def leaf_array_t(arg):
    """
    
    Extracts a leaf array type underlying a Python object tree, with a preference
    for differentiable arrays.
    
    This function implements the following set of behaviors:
    
    1. When the input isn't a type, it returns ``leaf_array_t(type(arg))``.
    
    2. When invoked with a Dr.Jit array type, returns the lowest-level array type
    underlying a potentially nested array.
    
    3. When invoked with a sequence, mapping or custom data structure made of Dr.Jit arrays,
    examines underlying Dr.Jit array types and returns the lowest-level array type with
    a preference for differentiable arrays and floating points arrays.
    E.g. when passing a list containing arrays of type :py:class:`drjit.cuda.ad.Float` and :py:class:`drjit.cuda.UInt`,
    the function will return :py:class:`drjit.cuda.ad.Float`.
    
    4. Otherwise returns ``None``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the extraction as described above.
    
    """
    ...

def lerp(a, b, t, /):
    """
    
    lerp(a, b, t, /)
    Blends between the values ``a`` and ``b`` using the expression :math:`a \cdot (1 - t) + b \cdot t`
    
    Args:
    a (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    b (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    t (float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | int | drjit.ArrayBase: Blended value
    
    """
    ...

def lgamma(arg, /):
    """
    
    Evaluates the natural logarithm of the Gamma function.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Value of the natural logarithm of the Gamma function at the input value
    
    """
    ...

def linspace(dtype, start, stop, num=1, endpoint=True):
    """
    
    This function generates an evenly spaced floating point sequence of size
    ``num`` covering the interval [``start``, ``stop``].
    
    Args:
    dtype (type): Desired Dr.Jit array type. The ``dtype`` must refer to a
    dynamically sized 1D Dr.Jit floating point array, such as
    :py:class:`drjit.scalar.ArrayXf` or :py:class:`drjit.cuda.Float`.
    
    start (float): Start of the interval.
    
    stop (float): End of the interval.
    
    num (int): Number of samples to generate.
    
    endpoint (bool): Should the interval endpoint be included? The default is `True`.
    
    Returns:
    object: The computed sequence of type ``dtype``.
    
    """
    ...


from .stubs import llvm as llvm

def llvm_version() -> str: ...
def log(arg, /):
    """
    
    log(arg, /)
    Natural exponential approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU").
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Natural logarithm of the input
    
    """
    ...

def log2(arg, /):
    """
    
    log2(arg, /)
    Base-2 exponential approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU").
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Base-2 logarithm of the input
    
    """
    ...

def log2i(arg, /):
    """
    
    Return the floor of the base-two logarithm.
    
    This function assumes that ``arg`` is an integer array.
    
    Args:
    arg (int | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    int | drjit.ArrayBase: number of leading zero bits in the input array
    
    """
    ...

def log_level() -> drjit.LogLevel: ...
log_two = ...
"Convert a string or number to a floating point number, if possible."
def lzcnt(arg, /):
    """
    
    Return the number of leading zero bits.
    
    This function assumes that ``arg`` is an integer array.
    
    Args:
    arg (int | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    int | drjit.ArrayBase: number of leading zero bits in the input array
    
    """
    ...

def make_opaque(*args): ...
def malloc_clear_statistics() -> None: ...
def mask_t(arg, /):
    """
    
    mask_t(arg, /)
    Return the *mask type* associated with the provided Dr.Jit array or type (i.e., the
    type produced by comparisons involving the argument).
    
    When the input is not a Dr.Jit array or type, the function returns the scalar
    Python ``bool`` type. The following assertions illustrate the behavior of
    :py:func:`mask_t`.
    
    
    .. code-block::
    
    assert dr.mask_t(dr.scalar.Array3f) is dr.scalar.Array3b
    assert dr.mask_t(dr.cuda.Array3f) is dr.cuda.Array3b
    assert dr.mask_t(dr.cuda.Matrix4f) is dr.cuda.Array44b
    assert dr.mask_t("test") is bool
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Returns the mask type associated with the input or ``bool`` when the
    input is not a Dr.Jit array.
    
    """
    ...

def matrix_to_quat(m, /):
    """
    
    matrix_to_quat(arg, /)
    Converts a 3x3 or 4x4 homogeneous containing
    a pure rotation into a rotation quaternion.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    Returns:
    drjit.ArrayBase: The Dr.Jit quaternion corresponding the to input matrix.
    
    """
    ...

def max(arg, /):
    """
    
    max(arg, /) -> float | int | drjit.ArrayBase
    Compute the maximum value in the provided input.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Maximum of the input
    
    """
    ...

def max_nested(arg, /):
    """
    
    max_nested(arg, /) -> float | int
    Iterates :py:func:`max` until the return value is reduced to a single value.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Maximum scalar value of the input
    
    """
    ...

def maximum(a, b, /):
    """
    
    maximum(arg0, arg1, /) -> float | int | drjit.ArrayBase
    Compute the element-wise maximum value of the provided inputs.
    
    This function returns a result of the type ``type(arg0 + arg1)`` (i.e.,
    according to the usual implicit type conversion rules).
    
    Args:
    arg0 (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    arg1 (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Maximum of the input(s)
    
    """
    ...

def mean(arg, /):
    """
    
    mean(arg, /) -> float | drjit.ArrayBase
    Compute the mean of all array elements.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Mean of the input
    
    """
    ...

def mean_nested(arg, /):
    """
    
    mean_nested(arg, /) -> float | int
    Iterates :py:func:`mean` until the return value is reduced to a single value.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Mean of the input
    
    """
    ...

def meshgrid(*args, indexing='xy'):
    """
    
    Creates a grid coordinates based on the coordinates contained in the
    provided one-dimensional arrays.
    
    The indexing keyword argument allows this function to support both matrix
    and Cartesian indexing conventions. If given the string 'ij', it will return
    a grid coordinates with matrix indexing. If given 'xy', it will return a
    grid coordinates with Cartesian indexing.
    
    .. code-block::
    
    import drjit as dr
    
    x, y = dr.meshgrid(
    dr.arange(dr.llvm.UInt, 4),
    dr.arange(dr.llvm.UInt, 4)
    )
    
    # x = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
    # y = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
    
    Args:
    args (drjit.ArrayBase): Dr.Jit one-dimensional coordinate arrays
    
    indexing (str): Specifies the indexing conventions
    
    Returns:
    tuple: Grid coordinates
    
    """
    ...

def migrate(a, type_): ...
def min(arg, /):
    """
    
    min(arg, /) -> float | int | drjit.ArrayBase
    Compute the minimum value in the provided input.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Minimum of the input
    
    """
    ...

def min_nested(arg, /):
    """
    
    min_nested(arg, /) -> float | int
    Iterates :py:func:`min` until the return value is reduced to a single value.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Minimum scalar value of the input
    
    """
    ...

def minimum(a, b, /):
    """
    
    minimum(arg0, arg1, /) -> float | int | drjit.ArrayBase
    Compute the element-wise minimum value of the provided inputs.
    
    This function returns a result of the type ``type(arg0 + arg1)`` (i.e.,
    according to the usual implicit type conversion rules).
    
    Args:
    arg0 (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    arg1 (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Minimum of the input(s)
    
    """
    ...

def mulhi(a, b): ...
def mulsign(a, b, /):
    """
    
    mulsign(arg0, arg1, /)
    Multiply ``arg0`` by the sign of ``arg1` element-wise.
    
    This function is equivalent to
    
    .. code-block::
    
    a * dr.sign(b)
    
    Args:
    arg0 (int | float | drjit.ArrayBase): A Python or Dr.Jit array to multiply the sign of
    arg1 (int | float | drjit.ArrayBase): A Python or Dr.Jit array to take the sign from
    
    Returns:
    float | int | drjit.ArrayBase: The values of ``arg0`` multiplied with the sign of ``arg1``
    
    """
    ...

nan = ...
"Convert a string or number to a floating point number, if possible."
def neq(a, b):
    """
    
    Return the element-wise not-equal comparison of the two arguments
    
    This function falls back to ``!=`` when none of the arguments are Dr.Jit
    arrays.
    
    Args:
    a (object): Input array.
    
    b (object): Input array.
    
    Returns:
    object: Output array, element-wise comparison of ``a != b``
    
    """
    ...

def none(arg, /):
    """
    
    none(arg, /) -> bool | drjit.ArrayBase
    Computes whether none of the input elements evaluate to ``True``.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Boolean array
    
    """
    ...

def none_nested(arg, /):
    """
    
    none_nested(arg, /) -> bool
    Iterates :py:func:`none` until the type of the return value no longer
    changes. This can be used to reduce a nested mask array into a single
    value.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Boolean
    
    """
    ...

def norm(arg, /):
    """
    
    norm(arg, /) -> float | int | drjit.ArrayBase
    Computes the norm of an array.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (list | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Norm of the input
    
    """
    ...

def normalize(arg, /):
    """
    
    normalize(arg, /) -> drjit.ArrayBase
    Normalizes the provided array.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (list | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Normalized input array
    
    """
    ...

def one_minus_epsilon(t):
    """
    
    Returns one minus machine epsilon value.
    
    Args:
    t (type): Python or Dr.Jit type determining whether to consider 32 or 64
    bits floating point precision.
    
    Returns:
    float: one minus machine epsilon value
    
    """
    ...

def ones(dtype, shape=1):
    """
    
    Return a constant-valued instance of the desired type and shape filled with ones.
    
    This function can create constant-valued instances of various types. In
    particular, ``dtype`` can be:
    
    - A Dr.Jit array type like :py:class:`drjit.cuda.Array2f`. When ``shape``
    specifies a sequence, it must be compatible with static dimensions of the
    ``dtype``. For example, ``dr.ones(dr.cuda.Array2f, shape=(3, 100))`` fails,
    since the leading dimension is incompatible with
    :py:class:`drjit.cuda.Array2f`. When ``shape`` is an integer, it specifies
    the size of the last (dynamic) dimension, if available.
    
    - A tensorial type like :py:class:`drjit.scalar.TensorXf`. When ``shape``
    specifies a sequence (list/tuple/..), it determines the tensor rank and
    shape. When ``shape`` is an integer, the function creates a rank-1 tensor of
    the specified size.
    
    - A :ref:`custom data structure <custom-struct>`. In this case,
    :py:func:`drjit.ones()` will invoke itself recursively to initialize
    each field of the data structure.
    
    - A scalar Python type like ``int``, ``float``, or ``bool``. The ``shape``
    parameter is ignored in this case.
    
    Args:
    dtype (type): Desired Dr.Jit array type, Python scalar type, or
    :ref:`custom data structure <custom-struct>`.
    
    shape (Sequence[int] | int): Shape of the desired array
    
    Returns:
    object: A instance of type ``dtype`` filled with ones
    
    """
    ...

def opaque(type_, value, shape=1): ...
def or_(a, b): ...
pi = ...
"Convert a string or number to a floating point number, if possible."
def polar_decomp(arg, it=10):
    """
    
    Returns the polar decomposition of the provided Dr.Jit matrix.
    
    The polar decomposition separates the matrix into a rotation followed by a
    scaling along each of its eigen vectors. This decomposition always exists
    for square matrices.
    
    The implementation relies on an iterative algorithm, where the number of
    iterations can be controlled by the argument ``it`` (tradeoff between
    precision and computational cost).
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    it (int): Number of iterations to be taken by the algorithm.
    
    Returns:
    tuple: A tuple containing the rotation matrix and the scaling matrix resulting from the decomposition.
    
    """
    ...

def popcnt(arg, /):
    """
    
    Return the number of nonzero zero bits.
    
    This function assumes that ``arg`` is an integer array.
    
    Args:
    arg (int | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    int | drjit.ArrayBase: number of nonzero zero bits in the input array
    
    """
    ...

def power(a, b):
    """
    
    Raise the first input value to the power given as second input value.
    
    This function handles both the case of integer and floating-point exponents.
    Moreover, when the exponent is an array, the function will calculate the
    element-wise powers of the input values.
    
    Args:
    x (int | float | drjit.ArrayBase): A Python or Dr.Jit array type as input value
    y (int | float | drjit.ArrayBase): A Python or Dr.Jit array type as exponent
    
    Returns:
    int | float | drjit.ArrayBase: input value raised to the power
    
    """
    ...

def prefix_sum(value, exclusive=True):
    """
    
    Compute an exclusive or inclusive prefix sum of the 1D input array.
    
    By default, the function returns an output array :math:`\mathbf{y}` of the
    same size as the input :math:`\mathbf{x}`, where
    
    .. math::
    
    y_i = \sum_{i=0}^{i-1} x_i.
    
    which is known as an *exclusive* prefix sum, as each element of the output
    array excludes the corresponding input in its sum. When the ``exclusive``
    argument is set to ``False``, the function instead returns an *inclusive*
    prefix sum defined as
    
    .. math::
    
    y_i = \sum_{i=0}^i x_i.
    
    There is also a convenience alias :py:func:`drjit.cumsum` that computes an
    inclusive sum analogous to various other nd-array frameworks.
    
    Not all numeric data types are supported by :py:func:`prefix_sum`:
    presently, the function accepts ``Int32``, ``UInt32``, ``UInt64``,
    ``Float32``, and ``Float64``-typed arrays.
    
    The CUDA backend implementation for "large" numeric types (``Float64``,
    ``UInt64``) has the following technical limitation: when reducing 64-bit
    integers, their values must be smaller than 2**62. When reducing double
    precision arrays, the two least significant mantissa bits are clamped to
    zero when forwarding the prefix from one 512-wide block to the next (at a
    *very minor*, probably negligible loss in accuracy). See the implementation
    for details on the rationale of this limitation.
    
    Args:
    value (drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    exclusive (bool): Specifies whether or not the prefix sum should
    be exclusive (the default) or inclusive.
    
    Returns:
    drjit.ArrayBase: An array of the same type containing the computed prefix sum.
    
    """
    ...

def print_threshold():
    """
    
    Return the maximum number of entries displayed when printing an array
    
    """
    ...

def printf_async(fmt, *args, active=True):
    """
    
    Print the specified variable contents from the kernel asynchronously.
    
    This function inserts a print statement directly into the kernel being
    generated. Note that this may produce a very large volume of output,
    and a nonzero ``active`` parameter can be supplied to suppress it based
    on condition.
    
    Args:
    fmt (str): The string to be printed. It might contain *format specifiers*
    (e.g. subsequences beginning with %)
    
    *args (tuple): Additional array arguments to be formatted and inserted
    in the printed string replacing their respective specifiers.
    
    active (bool | drjit.ArrayBase): Mask array to suppress printing specific
    elements in the supplied additional arrays.
    
    """
    ...

def prod(arg, /):
    """
    
    prod(arg, /) -> float | int | drjit.ArrayBase
    Compute the product of all array elements.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Product of the input
    
    """
    ...

def prod_nested(arg, /):
    """
    
    prod_nested(arg, /) -> float | int
    Iterates :py:func:`prod` until the return value is reduced to a single value.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Product of the input
    
    """
    ...

def quat_to_euler(q, /):
    """
    
    quat_to_euler(arg, /)
    Converts a quaternion into its Euler angles representation.
    
    The order for Euler angles is XYZ.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit quaternion type
    
    Returns:
    drjit.ArrayBase: A 3D Dr.Jit array containing the Euler angles.
    
    """
    ...

def quat_to_matrix(q, size=4):
    """
    
    quat_to_matrix(arg, size=4)
    Converts a quaternion into its matrix representation.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit quaternion type
    size (int): Controls whether to construct a 3x3 or 4x4 matrix.
    
    Returns:
    drjit.ArrayBase: The Dr.Jit matrix corresponding the to input quaternion.
    
    """
    ...

def rad2deg(arg, /):
    """
    
    rad2deg(arg, /) -> float | drjit.ArrayBase
    Convert angles from radians to degrees.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    The equivalent angle in degrees.
    
    """
    ...

def ravel(array, order='A'):
    """
    
    Convert the input into a contiguous flat array
    
    This operation takes a Dr.Jit array, typically with some static and some
    dynamic dimensions (e.g., :py:class:`drjit.cuda.Array3f` with shape `3xN`),
    and converts it into a flattened 1D dynamically sized array (e.g.,
    :py:class:`drjit.cuda.Float`) using either a C or Fortran-style ordering
    convention.
    
    It can also convert Dr.Jit tensors into a flat representation, though only
    C-style ordering is supported in this case.
    
    For example,
    
    .. code-block::
    
    x = dr.cuda.Array3f([1, 2], [3, 4], [5, 6])
    y = dr.ravel(x, order=...)
    
    will produce
    
    - ``[1, 3, 5, 2, 4, 6]`` with ``order='F'`` (the default for Dr.Jit arrays),
    which means that X/Y/Z components alternate.
    - ``[1, 2, 3, 4, 5, 6]`` with ``order='C'``, in which case all X coordinates
    are written as a contiguous block followed by the Y- and then Z-coordinates.
    
    .. danger::
    
    Currently C-style ordering is not implemented for tensor types.
    
    Args:
    array (drjit.ArrayBase): An arbitrary Dr.Jit array or tensor
    
    order (str): A single character indicating the index order. ``'F'``
    indicates column-major/Fortran-style ordering, in which case the first
    index changes at the highest frequency. The alternative ``'C'`` specifies
    row-major/C-style ordering, in which case the last index changes at the
    highest frequency. The default value ``'A'`` (automatic) will use F-style
    ordering for arrays and C-style ordering for tensors.
    
    Returns:
    object: A dynamic 1D array containing the flattened representation of
    ``array`` with the desired ordering. The type of the return value depends
    on the type of the input. When ``array`` is already contiguous/flattened,
    this function returns it without making a copy.
    
    """
    ...

def rcp(arg, /):
    """
    
    rcp(arg, /)
    Evaluate the reciprocal (1 / arg) of the provided input.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU"). The result is slightly
    approximate in this case (refer to the documentation of the instruction
    `rcp.approx.ftz.f32` in the NVIDIA PTX manual for details).
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Reciprocal of the input
    
    """
    ...

def real(arg, /):
    """
    
    Return the real part of a complex Dr.Jit array.
    
    When the provided array isn't an instance of :py:class:`drjit.Complex` or
    :py:class:`drjit.Quaternion`, this function returns the input unchanged.
    
    Args:
    arg (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | drjit.ArrayBase: Real part of the input array
    
    """
    ...

def recip_overflow(t):
    """
    
    Returns the reciprocal overflow threshold value.
    
    Any numbers below this threshold will overflow to infinity when a reciprocal
    is evaluated.
    
    Args:
    t (type): Python or Dr.Jit type determining whether to consider 32 or 64
    bits floating point precision.
    
    Returns:
    float: reciprocal overflow threshold value
    
    """
    ...

def registry_clear() -> None: ...
def registry_trim() -> None: ...
def reinterpret_array_v(dtype, value):
    """
    
    Reinterpret the provided Dr.Jit array/tensor into a specified type.
    
    Args:
    dtype (type): Target type for the reinterpretation.
    
    value (object): Dr.Jit array or tensor to reinterpret.
    
    Returns:
    object: Result of the conversion as described above.
    
    """
    ...

def repeat(array, count: int):
    """
    
    This function constructs an Dr.Jit array by repeating the elements of ``arg``
    ``count`` times.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit type
    count (int): Number of repetitions for the elements
    
    Returns:
    object: Output array where the elements where repeated.
    
    """
    ...

def replace_grad(dst, src):
    """
    
    Replace the gradient value of ``dst`` with the one of ``src``.
    
    Broadcasting is applied to ``dst`` if necessary to match the type of ``src``.
    
    Args:
    dst (object): An arbitrary Dr.Jit array, tensor, or scalar builtin instance.
    
    src (object): An differentiable Dr.Jit array or tensor.
    
    Returns:
    object: the variable with the replaced gradients.
    
    """
    ...

def resize(arg, size):
    """
    
    resize(arg, size)
    Resize in-place the provided Dr.Jit array, tensor, or
    :ref:`custom data structure <custom-struct>` to a new size.
    
    The provided variable must have a size of zero or one originally otherwise
    this function will fail.
    
    When the provided variable doesn't have a size of 1 and its size exactly
    matches ``size`` the function does nothing. Otherwise, it fails.
    
    Args:
    arg (drjit.ArrayBase): An arbitrary Dr.Jit array, tensor, or
    :ref:`custom data structure <custom-struct>` to be resized
    
    size (int): The new size
    
    """
    ...

def resume_grad(*args, when=True):
    """
    
    resume_grad(*args, when = True)
    Context manager for temporally resume derivative tracking.
    
    Dr.Jit's AD layer keeps track of a set of variables for which derivative
    tracking is currently enabled. Using this context manager is it possible to
    define a scope in which variables will be added to that set, thereby controlling
    what derivative terms should be generated in that scope.
    
    The variables to be added to the current set of enabled variables can be
    provided as function arguments. If none are provided, the scope defined by this
    context manager will temporally resume derivative tracking for all variables.
    
    .. code-block::
    
    a = dr.llvm.ad.Float(1.0)
    b = dr.llvm.ad.Float(2.0)
    dr.enable_grad(a, b)
    
    with suspend_grad():
    c = a + b
    
    with resume_grad():
    d = a + b
    
    with resume_grad(a):
    e = 2.0 * a
    f = 4.0 * b
    
    assert not dr.grad_enabled(c)
    assert dr.grad_enabled(d)
    assert dr.grad_enabled(e)
    assert not dr.grad_enabled(f)
    
    The optional ``when`` boolean keyword argument can be defined to specifed a
    condition determining whether to resume the tracking of derivatives or not.
    
    .. code-block::
    
    a = dr.llvm.ad.Float(1.0)
    dr.enable_grad(a)
    
    cond = condition()
    
    with suspend_grad():
    with resume_grad(when=cond):
    b = 4.0 * a
    
    assert dr.grad_enabled(b) == cond
    
    Args:
    *args (tuple): A variable-length list of differentiable Dr.Jit array
    instances, :ref:`custom data structures <custom-struct>`, sequences, or
    mappings. The function will recursively traverse data structures to
    discover all Dr.Jit arrays.
    
    when (bool): An optional Python boolean determining whether to resume
    derivative tracking.
    
    """
    ...

def rotate(dtype, axis, angle):
    """
    
    Constructs a rotation quaternion, which rotates by ``angle`` radians around
    ``axis``.
    
    The function requires ``axis`` to be normalized.
    
    Args:
    dtype (type): Desired Dr.Jit quaternion type.
    
    axis (drjit.ArrayBase): A 3-dimensional Dr.Jit array representing the rotation axis
    
    angle (float | drjit.ArrayBase): Rotation angle.
    
    Returns:
    drjit.ArrayBase: The rotation quaternion
    
    """
    ...

def round(arg, /):
    """
    
    round(arg, /)
    
    Rounds arg to the nearest integer using Banker's rounding for
    half-way values.
    
    This function is equivalent to ``std::rint`` in C++. It does not convert the
    type of the input array. A separate cast is necessary when integer output is
    desired.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Rounded result
    
    """
    ...

def rsqrt(arg, /):
    """
    
    rsqrt(arg, /)
    Evaluate the reciprocal square root (1 / sqrt(arg)) of the provided input.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU"). The result is slightly
    approximate in this case (refer to the documentation of the instruction
    `rsqrt.approx.ftz.f32` in the NVIDIA PTX manual for details).
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Reciprocal square root of the input
    
    """
    ...

def safe_acos(arg):
    """
    
    Safe wrapper around :py:func:`drjit.acos` that avoids domain errors.
    
    Input values are clipped to the :math:`(-1, 1)` domain.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Arccosine approximation
    
    """
    ...

def safe_asin(arg):
    """
    
    Safe wrapper around :py:func:`drjit.asin` that avoids domain errors.
    
    Input values are clipped to the :math:`(-1, 1)` domain.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Arcsine approximation
    
    """
    ...

def safe_sqrt(arg):
    """
    
    Safely evaluate the square root of the provided input avoiding domain errors.
    
    Negative inputs produce a ``0.0`` output value.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Square root of the input
    
    """
    ...


from .stubs import scalar as scalar

def scalar_t(arg, /):
    """
    
    scalar_t(arg, /)
    Return the *scalar type* associated with the provided Dr.Jit array or type (i.e., the
    representation of elements at the lowest level)
    
    When the input is not a Dr.Jit array or type, the function returns the input
    unchanged. The following assertions illustrate the behavior of
    :py:func:`scalar_t`.
    
    
    .. code-block::
    
    assert dr.scalar_t(dr.scalar.Array3f) is bool
    assert dr.scalar_t(dr.cuda.Array3f) is float
    assert dr.scalar_t(dr.cuda.Matrix4f) is float
    assert dr.scalar_t("test") is str
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    int: Returns the scalar type of the provided Dr.Jit array, or the type of
    the input.
    
    """
    ...

def scatter(target, value, index, active=True):
    """
    
    Scatter values into a flat array or nested data structure
    
    This operation performs a *scatter* (i.e., indirect memory write) of the
    ``value`` parameter to the ``target`` array at position ``index``. The optional
    ``active`` argument can be used to disable some of the individual write
    operations, which is useful when not all provided values or indices are valid.
    
    This operation can be used in the following different ways:
    
    1. When ``target`` is a 1D Dr.Jit array like :py:class:`drjit.llvm.ad.Float`,
    this operation implements a parallelized version of the Python array
    indexing expression ``target[index] = value`` with optional masking. Example:
    
    .. code-block::
    
    target = dr.empty(dr.cuda.Float, 1024*1024)
    value = dr.cuda.Float([...])
    index = dr.cuda.UInt([...]) # Note: negative indices are not permitted
    dr.scatter(target, value=value, index=index)
    
    2. When ``target`` is a more complex type (e.g. a :ref:`custom source structure
    <custom-struct>`, nested Dr.Jit array, tuple, list, dictionary, etc.), the
    behavior depends:
    
    - When ``target`` and ``value`` are of the same type, the scatter operation
    threads through entries and invokes itself recursively. For example, the
    scatter operation in
    
    .. code-block::
    
    target = dr.cuda.Array3f(...)
    value = dr.cuda.Array3f(...)
    index = dr.cuda.UInt([...])
    dr.scatter(target, value, index)
    
    is equivalent to
    
    .. code-block::
    
    dr.scatter(target.x, value.x, index)
    dr.scatter(target.y, value.y, index)
    dr.scatter(target.z, value.z, index)
    
    - Otherwise, the operation flattens the ``value`` array and writes it using
    C-style ordering with a suitably modified ``index``. For example, the
    scatter below writes 3D vectors into a 1D array.
    
    .. code-block::
    
    target = dr.cuda.Float(...)
    value = dr.cuda.Array3f(...)
    index = dr.cuda.UInt([...])
    dr.scatter(target, value, index)
    
    and is equivalent to
    
    .. code-block::
    
    dr.scatter(target, value.x, index*3 + 0)
    dr.scatter(target, value.y, index*3 + 1)
    dr.scatter(target, value.z, index*3 + 2)
    
    .. danger::
    
    The indices provided to this operation are unchecked. Out-of-bounds writes
    are undefined behavior (if not disabled via the ``active`` parameter) and
    may crash the application. Negative indices are not permitted.
    
    Dr.Jit makes no guarantees about the expected behavior when a scatter
    operation has *conflicts*, i.e., when a specific position is written
    multiple times by a single :py:func:`drjit.scatter()` operation.
    
    Args:
    target (object): The object into which data should be written (typically
    a 1D Dr.Jit array, but other variations are possible as well, see the
    description above.)
    
    value (object): The values to be written (typically of type ``type(target)``,
    but other variations are possible as well, see the description above.)
    Dr.Jit will attempt an implicit conversion if the the input is not an
    array type.
    
    index (object): a 1D dynamic unsigned 32-bit Dr.Jit array (e.g.,
    :py:class:`drjit.scalar.ArrayXu` or :py:class:`drjit.cuda.UInt`)
    specifying gather indices. Dr.Jit will attempt an implicit conversion
    if another type is provided.
    
    active (object): an optional 1D dynamic Dr.Jit mask array (e.g.,
    :py:class:`drjit.scalar.ArrayXb` or :py:class:`drjit.cuda.Bool`)
    specifying active components. Dr.Jit will attempt an implicit
    conversion if another type is provided. The default is `True`.
    
    """
    ...

def scatter_inc(target, index, active=True):
    """
    
    Atomically increment a value within an unsigned 32-bit integer array
    and return the value prior to the update.
    
    This operation works just like the :py:func:`drjit.scatter_reduce()`
    operation for 32-bit unsigned integer operands, but with a fixed
    ``value=1`` parameter and ``reduce_op=ReduceOp::Add``.
    
    The main difference is that this variant additionally returns the *old*
    value of the target array prior to the atomic update in contrast to the
    more general scatter-reduction, which just returns ``None``. The operation
    also supports masking---the return value in the unmasked case is undefined.
    Both ``target`` and ``index`` parameters must be 1D unsigned 32-bit
    arrays.
    
    This operation is a building block for stream compaction: threads can
    scatter-increment a global counter to request a spot in an array and then
    write their result there. The recipe for this is look as follows:
    
    .. code-block:: python
    
    ctr = UInt32(0) # Counter
    active = drjit.ones(Bool, len(data_1)) # .. or a more complex condition
    
    my_index = dr.scatter_inc(target=ctr, index=UInt32(0), mask=active)
    
    dr.scatter(
    target=data_compact_1,
    value=data_1,
    index=my_index,
    mask=active
    )
    
    dr.scatter(
    target=data_compact_2,
    value=data_2,
    index=my_index,
    mask=active
    )
    
    When following this approach, be sure to provide the same mask value to the
    :py:func:`drjit.scatter_inc()` and subsequent :py:func:`drjit.scatter()`
    operations.
    
    The function :py:func:`drjit.scatter_inc()` exhibits the following unusual
    behavior compared to regular Dr.Jit operations: the return value references
    the instantaneous state during a potentially large sequence of atomic
    operations. This instantaneous state is not reproducible in later kernel
    evaluations, and Dr.Jit will refuse to do so when the computed index is
    reused. In essence, the variable is "consumed" by the process of
    evaluation.
    
    .. code-block:: python
    
    my_index = dr.scatter_inc(target=ctr, index=UInt32(0), mask=active)
    dr.scatter(
    target=data_compact_1,
    value=data_1,
    index=my_index,
    mask=active
    )
    
    dr.eval(data_compact_1) # Run Kernel #1
    
    dr.scatter(
    target=data_compact_2,
    value=data_2,
    index=my_index, # <-- oops, reusing my_index in another kernel.
    mask=active     #     This raises an exception.
    )
    
    To get the above code to work, you will need to evaluate ``my_index`` at
    the same time to materialize it into a stored (and therefore trivially
    reproducible) representation. For this, ensure that the size of the
    ``active`` mask matches ``len(data_*)`` and that it is not the trivial
    ``True`` default mask (otherwise, the evaluated ``my_index`` will be
    scalar).
    
    .. code-block:: python
    
    dr.eval(data_compact_1, my_index)
    
    Such multi-stage evaluation is potentially inefficient and may defeat the
    purpose of performing stream compaction in the first place. In general,
    prefer keeping all scatter operations involving the computed index in the
    same kernel, and then this issue does not arise.
    
    The implementation of :py:func:`drjit.scatter_inc()` performs a local
    reduction first, followed by a single atomic write per SIMD packet/warp.
    This is done to reduce contention from a potentially very large number of
    atomic operations targeting the same memory address. Fully masked updates
    do not cause memory traffic.
    
    There is some conceptual overlap between this function and
    :py:func:`drjit.compress()`, which can likewise be used to reduce a stream
    to a smaller subset of active items. The downside of
    :py:func:`drjit.compress()` is that it requires evaluating the variables to
    be reduced, which can be very costly in terms of of memory traffic and
    storage footprint. Reducing through :py:func:`drjit.scatter_inc()` does not
    have this limitation: it can operate on symbolic arrays that greatly exceed
    the available device memory. One advantage of :py:func:`drjit.compress()`
    is that it essentially boils down to a realtively simple prefix sum, which
    does not require atomic memory operations (these can be slow in some
    cases).
    """
    ...

def scatter_reduce(op, target, value, index, active=True):
    """
    
    Perform a read-modify-write operation on a flat array or nested data structure
    
    This function performs a read-modify-write operation of the ``value``
    parameter to the ``target`` array at position ``index``. The optional
    ``active`` argument can be used to disable some of the individual write
    operations, which is useful when not all provided values or indices are valid.
    
    The operation to be applied is defined by tje ``op`` argument (see
    :py:class:`drjit.ReduceOp`).
    
    This operation can be used in the following different ways:
    
    1. When ``target`` is a 1D Dr.Jit array like :py:class:`drjit.llvm.ad.Float`,
    this operation implements a parallelized version of the expression
    ``target[index] = op(value, target[index])`` with optional masking. Example:
    
    .. code-block::
    
    target = dr.cuda.Float([...])
    value = dr.cuda.Float([...])
    index = dr.cuda.UInt([...]) # Note: negative indices are not permitted
    dr.scatter_reduce(dr.ReduceOp.Add, target, value=value, index=index)
    
    2. When ``target`` is a more complex type (e.g. a :ref:`custom source structure
    <custom-struct>`, nested Dr.Jit array, tuple, list, dictionary, etc.), then
    ``target`` and ``value`` must be of the same type. The scatter reduce operation
    threads through entries and invokes itself recursively. For example, the
    scatter operation in
    
    .. code-block::
    
    target = dr.cuda.Array3f(...)
    value = dr.cuda.Array3f(...)
    index = dr.cuda.UInt([...])
    dr.scatter_reduce(dr.ReduceOp.Add, target, value, index)
    
    is equivalent to
    
    .. code-block::
    
    dr.scatter_reduce(dr.ReduceOp.Add, target.x, value.x, index)
    dr.scatter_reduce(dr.ReduceOp.Add, target.y, value.y, index)
    dr.scatter_reduce(dr.ReduceOp.Add, target.z, value.z, index)
    
    .. danger::
    
    The indices provided to this operation are unchecked. Out-of-bounds writes
    are undefined behavior (if not disabled via the ``active`` parameter) and
    may crash the application. Negative indices are not permitted.
    
    Args:
    op (drjit.ReduceOp): Operation to be perform in the reduction.
    target (object): The object into which data should be written (typically
    a 1D Dr.Jit array, but other variations are possible as well, see the
    description above.)
    
    value (object): The values to be written (typically of type ``type(target)``,
    but other variations are possible as well, see the description above.)
    Dr.Jit will attempt an implicit conversion if the the input is not an
    array type.
    
    index (object): a 1D dynamic unsigned 32-bit Dr.Jit array (e.g.,
    :py:class:`drjit.scalar.ArrayXu` or :py:class:`drjit.cuda.UInt`)
    specifying gather indices. Dr.Jit will attempt an implicit conversion
    if another type is provided.
    
    active (object): an optional 1D dynamic Dr.Jit mask array (e.g.,
    :py:class:`drjit.scalar.ArrayXb` or :py:class:`drjit.cuda.Bool`)
    specifying active components. Dr.Jit will attempt an implicit
    conversion if another type is provided. The default is `True`.
    
    """
    ...

def schedule(*args):
    """
    
    Schedule the provided JIT variable(s) for later evaluation
    
    This function causes ``args`` to be evaluated by the next kernel launch. In
    other words, the effect of this operation is deferred: the next time that
    Dr.Jit's LLVM or CUDA backends compile and execute code, they will include the
    *trace* of the specified variables in the generated kernel and turn them into
    an explicit memory-based representation.
    
    Scheduling and evaluation of traced computation happens automatically, hence it
    is rare that a user would need to call this function explicitly. Explicit
    scheduling can improve performance in certain cases---for example, consider the
    following code:
    
    .. code-block::
    
    # Computation that produces Dr.Jit arrays
    a, b = ...
    
    # The following line launches a kernel that computes 'a'
    print(a)
    
    # The following line launches a kernel that computes 'b'
    print(b)
    
    If the traces of ``a`` and ``b`` overlap (perhaps they reference computation
    from an earlier step not shown here), then this is inefficient as these steps
    will be executed twice. It is preferable to launch bigger kernels that leverage
    common subexpressions, which is what :py:func:`drjit.schedule()` enables:
    
    .. code-block::
    
    a, b = ... # Computation that produces Dr.Jit arrays
    
    # Schedule both arrays for deferred evaluation, but don't evaluate yet
    dr.schedule(a, b)
    
    # The following line launches a kernel that computes both 'a' and 'b'
    print(a)
    
    # References the stored array, no kernel launch
    print(b)
    
    Note that :py:func:`drjit.eval()` would also have been a suitable alternative
    in the above example; the main difference to :py:func:`drjit.schedule()` is
    that it does the evaluation immediately without deferring the kernel launch.
    
    This function accepts a variable-length keyword argument and processes it
    as follows:
    
    - It recurses into sequences (``tuple``, ``list``, etc.)
    - It recurses into the values of mappings (``dict``, etc.)
    - It recurses into the fields of :ref:`custom data structures <custom-struct>`.
    
    During recursion, the function gathers all unevaluated Dr.Jit arrays. Evaluated
    arrays and incompatible types are ignored. Multiple variables can be
    equivalently scheduled with a single :py:func:`drjit.schedule()` call or a
    sequence of calls to :py:func:`drjit.schedule()`. Variables that are garbage
    collected between the original :py:func:`drjit.schedule()` call and the next
    kernel launch are ignored and will not be stored in memory.
    
    Args:
    *args (tuple): A variable-length list of Dr.Jit array instances,
    :ref:`custom data structures <custom-struct>`, sequences, or mappings.
    The function will recursively traverse data structures to discover all
    Dr.Jit arrays.
    
    Returns:
    bool: ``True`` if a variable was scheduled, ``False`` if the operation did
    not do anything.
    
    """
    ...

class scoped_rtld_deepbind:
    ...

class scoped_set_flag:
    ...

def sec(arg):
    """
    
    sec(arg, /)
    Secant approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Secant of the input
    
    """
    ...

def select(m, t, f, /):
    """
    
    select(condition, x, y, /)
    Select elements from inputs based on a condition
    
    This function implements the component-wise operation
    
    .. math::
    
    \mathrm{result}_i = \begin{cases}
    x_i,\quad&\text{if condition}_i,\\
    y_i,\quad&\text{otherwise.}
    \end{cases}
    
    Args:
    condition (bool | drjit.ArrayBase): A Python or Dr.Jit mask/boolean array
    x (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    y (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | int | drjit.ArrayBase: Component-wise result of the selection operation
    
    """
    ...

def set_device(device: int) -> None: ...
def set_flag(arg0: drjit.JitFlag, arg1: bool) -> None: ...
def set_flags(arg0: int) -> None: ...
def set_grad(dst, src):
    """
    
    Set the gradient value to the provided variable.
    
    Broadcasting is applied to the gradient value if necessary and possible to match
    the type of the input variable.
    
    Args:
    dst (object): An arbitrary Dr.Jit array, tensor,
    :ref:`custom data structure <custom-struct>`, sequences, or mapping.
    
    src (object): An arbitrary Dr.Jit array, tensor,
    :ref:`custom data structure <custom-struct>`, sequences, or mapping.
    
    """
    ...

def set_grad_enabled(arg, value):
    """
    
    Enable or disable gradient tracking on the provided variables.
    
    Args:
    arg (object): An arbitrary Dr.Jit array, tensor,
    :ref:`custom data structure <custom-struct>`, sequence, or mapping.
    
    value (bool): Defines whether gradient tracking should be enabled or
    disabled.
    
    """
    ...

def set_label(*args, **kwargs):
    """
    
    Sets the label of a provided Dr.Jit array, either in the JIT or the AD system.
    
    When a :ref:`custom data structure <custom-struct>` is provided, the field names
    will be used as suffix for the variables labels.
    
    When a sequence or static array is provided, the item's indices will be appended
    to the label.
    
    When a mapping is provided, the item's key will be appended to the label.
    
    Args:
    *arg (tuple): a Dr.Jit array instance and its corresponding label ``str`` value.
    
    **kwarg (dict): A set of (keyword, object) pairs.
    
    """
    ...

def set_log_level(arg0: drjit.LogLevel) -> None: ...
def set_print_threshold(size):
    """
    
    Set the maximum number of entries displayed when printing an array
    
    """
    ...

def set_thread_count(arg0: int) -> None: ...
def sh_eval(arg, order, /):
    """
    
    Evaluates the real spherical harmonics basis functions up to and including
    order ``order``.
    
    The directions provided to ``sh_eval`` must be normalized 3D vectors
    (i.e. using Cartesian instead of spherical coordinates).
    
    This function supports evaluation order up to 10 (e.g. ``order=9``).
    
    Args:
    arg (drjit.ArrayBase): A 3D Dr.Jit array type for the direction to be evaluated
    order (int): Order of the spherical harmonic evaluation
    
    Returns:
    list: List of spherical harmonics coefficients
    
    """
    ...

def shape(arg, /):
    """
    
    shape(arg, /)
    Return a tuple describing dimension and shape of the provided Dr.Jit array
    or tensor.
    
    When the arrays is ragged, the implementation signals a failure by returning
    ``None``. A ragged array has entries of incompatible size, e.g. ``[[1, 2],
    [3, 4, 5]]``. Note that an scalar entries (e.g. ``[[1, 2], [3]]``) are
    acceptable, since broadcasting can effectively convert them to any size.
    
    The expressions ``drjit.shape(arg)`` and ``arg.shape`` are equivalent.
    
    Args:
    arg (drjit.ArrayBase): An arbitrary Dr.Jit array or tensor
    
    Returns:
    tuple | NoneType: A tuple describing the dimension and shape of the
    provided Dr.Jit input array or tensor. When the input array is *ragged*
    (i.e., when it contains components with mismatched sizes), the function
    returns ``None``.
    
    """
    ...

def shuffle(perm, value):
    """
    
    Permute the entries of the provided Dr.Jit static array for the indices
    given in ``perm``.
    
    The pseudocode for this operation is
    
    .. code-block:: python
    
    out = [value[p] for p in perm]
    
    Args:
    perm (drjit.ArrayBase): A Python list of integers
    value (drjit.ArrayBase): A Dr.Jit static array type
    
    Returns:
    Shuffled input array
    
    """
    ...

def sign(arg, /):
    """
    
    sign(arg, /)
    Return the element-wise sign of the provided array.
    
    Args:
    arg (int | float | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    float | int | drjit.ArrayBase: Sign of the input array
    
    """
    ...

def sin(arg, /):
    """
    
    sin(arg, /)
    Sine approximation based on the CEPHES library.
    
    The implementation of this function is designed to achieve low error on the domain
    :math:`|x| < 8192` and will not perform as well beyond this range. See the
    section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU").
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Sine of the input
    
    """
    ...

def sincos(arg, /):
    """
    
    sincos(arg, /)
    Sine/cosine approximation based on the CEPHES library.
    
    The implementation of this function is designed to achieve low error on the
    domain :math:`|x| < 8192` and will not perform as well beyond this range. See
    the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using two operations involving the native multi-function unit ("MUFU").
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    (float, float) | (drjit.ArrayBase, drjit.ArrayBase): Sine and cosine of the input
    
    """
    ...

def sincosh(arg, /):
    """
    
    sincosh(arg, /)
    Hyperbolic sine/cosine approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    (float, float) | (drjit.ArrayBase, drjit.ArrayBase): Hyperbolic sine and cosine of the input
    
    """
    ...

def sinh(arg, /):
    """
    
    sinh(arg, /)
    Hyperbolic sine approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Hyperbolic sine of the input
    
    """
    ...

def size_v(arg, /):
    """
    
    size_v(arg, /)
    Return the (static) size of the outermost dimension of the provided Dr.Jit
    array instance or type
    
    Note that this function mainly exists to query type-level information. Use the
    Python ``len()`` function to query the size in a way that does not distinguish
    between static and dynamic arrays.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    int: Returns either the static size or :py:data:`drjit.Dynamic` when
    ``arg`` is a dynamic Dr.Jit array. Returns ``1`` for all other types.
    
    """
    ...

def slice(value, index=None, return_type=None):
    """
    
    Slice a structure of arrays to return a single entry for a given index
    
    This function is the equivalent to ``__getitem__(index)`` for the *dynamic
    dimension* of a Dr.Jit array or :ref:`custom source structure <custom-struct>`.
    It can be used to access a single element out a structure of arrays for a
    given index.
    
    The returned object type will differ from the type of the input value as its
    *dynamic dimension* will be removed. For static arrays (e.g.
    :py:class:`drjit.cuda.Array3f`) the function will return a Python ``list``.
    For :ref:`custom source structure <custom-struct>` the returned type needs
    to be specified through the argument ``return_type``.
    
    Args:
    value (object): A dynamically sized 1D Dr.Jit array instance
    that is compatible with ``dtype``. In other words, both must have the
    same underlying scalar type and be located imported in the same package
    (e.g., ``drjit.llvm.ad``).
    
    index (int): Index of the entry to be returned in the structure of arrays.
    When not specified (or ``None``), the provided object must have a
    dynamic width of ``1`` and this function will *remove* the dynamic
    dimension to this object by casting it into the appropriate type.
    
    return_type (type): A return type must be specified when slicing through
    a :ref:`custom source structure <custom-struct>`. Otherwise set to ``None``.
    
    Returns:
    object: Single entry of the structure of arrays.
    
    """
    ...

def smallest(t):
    """
    
    Returns the smallest normalized floating point value.
    
    Args:
    t (type): Python or Dr.Jit type determining whether to consider 32 or 64
    bits floating point precision.
    
    Returns:
    float: smallest normalized floating point value
    
    """
    ...

def sqr(a):
    """
    
    sqr(arg, /)
    Evaluate the square of the provided input.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Square of the input
    
    """
    ...

def sqrt(arg, /):
    """
    
    sqrt(arg, /)
    Evaluate the square root of the provided input.
    
    Negative inputs produce a *NaN* output value.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Square root of the input
    
    """
    ...

sqrt_four_pi = ...
"Convert a string or number to a floating point number, if possible."
sqrt_pi = ...
"Convert a string or number to a floating point number, if possible."
sqrt_two = ...
"Convert a string or number to a floating point number, if possible."
sqrt_two_pi = ...
"Convert a string or number to a floating point number, if possible."
def squared_norm(arg, /):
    """
    
    squared_norm(arg, /) -> float | int | drjit.ArrayBase
    Computes the squared norm of an array.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (list | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Squared norm of the input
    
    """
    ...

def sum(arg, /):
    """
    
    sum(arg, /) -> float | int | drjit.ArrayBase
    Compute the sum of all array elements.
    
    When the argument is a dynamic array, function performs a horizontal reduction.
    Please see the section on :ref:`horizontal reductions <horizontal-reductions>`
    for details.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Sum of the input
    
    """
    ...

def sum_nested(arg, /):
    """
    
    sum_nested(arg, /) -> float | int
    Iterates :py:func:`sum` until the return value is reduced to a single value.
    
    This function recursively calls :py:func:`drjit.sum` on all elements of
    the input array in order to reduce the returned value to a single entry.
    
    Args:
    arg (float | int | drjit.ArrayBase): A Python or Dr.Jit arithmetic type
    
    Returns:
    Sum of the input
    
    """
    ...

def suspend_grad(*args, when=True):
    """
    
    suspend_grad(*args, when = True)
    Context manager for temporally suspending derivative tracking.
    
    Dr.Jit's AD layer keeps track of a set of variables for which derivative
    tracking is currently enabled. Using this context manager is it possible to
    define a scope in which variables will be subtracted from that set, thereby
    controlling what derivative terms shouldn't be generated in that scope.
    
    The variables to be subtracted from the current set of enabled variables can be
    provided as function arguments. If none are provided, the scope defined by this
    context manager will temporally disable all derivative tracking.
    
    .. code-block::
    
    a = dr.llvm.ad.Float(1.0)
    b = dr.llvm.ad.Float(2.0)
    dr.enable_grad(a, b)
    
    with suspend_grad(): # suspend all derivative tracking
    c = a + b
    
    assert not dr.grad_enabled(c)
    
    with suspend_grad(a): # only suspend derivative tracking on `a`
    d = 2.0 * a
    e = 4.0 * b
    
    assert not dr.grad_enabled(d)
    assert dr.grad_enabled(e)
    
    In a scope where derivative tracking is completely suspended, the AD layer will
    ignore any attempt to enable gradient tracking on a variable:
    
    .. code-block::
    
    a = dr.llvm.ad.Float(1.0)
    
    with suspend_grad():
    dr.enable_grad(a) # <-- ignored
    assert not dr.grad_enabled(a)
    
    assert not dr.grad_enabled(a)
    
    The optional ``when`` boolean keyword argument can be defined to specifed a
    condition determining whether to suspend the tracking of derivatives or not.
    
    .. code-block::
    
    a = dr.llvm.ad.Float(1.0)
    dr.enable_grad(a)
    
    cond = condition()
    
    with suspend_grad(when=cond):
    b = 4.0 * a
    
    assert dr.grad_enabled(b) == not cond
    
    Args:
    *args (tuple): A variable-length list of differentiable Dr.Jit array
    instances, :ref:`custom data structures <custom-struct>`, sequences, or
    mappings. The function will recursively traverse data structures to
    discover all Dr.Jit arrays.
    
    when (bool): An optional Python boolean determining whether to suspend
    derivative tracking.
    
    """
    ...

def switch(indices, funcs, *args):
    """
    
    Dispatches a call to one of the given functions based on the given indices.
    
    .. code-block:: python
    
    def f1(x):
    return x * 10
    
    def f2(x):
    return x * 100
    
    arg = dr.llvm.Float([1.0, 2.0, 3.0, 4.0])
    indices = dr.llvm.UInt32([0, 1, 1, 0])
    
    res = dr.switch(indices, [f1, f2], arg)
    
    # [10.0, 200.0, 300.0, 40.0]
    
    Args:
    indices (drjit.ArrayBase): a list of indices to choose the functions
    funcs (list): a list of functions to dispatch based on ``indices``
    args (tuple): the arguments to pass to the functions
    
    Returns:
    object: the result of the function call dispatched based on the indices
    
    """
    ...

def sync_all_devices() -> None: ...
def sync_device() -> None: ...
def sync_thread() -> None: ...
def tan(arg, /):
    """
    
    tan(arg, /)
    Tangent approximation based on the CEPHES library.
    
    The implementation of this function is designed to achieve low error on the
    domain :math:`|x| < 8192` and will not perform as well beyond this range. See
    the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    When ``arg`` is a CUDA single precision array, the operation is implemented
    using the native multi-function unit ("MUFU").
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Tangent of the input
    
    """
    ...

def tanh(arg, /):
    """
    
    tanh(arg, /)
    Hyperbolic tangent approximation based on the CEPHES library.
    
    See the section on :ref:`transcendental function approximations
    <transcendental-accuracy>` for details regarding accuracy.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Hyperbolic tangent of the input
    
    """
    ...

def tgamma(arg, /):
    """
    
    Evaluates the Gamma function defined as
    
    .. math::
    
    \Gamma(x)=\int_0^\infty t^{x-1} e^{-t}\,\mathrm{d}t.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Value of the Gamma function at the input value
    
    """
    ...

def tile(arg, count: int):
    """
    
    This function constructs an Dr.Jit array by repeating ``arg`` ``count`` times.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit type
    count (int): Number of repetitions
    
    Returns:
    object: The tiled output array.
    
    """
    ...

def trace(a, /):
    """
    
    trace(arg, /)
    Returns the trace of the provided Dr.Jit matrix.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    Returns:
    drjit.ArrayBase: The trace of the input matrix
    
    """
    ...

def transform_compose(s, q, t, /):
    """
    
    transform_compose(S, Q, T, /)
    This function composes a 4x4 homogeneous coordinate transformation from the
    given scale, rotation, and translation. It performs the reverse of
    :py:func:`transform_decompose`.
    
    Args:
    S (drjit.ArrayBase): A Dr.Jit matrix type representing the scaling part
    Q (drjit.ArrayBase): A Dr.Jit quaternion type representing the rotation part
    T (drjit.ArrayBase): A 3D Dr.Jit array type representing the translation part
    
    Returns:
    drjit.ArrayBase: The Dr.Jit matrix resulting from the composition described above.
    
    """
    ...

def transform_decompose(a, it=10):
    """
    
    transform_decompose(arg, it=10)
    Performs a polar decomposition of a non-perspective 4x4 homogeneous
    coordinate matrix and returns a tuple of
    
    1. A positive definite 3x3 matrix containing an inhomogeneous scaling operation
    2. A rotation quaternion
    3. A 3D translation vector
    
    This representation is helpful when animating keyframe animations.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    it (int): Number of iterations to be taken by the polar decomposition algorithm.
    
    Returns:
    tuple: The tuple containing the scaling matrix, rotation quaternion and 3D translation vector.
    
    """
    ...

def transpose(a, /):
    """
    
    transpose(arg, /)
    Transpose the provided Dr.Jit matrix.
    
    Args:
    arg (drjit.ArrayBase): A Dr.Jit matrix type
    
    Returns:
    drjit.ArrayBase: The transposed matrix
    
    """
    ...

def traverse(dtype, mode, flags=ADFlag.Default):
    """
    
    Propagate derivatives through the enqueued set of edges in the AD computational
    graph in the direction specified by ``mode``.
    
    By default, Dr.Jit's AD system destructs the enqueued input graph during AD
    traversal. This frees up resources, which is useful when working with large
    wavefronts or very complex computation graphs. However, this also prevents
    repeated propagation of gradients through a shared subgraph that is being
    differentiated multiple times.
    
    To support more fine-grained use cases that require this, the following flags
    can be used to control what should and should not be destructed:
    
    - ``ADFlag.ClearNone``: clear nothing
    - ``ADFlag.ClearEdges``: delete all traversed edges from the computation graph
    - ``ADFlag.ClearInput``: clear the gradients of processed input vertices (in-degree == 0)
    - ``ADFlag.ClearInterior``: clear the gradients of processed interior vertices (out-degree != 0)
    - ``ADFlag.ClearVertices``: clear gradients of processed vertices only, but leave edges intact
    - ``ADFlag.Default``: clear everything (default behaviour)
    
    Args:
    dtype (type): defines the Dr.JIT array type used to build the AD graph
    
    mode (ADMode): defines the mode traversal (backward or forward)
    
    flags (ADFlag | int): flags to control what should and should not be
    destructed during forward/backward mode traversal.
    
    """
    ...

def trunc(arg, /):
    """
    
    trunc(arg, /)
    Truncates arg to the nearest integer by towards zero.
    
    The function does not convert the type of the input array. A separate
    cast is necessary when integer output is desired.
    
    Args:
    arg (float | drjit.ArrayBase): A Python or Dr.Jit floating point type
    
    Returns:
    float | drjit.ArrayBase: Truncated result
    
    """
    ...

two_pi = ...
"Convert a string or number to a floating point number, if possible."
def tzcnt(arg, /):
    """
    
    Return the number of trailing zero bits.
    
    This function assumes that ``arg`` is an integer array.
    
    Args:
    arg (int | drjit.ArrayBase): A Python or Dr.Jit array
    
    Returns:
    int | drjit.ArrayBase: number of trailing zero bits in the input array
    
    """
    ...

def uint32_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into a *unsigned 32 bit*
    version.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3f`), it
    returns an *unsigned 32 bit* version (e.g. :py:class:`drjit.cuda.Array3u`).
    
    2. When the input isn't a type, it returns ``uint32_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``int``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def uint64_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into an *unsigned 64 bit*
    version.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3f`), it
    returns an *unsigned 64 bit* version (e.g. :py:class:`drjit.cuda.Array3u64`).
    
    2. When the input isn't a type, it returns ``uint64_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``int``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def uint_array_t(arg):
    """
    
    Converts the provided Dr.Jit array/tensor type into a *unsigned integer*
    version with the same element size.
    
    This function implements the following set of behaviors:
    
    1. When invoked with a Dr.Jit array *type* (e.g. :py:class:`drjit.cuda.Array3f64`), it
    returns an *unsigned integer* version (e.g. :py:class:`drjit.cuda.Array3u64`).
    
    2. When the input isn't a type, it returns ``uint_array_t(type(arg))``.
    
    3. When the input is not a Dr.Jit array or type, the function returns ``int``.
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Result of the conversion as described above.
    
    """
    ...

def unravel(dtype, array, order='F'):
    """
    
    Load a sequence of Dr.Jit vectors/matrices/etc. from a contiguous flat array
    
    This operation implements the inverse of :py:func:`drjit.ravel()`. In contrast
    to :py:func:`drjit.ravel()`, it requires one additional parameter (``dtype``)
    specifying type of the return value. For example,
    
    .. code-block::
    
    x = dr.cuda.Float([1, 2, 3, 4, 5, 6])
    y = dr.unravel(dr.cuda.Array3f, x, order=...)
    
    will produce an array of two 3D vectors with different contents depending
    on the indexing convention:
    
    - ``[1, 2, 3]`` and ``[4, 5, 6]`` when unraveled with ``order='F'`` (the default for Dr.Jit arrays), and
    - ``[1, 3, 5]`` and ``[2, 4, 6]`` when unraveled with ``order='C'``
    
    Args:
    dtype (type): An arbitrary Dr.Jit array type
    
    array (drjit.ArrayBase): A dynamically sized 1D Dr.Jit array instance
    that is compatible with ``dtype``. In other words, both must have the
    same underlying scalar type and be located imported in the same package
    (e.g., ``drjit.llvm.ad``).
    
    order (str): A single character indicating the index order. ``'F'`` (the
    default) indicates column-major/Fortran-style ordering, in which case
    the first index changes at the highest frequency. The alternative
    ``'C'`` specifies row-major/C-style ordering, in which case the last
    index changes at the highest frequency.
    
    
    Returns:
    object: An instance of type ``dtype`` containing the result of the unravel
    operation.
    
    """
    ...

def upsample(t, shape=None, scale_factor=None, align_corners=False):
    """
    
    upsample(source, shape=None, scale_factor=None, align_corners=False)
    Up-sample the input tensor or texture according to the provided shape.
    
    Alternatively to specifying the target shape, a scale factor can be
    provided.
    
    The behavior of this function depends on the type of ``source``:
    
    1. When ``source`` is a Dr.Jit tensor, nearest neighbor up-sampling will use
    hence the target ``shape`` values must be multiples of the source shape
    values. When `scale_factor` is used, its values must be integers.
    
    2. When ``source`` is a Dr.Jit texture type, the up-sampling will be
    performed according to the filter mode set on the input texture. Target
    ``shape`` values are not required to be multiples of the source shape
    values. When `scale_factor` is used, its values must be integers.
    
    Args:
    source (object): A Dr.Jit tensor or texture type.
    
    shape (list): The target shape (optional)
    
    scale_factor (list): The scale factor to apply to the current shape
    (optional)
    
    align_corners (bool): Defines whether or not the corner pixels of the
    input and output should be aligned. This allows the values at the
    corners to be preserved. This flag is only relevant when ``source`` is
    a Dr.Jit texture type performing linear interpolation. The default is
    `False`.
    
    Returns:
    object: the up-sampled tensor or texture object. The type of the output
    will be the same as the type of the source.
    
    """
    ...

def value_t(arg, /):
    """
    
    value_t(arg, /)
    Return the *value type* underlying the provided Dr.Jit array or type (i.e., the
    type of values obtained by accessing the contents using a 1D index).
    
    When the input is not a Dr.Jit array or type, the function returns the input
    unchanged. The following code fragment shows several example uses of
    :py:func:`value_t`.
    
    .. code-block::
    
    assert dr.value_t(dr.scalar.Array3f) is float
    assert dr.value_t(dr.cuda.Array3f) is dr.cuda.Float
    assert dr.value_t(dr.cuda.Matrix4f) is dr.cuda.Array4f
    assert dr.value_t(dr.cuda.TensorXf) is float
    assert dr.value_t("test") is str
    
    Args:
    arg (object): An arbitrary Python object
    
    Returns:
    type: Returns the value type of the provided Dr.Jit array, or the type of
    the input.
    
    """
    ...

def whos() -> None: ...
def whos_str() -> str: ...
def width(arg, /):
    """
    
    width(arg, /)
    Return the width of the provided dynamic Dr.Jit array, tensor, or
    :ref:`custom data structure <custom-struct>`.
    
    The function returns ``1`` if the input variable isn't a Dr.Jit array,
    tensor, or :ref:`custom data structure <custom-struct>`.
    
    Args:
    arg (drjit.ArrayBase): An arbitrary Dr.Jit array, tensor, or
    :ref:`custom data structure <custom-struct>`
    
    Returns:
    int: The dynamic width of the provided variable.
    
    """
    ...

def wrap_ad(source: str, target: str):
    """
    
    Function decorator that wraps the excecution of a function using a different
    AD framework to ensure that gradients can flow seamlessly between both
    frameworks.
    
    Using this decorator it is possible to mix AD-aware computation between two
    AD frameworks (e.g. Dr.Jit and PyTorch). The wrapped function's arguments
    will be casted to the tensor types corresponding to the ``target`` framework.
    Similarily, the return values will be casted to the tensor types corresponding
    to the ``source`` framework.
    
    The decorated function can take an arbitrary number of arguments and have any
    number of return values.
    
    Currently only the following combination of frameworks are supported:
    
    .. list-table::
    :header-rows: 1
    
    * - ``source``
    - ``target``
    - Forward AD
    - Backward AD
    * - ``drjit``
    - ``torch``
    - ❌
    - ✔️
    * - ``torch``
    - ``drjit``
    - ❌
    - ✔️
    
    The example below shows how to wrap a Dr.Jit function in a PyTorch script:
    
    .. code-block:: python
    
    # Start with a PyTorch tensor
    a = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
    
    # Some PyTorch arithmetic
    b = torch.sin(a)
    
    # Wrap a function performing some arithmetic using Dr.Jit
    @dr.wrap_ad(source='torch', target='drjit')
    def dr_func(x):
    return dr.cos(x) + dr.power(x, 2)
    
    # Excecute the wrapped function (returns a PyTorch tensor)
    c = dr_func(b)
    
    # Some more PyTorch arithmetic
    d = torch.tan(c)
    
    # Propagate gradients to variable a (through PyTorch -> Dr.Jit -> PyTorch)
    d.sum().backward()
    
    # Inspect the resulting gradients
    print(a.grad)
    
    Similarily the following example shows how to wrap PyTorch code into a
    Dr.Jit script:
    
    .. code-block:: python
    
    # Start with a Dr.Jit tensor
    a = dr.llvm.ad.TensorXf([1, 2, 3], shape=[3])
    dr.enable_grad(a)
    
    # Some Dr.Jit arithmetic
    b = dr.sin(a)
    
    # Wrap a function performing some arithmetic using PyTorch
    @dr.wrap_ad(source='drjit', target='torch')
    def torch_func(x):
    return torch.cos(x) + torch.sin(x)
    
    # Excecute the wrapped function (returns a Dr.Jit tensor)
    c = torch_func(b)
    
    # Some more Dr.Jit arithmetic
    d = dr.tan(c)
    
    # Propagate gradients to variable a (through Dr.Jit -> PyTorch -> Dr.Jit)
    dr.backward(d)
    
    # Inspect the resulting gradients
    print(dr.grad(a))
    
    .. danger::
    
    Forward-mode AD isn't currently supported by this operation.
    
    Args:
    source (str | module): The AD framework used outside of the wrapped function.
    target (str | module): The AD framework used within the wrapped function.
    
    Returns:
    The decorated function.
    
    """
    ...

def zeros(dtype, shape=1):
    """
    
    Return a zero-initialized instance of the desired type and shape
    
    This function can create zero-initialized instances of various types. In
    particular, ``dtype`` can be:
    
    - A Dr.Jit array type like :py:class:`drjit.cuda.Array2f`. When ``shape``
    specifies a sequence, it must be compatible with static dimensions of the
    ``dtype``. For example, ``dr.zeros(dr.cuda.Array2f, shape=(3, 100))`` fails,
    since the leading dimension is incompatible with
    :py:class:`drjit.cuda.Array2f`. When ``shape`` is an integer, it specifies
    the size of the last (dynamic) dimension, if available.
    
    - A tensorial type like :py:class:`drjit.scalar.TensorXf`. When ``shape``
    specifies a sequence (list/tuple/..), it determines the tensor rank and
    shape. When ``shape`` is an integer, the function creates a rank-1 tensor of
    the specified size.
    
    - A :ref:`custom data structure <custom-struct>`. In this case,
    :py:func:`drjit.zeros()` will invoke itself recursively to zero-initialize
    each field of the data structure.
    
    - A scalar Python type like ``int``, ``float``, or ``bool``. The ``shape``
    parameter is ignored in this case.
    
    Note that when ``dtype`` refers to a scalar mask or a mask array, it will be
    initialized to ``False`` as opposed to zero.
    
    Args:
    dtype (type): Desired Dr.Jit array type, Python scalar type, or
    :ref:`custom data structure <custom-struct>`.
    
    shape (Sequence[int] | int): Shape of the desired array
    
    Returns:
    object: A zero-initialized instance of type ``dtype``.
    
    """
    ...

