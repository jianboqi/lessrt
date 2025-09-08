from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

class AdjointIntegrator(Integrator):
    """
    Abstract adjoint integrator that performs Monte Carlo sampling
    starting from the emitters.
    
    Subclasses of this interface must implement the sample() method, which
    performs recursive Monte Carlo integration starting from an emitter
    and directly accumulates the product of radiance and importance into
    the film. The render() method then repeatedly invokes this estimator
    to compute the rendered image.
    
    Remark:
        The adjoint integrator does not support renderings with arbitrary
        output variables (AOVs).
    """

    def __init__(self: mitsuba.AdjointIntegrator, arg0: mitsuba.Properties) -> None: ...
    ptr = ...

    def aov_names(self: mitsuba.Integrator) -> List[str]:
        """
        For integrators that return one or more arbitrary output variables
        (AOVs), this function specifies a list of associated channel names.
        The default implementation simply returns an empty vector.
        """
        ...

    def cancel(self: mitsuba.Integrator) -> None:
        """
        Cancel a running render job (e.g. after receiving Ctrl-C)
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function renders the scene from the viewpoint of ``sensor``. All
        other parameters are optional and control different aspects of the
        rendering process. In particular:
        
        Parameter ``seed``:
            This parameter controls the initialization of the random number
            generator. It is crucial that you specify different seeds (e.g.,
            an increasing sequence) if subsequent ``render``() calls should
            produce statistically independent images.
        
        Parameter ``spp``:
            Set this parameter to a nonzero value to override the number of
            samples per pixel. This value then takes precedence over whatever
            was specified in the construction of ``sensor->sampler()``. This
            parameter may be useful in research applications where an image
            must be rendered multiple times using different quality levels.
        
        Parameter ``develop``:
            If set to ``True``, the implementation post-processes the data
            stored in ``sensor->film()``, returning the resulting image as a
            TensorXf. Otherwise, it returns an empty tensor.
        
        Parameter ``evaluate``:
            This parameter is only relevant for JIT variants of Mitsuba (LLVM,
            CUDA). If set to ``True``, the rendering step evaluates the
            generated image and waits for its completion. A log message also
            denotes the rendering time. Otherwise, the returned tensor
            (``develop=true``) or modified film (``develop=false``) represent
            the rendering task as an unevaluated computation graph.
        
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor: int = 0, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function is just a thin wrapper around the previous render()
        overload. It accepts a sensor *index* instead and renders the scene
        using sensor 0 by default.
        """
        ...

    @overload
    def render_backward(self: mitsuba.AdjointIntegrator, scene: mitsuba.Scene, params: object, grad_in: mitsuba.TensorXf, sensor, seed: int = 0, spp: int = 0) -> None: ...
    @overload
    def render_backward(self: mitsuba.AdjointIntegrator, scene: mitsuba.Scene, params: object, grad_in: mitsuba.TensorXf, sensor: int = 0, seed: int = 0, spp: int = 0) -> None: ...
    @overload
    def render_forward(self: mitsuba.AdjointIntegrator, scene: mitsuba.Scene, params: object, sensor, seed: int = 0, spp: int = 0) -> mitsuba.TensorXf: ...
    @overload
    def render_forward(self: mitsuba.AdjointIntegrator, scene: mitsuba.Scene, params: object, sensor: int = 0, seed: int = 0, spp: int = 0) -> mitsuba.TensorXf: ...
    def sample(self: mitsuba.AdjointIntegrator, scene: mitsuba.Scene, sensor, sampler, block: mitsuba.ImageBlock, sample_scale: float) -> None:
        """
        Sample the incident importance and splat the product of importance and
        radiance to the film.
        
        Parameter ``scene``:
            The underlying scene
        
        Parameter ``sensor``:
            A sensor from which rays should be sampled
        
        Parameter ``sampler``:
            A source of (pseudo-/quasi-) random numbers
        
        Parameter ``block``:
            An image block that will be updated during the sampling process
        
        Parameter ``sample_scale``:
            A scale factor that must be applied to each sample to account for
            the film resolution and number of samples.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def should_stop(self: mitsuba.Integrator) -> bool:
        """
        Indicates whether cancel() or a timeout have occurred. Should be
        checked regularly in the integrator's main loop so that timeouts are
        enforced accurately.
        
        Note that accurate timeouts rely on m_render_timer, which needs to be
        reset at the beginning of the rendering phase.
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Appender(Object):
    """
    This class defines an abstract destination for logging-relevant
    information
    """

    def __init__(self: mitsuba.Appender) -> None: ...
    ptr = ...

    def append(self: mitsuba.Appender, level: mitsuba.LogLevel, text: str) -> None:
        """
        Append a line of text with the given log level
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def log_progress(self: mitsuba.Appender, progress: float, name: str, formatted: str, eta: str, ptr: capsule = None) -> None:
        """
        Process a progress message
        
        Parameter ``progress``:
            Percentage value in [0, 100]
        
        Parameter ``name``:
            Title of the progress message
        
        Parameter ``formatted``:
            Formatted string representation of the message
        
        Parameter ``eta``:
            Estimated time until 100% is reached.
        
        Parameter ``ptr``:
            Custom pointer payload. This is used to express the context of a
            progress message. When rendering a scene, it will usually contain
            a pointer to the associated ``RenderJob``.
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class ArgParser:
    """
    Minimal command line argument parser
    
    This class provides a minimal cross-platform command line argument
    parser in the spirit of to GNU getopt. Both short and long arguments
    that accept an optional extra value are supported.
    
    The typical usage is
    
    ```
    ArgParser p;
    auto arg0 = p.register("--myParameter");
    auto arg1 = p.register("-f", true);
    p.parse(argc, argv);
    if (*arg0)
        std::cout << "Got --myParameter" << std::endl;
    if (*arg1)
        std::cout << "Got -f " << arg1->value() << std::endl;
    ```
    """

    def __init__(self: mitsuba.ArgParser) -> None: ...
    class Arg:
        def as_float(self: mitsuba.ArgParser.Arg) -> float:
            """
            Return the extra argument associated with this argument
            """
            ...

        def as_int(self: mitsuba.ArgParser.Arg) -> int:
            """
            Return the extra argument associated with this argument
            """
            ...

        def as_string(self: mitsuba.ArgParser.Arg) -> str:
            """
            Return the extra argument associated with this argument
            """
            ...

        def count(self: mitsuba.ArgParser.Arg) -> int:
            """
            Specifies how many times the argument has been specified
            """
            ...

        def extra(self: mitsuba.ArgParser.Arg) -> bool:
            """
            Specifies whether the argument takes an extra value
            """
            ...

        def next(self: mitsuba.ArgParser.Arg) -> mitsuba.ArgParser.Arg:
            """
            For arguments that are specified multiple times, advance to the next
            one.
            """
            ...

        ...

    @overload
    def add(self: mitsuba.ArgParser, prefix: str, extra: bool = False) -> mitsuba.ArgParser.Arg:
        """
        Register a new argument with the given list of prefixes
        
        Parameter ``prefixes``:
            A list of command prefixes (i.e. {"-f", "--fast"})
        
        Parameter ``extra``:
            Indicates whether the argument accepts an extra argument value
        
        """
        ...

    @overload
    def add(self: mitsuba.ArgParser, prefixes: List[str], extra: bool = False) -> mitsuba.ArgParser.Arg:
        """
        Register a new argument with the given prefix
        
        Parameter ``prefix``:
            A single command prefix (i.e. "-f")
        
        Parameter ``extra``:
            Indicates whether the argument accepts an extra argument value
        """
        ...

    def executable_name(self: mitsuba.ArgParser) -> str: ...
    def parse(self: mitsuba.ArgParser, arg0: List[str]) -> None:
        """
        Parse the given set of command line arguments
        """
        ...

    ...

class AtomicFloat:
    """
    Atomic floating point data type
    
    The class implements an an atomic floating point data type (which is
    not possible with the existing overloads provided by ``std::atomic``).
    It internally casts floating point values to an integer storage format
    and uses atomic integer compare and exchange operations to perform
    changes.
    """

    def __init__(self: mitsuba.AtomicFloat, arg0: float) -> None:
        """
        Initialize the AtomicFloat with a given floating point value
        """
        ...

    ...

class BSDF(Object):
    """
    Bidirectional Scattering Distribution Function (BSDF) interface
    
    This class provides an abstract interface to all %BSDF plugins in
    Mitsuba. It exposes functions for evaluating and sampling the model,
    and for querying associated probability densities.
    
    By default, functions in class sample and evaluate the complete BSDF,
    but it also allows to pick and choose individual components of multi-
    lobed BSDFs based on their properties and component indices. This
    selection is specified using a context data structure that is provided
    along with every operation.
    
    When polarization is enabled, BSDF sampling and evaluation returns 4x4
    Mueller matrices that describe how scattering changes the polarization
    state of incident light. Mueller matrices (e.g. for mirrors) are
    expressed with respect to a reference coordinate system for the
    incident and outgoing direction. The convention used here is that
    these coordinate systems are given by ``coordinate_system(wi)`` and
    ``coordinate_system(wo)``, where 'wi' and 'wo' are the incident and
    outgoing direction in local coordinates.
    
    See also:
        mitsuba.BSDFContext
    
    See also:
        mitsuba.BSDFSample3f
    """

    def __init__(self: mitsuba.BSDF, props: mitsuba.Properties) -> None: ...
    m_components = ...
    m_flags = ...
    ptr = ...

    def component_count(self: mitsuba.BSDF, active: bool = True) -> int:
        """
        Number of components this BSDF is comprised of.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.BSDF, ctx: mitsuba.BSDFContext, si: mitsuba.SurfaceInteraction3f, wo: mitsuba.Vector3f, active: bool = True) -> mitsuba.Color3f:
        """
        Evaluate the BSDF f(wi, wo) or its adjoint version f^{*}(wi, wo) and
        multiply by the cosine foreshortening term.
        
        Based on the information in the supplied query context ``ctx``, this
        method will either evaluate the entire BSDF or query individual
        components (e.g. the diffuse lobe). Only smooth (i.e. non Dirac-delta)
        components are supported: calling ``eval()`` on a perfectly specular
        material will return zero.
        
        Note that the incident direction does not need to be explicitly
        specified. It is obtained from the field ``si.wi``.
        
        Parameter ``ctx``:
            A context data structure describing which lobes to evaluate, and
            whether radiance or importance are being transported.
        
        Parameter ``si``:
            A surface interaction data structure describing the underlying
            surface position. The incident direction is obtained from the
            field ``si.wi``.
        
        Parameter ``wo``:
            The outgoing direction
        """
        ...

    def eval_attribute(self: mitsuba.BSDF, name: str, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Evaluate a specific BSDF attribute at the given surface interaction.
        
        BSDF attributes are user-provided fields that provide extra
        information at an intersection. An example of this would be a per-
        vertex or per-face color on a triangle mesh.
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An unpolarized spectral power distribution or reflectance value
        """
        ...

    def eval_attribute_1(self: mitsuba.BSDF, name: str, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> float:
        """
        Monochromatic evaluation of a BSDF attribute at the given surface
        interaction
        
        This function differs from eval_attribute() in that it provided raw
        access to scalar intensity/reflectance values without any color
        processing (e.g. spectral upsampling).
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An scalar intensity or reflectance value
        """
        ...

    def eval_attribute_3(self: mitsuba.BSDF, name: str, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Trichromatic evaluation of a BSDF attribute at the given surface
        interaction
        
        This function differs from eval_attribute() in that it provided raw
        access to RGB intensity/reflectance values without any additional
        color processing (e.g. RGB-to-spectral upsampling).
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An trichromatic intensity or reflectance value
        """
        ...

    def eval_diffuse_reflectance(self: mitsuba.BSDF, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Evaluate the diffuse reflectance
        
        This method approximates the total diffuse reflectance for a given
        direction. For some materials, an exact value can be computed
        inexpensively. When this is not possible, the value is approximated by
        evaluating the BSDF for a normal outgoing direction and returning this
        value multiplied by pi. This is the default behaviour of this method.
        
        Parameter ``si``:
            A surface interaction data structure describing the underlying
            surface position.
        """
        ...

    def eval_null_transmission(self: mitsuba.BSDF, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Evaluate un-scattered transmission component of the BSDF
        
        This method will evaluate the un-scattered transmission
        (BSDFFlags::Null) of the BSDF for light arriving from direction ``w``.
        The default implementation returns zero.
        
        Parameter ``si``:
            A surface interaction data structure describing the underlying
            surface position. The incident direction is obtained from the
            field ``si.wi``.
        """
        ...

    def eval_pdf(self: mitsuba.BSDF, ctx: mitsuba.BSDFContext, si: mitsuba.SurfaceInteraction3f, wo: mitsuba.Vector3f, active: bool = True) -> Tuple[mitsuba.Color3f, float]:
        """
        Jointly evaluate the BSDF f(wi, wo) and the probability per unit solid
        angle of sampling the given direction. The result from the evaluated
        BSDF is multiplied by the cosine foreshortening term.
        
        Based on the information in the supplied query context ``ctx``, this
        method will either evaluate the entire BSDF or query individual
        components (e.g. the diffuse lobe). Only smooth (i.e. non Dirac-delta)
        components are supported: calling ``eval()`` on a perfectly specular
        material will return zero.
        
        This method provides access to the probability density that would
        result when supplying the same BSDF context and surface interaction
        data structures to the sample() method. It correctly handles changes
        in probability when only a subset of the components is chosen for
        sampling (this can be done using the BSDFContext::component and
        BSDFContext::type_mask fields).
        
        Note that the incident direction does not need to be explicitly
        specified. It is obtained from the field ``si.wi``.
        
        Parameter ``ctx``:
            A context data structure describing which lobes to evaluate, and
            whether radiance or importance are being transported.
        
        Parameter ``si``:
            A surface interaction data structure describing the underlying
            surface position. The incident direction is obtained from the
            field ``si.wi``.
        
        Parameter ``wo``:
            The outgoing direction
        """
        ...

    def eval_pdf_sample(self: mitsuba.BSDF, ctx: mitsuba.BSDFContext, si: mitsuba.SurfaceInteraction3f, wo: mitsuba.Vector3f, sample1: float, sample2: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.Color3f, float, mitsuba.BSDFSample3f, mitsuba.Color3f]:
        """
        Jointly evaluate the BSDF f(wi, wo) and the probability per unit solid
        angle of sampling the given direction. The result from the evaluated
        BSDF is multiplied by the cosine foreshortening term.
        
        Based on the information in the supplied query context ``ctx``, this
        method will either evaluate the entire BSDF or query individual
        components (e.g. the diffuse lobe). Only smooth (i.e. non Dirac-delta)
        components are supported: calling ``eval()`` on a perfectly specular
        material will return zero.
        
        This method provides access to the probability density that would
        result when supplying the same BSDF context and surface interaction
        data structures to the sample() method. It correctly handles changes
        in probability when only a subset of the components is chosen for
        sampling (this can be done using the BSDFContext::component and
        BSDFContext::type_mask fields).
        
        Note that the incident direction does not need to be explicitly
        specified. It is obtained from the field ``si.wi``.
        
        Parameter ``ctx``:
            A context data structure describing which lobes to evaluate, and
            whether radiance or importance are being transported.
        
        Parameter ``si``:
            A surface interaction data structure describing the underlying
            surface position. The incident direction is obtained from the
            field ``si.wi``.
        
        Parameter ``wo``:
            The outgoing direction
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    @overload
    def flags(self: mitsuba.BSDF, index: int, active: bool = True) -> int:
        """
        Flags for a specific component of this BSDF.
        
        """
        ...

    @overload
    def flags(self: mitsuba.BSDF) -> int:
        """
        Flags for all components combined.
        """
        ...

    def has_attribute(self: mitsuba.BSDF, name: str, active: bool = True) -> bool:
        """
        Returns whether this BSDF contains the specified attribute.
        
        Parameter ``name``:
            Name of the attribute
        """
        ...

    def id(self: mitsuba.BSDF) -> str:
        """
        Return a string identifier
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def needs_differentials(self: mitsuba.BSDF) -> bool:
        """
        Does the implementation require access to texture-space differentials?
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def pdf(self: mitsuba.BSDF, ctx: mitsuba.BSDFContext, si: mitsuba.SurfaceInteraction3f, wo: mitsuba.Vector3f, active: bool = True) -> float:
        """
        Compute the probability per unit solid angle of sampling a given
        direction
        
        This method provides access to the probability density that would
        result when supplying the same BSDF context and surface interaction
        data structures to the sample() method. It correctly handles changes
        in probability when only a subset of the components is chosen for
        sampling (this can be done using the BSDFContext::component and
        BSDFContext::type_mask fields).
        
        Note that the incident direction does not need to be explicitly
        specified. It is obtained from the field ``si.wi``.
        
        Parameter ``ctx``:
            A context data structure describing which lobes to evaluate, and
            whether radiance or importance are being transported.
        
        Parameter ``si``:
            A surface interaction data structure describing the underlying
            surface position. The incident direction is obtained from the
            field ``si.wi``.
        
        Parameter ``wo``:
            The outgoing direction
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample(self: mitsuba.BSDF, ctx: mitsuba.BSDFContext, si: mitsuba.SurfaceInteraction3f, sample1: float, sample2: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.BSDFSample3f, mitsuba.Color3f]:
        """
        Importance sample the BSDF model
        
        The function returns a sample data structure along with the importance
        weight, which is the value of the BSDF divided by the probability
        density, and multiplied by the cosine foreshortening factor (if needed
        --- it is omitted for degenerate BSDFs like smooth
        mirrors/dielectrics).
        
        If the supplied context data structures selects subset of components
        in a multi-lobe BRDF model, the sampling is restricted to this subset.
        Depending on the provided transport type, either the BSDF or its
        adjoint version is sampled.
        
        When sampling a continuous/non-delta component, this method also
        multiplies by the cosine foreshortening factor with respect to the
        sampled direction.
        
        Parameter ``ctx``:
            A context data structure describing which lobes to sample, and
            whether radiance or importance are being transported.
        
        Parameter ``si``:
            A surface interaction data structure describing the underlying
            surface position. The incident direction is obtained from the
            field ``si.wi``.
        
        Parameter ``sample1``:
            A uniformly distributed sample on :math:`[0,1]`. It is used to
            select the BSDF lobe in multi-lobe models.
        
        Parameter ``sample2``:
            A uniformly distributed sample on :math:`[0,1]^2`. It is used to
            generate the sampled direction.
        
        Returns:
            A pair (bs, value) consisting of
        
        bs: Sampling record, indicating the sampled direction, PDF values and
        other information. The contents are undefined if sampling failed.
        
        value: The BSDF value divided by the probability (multiplied by the
        cosine foreshortening factor when a non-delta component is sampled). A
        zero spectrum indicates that sampling failed.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class BSDFContext:
    """
    Context data structure for BSDF evaluation and sampling
    
    BSDF models in Mitsuba can be queried and sampled using a variety of
    different modes -- for instance, a rendering algorithm can indicate
    whether radiance or importance is being transported, and it can also
    restrict evaluation and sampling to a subset of lobes in a a multi-
    lobe BSDF model.
    
    The BSDFContext data structure encodes these preferences and is
    supplied to most BSDF methods.
    """

    @overload
    def __init__(self: mitsuba.BSDFContext, mode: mitsuba.TransportMode = TransportMode.Radiance) -> None:
        """
        //! @}
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BSDFContext, mode: mitsuba.TransportMode, type_mask: int, component: int) -> None: ...
    component = ...
    """
    Integer value of requested BSDF component index to be
    sampled/evaluated.
    """
    mode = ...
    "Transported mode (radiance or importance)"
    type_mask = ...

    def is_enabled(self: mitsuba.BSDFContext, type: mitsuba.BSDFFlags, component: int = 0) -> bool:
        """
        Checks whether a given BSDF component type and BSDF component index
        are enabled in this context.
        """
        ...

    def reverse(self: mitsuba.BSDFContext) -> None:
        """
        Reverse the direction of light transport in the record
        
        This updates the transport mode (radiance to importance and vice
        versa).
        """
        ...

    ...

class BSDFFlags:
    """
    This list of flags is used to classify the different types of lobes
    that are implemented in a BSDF instance.
    
    They are also useful for picking out individual components, e.g., by
    setting combinations in BSDFContext::type_mask.
    
    Members:
    
      Empty : No flags set (default value)
    
      Null : 'null' scattering event, i.e. particles do not undergo deflection
    
      DiffuseReflection : Ideally diffuse reflection
    
      DiffuseTransmission : Ideally diffuse transmission
    
      GlossyReflection : Glossy reflection
    
      GlossyTransmission : Glossy transmission
    
      DeltaReflection : Reflection into a discrete set of directions
    
      DeltaTransmission : Transmission into a discrete set of directions
    
      Anisotropic : The lobe is not invariant to rotation around the normal
    
      SpatiallyVarying : The BSDF depends on the UV coordinates
    
      NonSymmetric : Flags non-symmetry (e.g. transmission in dielectric materials)
    
      FrontSide : Supports interactions on the front-facing side
    
      BackSide : Supports interactions on the back-facing side
    
      Reflection : Any reflection component (scattering into discrete, 1D, or 2D set of
    directions)
    
      Transmission : Any transmission component (scattering into discrete, 1D, or 2D set of
    directions)
    
      Diffuse : Diffuse scattering into a 2D set of directions
    
      Glossy : Non-diffuse scattering into a 2D set of directions
    
      Smooth : Scattering into a 2D set of directions
    
      Delta : Scattering into a discrete set of directions
    
      Delta1D : Scattering into a 1D space of directions
    
      All : Any kind of scattering
    """

    def __init__(self: mitsuba.BSDFFlags, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    All = 511
    """
      All : Any kind of scattering
    """
    Anisotropic = 4096
    """
      Anisotropic : The lobe is not invariant to rotation around the normal
    """
    BackSide = 65536
    """
      BackSide : Supports interactions on the back-facing side
    """
    Delta = 97
    """
      DeltaReflection : Reflection into a discrete set of directions
      DeltaTransmission : Transmission into a discrete set of directions
      Delta : Scattering into a discrete set of directions
      Delta1D : Scattering into a 1D space of directions
    """
    Delta1D = 384
    """
      Delta1D : Scattering into a 1D space of directions
    """
    DeltaReflection = 32
    """
      DeltaReflection : Reflection into a discrete set of directions
    """
    DeltaTransmission = 64
    """
      DeltaTransmission : Transmission into a discrete set of directions
    """
    Diffuse = 6
    """
      DiffuseReflection : Ideally diffuse reflection
      DiffuseTransmission : Ideally diffuse transmission
      Diffuse : Diffuse scattering into a 2D set of directions
    """
    DiffuseReflection = 2
    """
      DiffuseReflection : Ideally diffuse reflection
    """
    DiffuseTransmission = 4
    """
      DiffuseTransmission : Ideally diffuse transmission
    """
    Empty = 0
    """
      Empty : No flags set (default value)
    """
    FrontSide = 32768
    """
      FrontSide : Supports interactions on the front-facing side
    """
    Glossy = 24
    """
      GlossyReflection : Glossy reflection
      GlossyTransmission : Glossy transmission
      Glossy : Non-diffuse scattering into a 2D set of directions
    """
    GlossyReflection = 8
    """
      GlossyReflection : Glossy reflection
    """
    GlossyTransmission = 16
    """
      GlossyTransmission : Glossy transmission
    """
    NonSymmetric = 16384
    """
      NonSymmetric : Flags non-symmetry (e.g. transmission in dielectric materials)
    """
    Null = 1
    """
      Null : 'null' scattering event, i.e. particles do not undergo deflection
    """
    Reflection = 170
    """
      Reflection : Any reflection component (scattering into discrete, 1D, or 2D set of
    """
    Smooth = 30
    """
      Smooth : Scattering into a 2D set of directions
    """
    SpatiallyVarying = 8192
    """
      SpatiallyVarying : The BSDF depends on the UV coordinates
    """
    Transmission = 341
    """
      Transmission : Any transmission component (scattering into discrete, 1D, or 2D set of
    """

    ...

class BSDFSample3f:
    """
    Data structure holding the result of BSDF sampling operations.
    """

    @overload
    def __init__(self: mitsuba.BSDFSample3f) -> None: ...
    @overload
    def __init__(self: mitsuba.BSDFSample3f, wo: mitsuba.Vector3f) -> None:
        """
        Given a surface interaction and an incident/exitant direction pair
        (wi, wo), create a query record to evaluate the BSDF or its sampling
        density.
        
        By default, all components will be sampled regardless of what measure
        they live on.
        
        Parameter ``wo``:
            An outgoing direction in local coordinates. This should be a
            normalized direction vector that points *away* from the scattering
            event.
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BSDFSample3f, bs: mitsuba.BSDFSample3f) -> None:
        """
        Copy constructor
        """
        ...

    eta = ...
    "Relative index of refraction in the sampled direction"
    pdf = ...
    "Probability density at the sample"
    sampled_component = ...
    "Stores the component index that was sampled by BSDF::sample()"
    sampled_type = ...
    "Stores the component type that was sampled by BSDF::sample()"
    wo = ...
    "Normalized outgoing direction in local coordinates"

    def assign(self: mitsuba.BSDFSample3f, arg0: mitsuba.BSDFSample3f) -> None: ...
    ...

class Bitmap(Object):
    """
    General-purpose bitmap class with read and write support for several
    common file formats.
    
    This class handles loading of PNG, JPEG, BMP, TGA, as well as OpenEXR
    files, and it supports writing of PNG, JPEG and OpenEXR files.
    
    PNG and OpenEXR files are optionally annotated with string-valued
    metadata, and the gamma setting can be stored as well. Please see the
    class methods and enumerations for further detail.
    """

    @overload
    def __init__(self: mitsuba.Bitmap, pixel_format: mitsuba.Bitmap.PixelFormat, component_format: mitsuba.Struct.Type, size, channel_count: int = 0, channel_names: List[str] = []) -> None:
        """
        Create a bitmap of the specified type and allocate the necessary
        amount of memory
        
        Parameter ``pixel_format``:
            Specifies the pixel format (e.g. RGBA or Luminance-only)
        
        Parameter ``component_format``:
            Specifies how the per-pixel components are encoded (e.g. unsigned
            8 bit integers or 32-bit floating point values). The component
            format struct_type_v<Float> will be translated to the
            corresponding compile-time precision type (Float32 or Float64).
        
        Parameter ``size``:
            Specifies the horizontal and vertical bitmap size in pixels
        
        Parameter ``channel_count``:
            Channel count of the image. This parameter is only required when
            ``pixel_format`` = PixelFormat::MultiChannel
        
        Parameter ``channel_names``:
            Channel names of the image. This parameter is optional, and only
            used when ``pixel_format`` = PixelFormat::MultiChannel
        
        Parameter ``data``:
            External pointer to the image data. If set to ``nullptr``, the
            implementation will allocate memory itself.
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Bitmap, arg0: mitsuba.Bitmap) -> None: ...
    @overload
    def __init__(self: mitsuba.Bitmap, path: mitsuba.filesystem.path, format: mitsuba.Bitmap.FileFormat = FileFormat.Auto) -> None: ...
    @overload
    def __init__(self: mitsuba.Bitmap, stream: mitsuba.Stream, format: mitsuba.Bitmap.FileFormat = FileFormat.Auto) -> None: ...
    @overload
    def __init__(self: mitsuba.Bitmap, array: mitsuba.PyObjectWrapper, pixel_format: object = None, channel_names: List[str] = []) -> None:
        """
        Initialize a Bitmap from any array that implements ``__array_interface__``
        """
        ...

    class AlphaTransform:
        """
        Type of alpha transformation
        
        Members:
        
          Empty : No transformation (default)
        
          Premultiply : No transformation (default)
        
          Unpremultiply : No transformation (default)
        """

        def __init__(self: mitsuba.Bitmap.AlphaTransform, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        Empty = 0
        """
          Empty : No transformation (default)
        """
        Premultiply = 1
        """
          Premultiply : No transformation (default)
        """
        Unpremultiply = 2
        """
          Unpremultiply : No transformation (default)
        """

        ...

    class FileFormat:
        """
        Supported image file formats
        
        Members:
        
          PNG : Portable network graphics
        
        The following is supported:
        
        * Loading and saving of 8/16-bit per component bitmaps for all pixel
        formats (Y, YA, RGB, RGBA)
        
        * Loading and saving of 1-bit per component mask bitmaps
        
        * Loading and saving of string-valued metadata fields
        
          OpenEXR : OpenEXR high dynamic range file format developed by Industrial Light &
        Magic (ILM)
        
        The following is supported:
        
        * Loading and saving of Float16 / Float32/ UInt32 bitmaps with all
        supported RGB/Luminance/Alpha combinations
        
        * Loading and saving of spectral bitmaps
        
        * Loading and saving of XYZ tristimulus bitmaps
        
        * Loading and saving of string-valued metadata fields
        
        The following is *not* supported:
        
        * Saving of tiled images, tile-based read access
        
        * Display windows that are different than the data window
        
        * Loading of spectrum-valued bitmaps
        
          RGBE : RGBE image format by Greg Ward
        
        The following is supported
        
        * Loading and saving of Float32 - based RGB bitmaps
        
          PFM : PFM (Portable Float Map) image format
        
        The following is supported
        
        * Loading and saving of Float32 - based Luminance or RGB bitmaps
        
          PPM : PPM (Portable Pixel Map) image format
        
        The following is supported
        
        * Loading and saving of UInt8 and UInt16 - based RGB bitmaps
        
          JPEG : Joint Photographic Experts Group file format
        
        The following is supported:
        
        * Loading and saving of 8 bit per component RGB and luminance bitmaps
        
          TGA : Truevision Advanced Raster Graphics Array file format
        
        The following is supported:
        
        * Loading of uncompressed 8-bit RGB/RGBA files
        
          BMP : Windows Bitmap file format
        
        The following is supported:
        
        * Loading of uncompressed 8-bit luminance and RGBA bitmaps
        
          Unknown : Unknown file format
        
          Auto : Automatically detect the file format
        
        Note: this flag only applies when loading a file. In this case, the
        source stream must support the ``seek()`` operation.
        """

        def __init__(self: mitsuba.Bitmap.FileFormat, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        Auto = 9
        """
          Auto : Automatically detect the file format
        """
        BMP = 7
        """
          BMP : Windows Bitmap file format
        """
        JPEG = 5
        """
          JPEG : Joint Photographic Experts Group file format
        """
        OpenEXR = 1
        """
          OpenEXR : OpenEXR high dynamic range file format developed by Industrial Light &
        """
        PFM = 3
        """
          PFM : PFM (Portable Float Map) image format
        """
        PNG = 0
        """
          PNG : Portable network graphics
        """
        PPM = 4
        """
          PPM : PPM (Portable Pixel Map) image format
        """
        RGBE = 2
        """
          RGBE : RGBE image format by Greg Ward
        """
        TGA = 6
        """
          TGA : Truevision Advanced Raster Graphics Array file format
        """
        Unknown = 8
        """
          Unknown : Unknown file format
        """

        ...

    class PixelFormat:
        """
        This enumeration lists all pixel format types supported by the Bitmap
        class. This both determines the number of channels, and how they
        should be interpreted
        
        Members:
        
          Y : Single-channel luminance bitmap
        
          YA : Two-channel luminance + alpha bitmap
        
          RGB : RGB bitmap
        
          RGBA : RGB bitmap + alpha channel
        
          RGBW : RGB bitmap + weight (used by ImageBlock)
        
          RGBAW : RGB bitmap + alpha channel + weight (used by ImageBlock)
        
          XYZ : XYZ tristimulus bitmap
        
          XYZA : XYZ tristimulus + alpha channel
        
          MultiChannel : Arbitrary multi-channel bitmap without a fixed interpretation
        """

        def __init__(self: mitsuba.Bitmap.PixelFormat, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        MultiChannel = 8
        """
          MultiChannel : Arbitrary multi-channel bitmap without a fixed interpretation
        """
        RGB = 2
        """
          RGB : RGB bitmap
          RGBA : RGB bitmap + alpha channel
          RGBW : RGB bitmap + weight (used by ImageBlock)
          RGBAW : RGB bitmap + alpha channel + weight (used by ImageBlock)
        """
        RGBA = 3
        """
          RGBA : RGB bitmap + alpha channel
          RGBAW : RGB bitmap + alpha channel + weight (used by ImageBlock)
        """
        RGBAW = 5
        """
          RGBAW : RGB bitmap + alpha channel + weight (used by ImageBlock)
        """
        XYZ = 6
        """
          XYZ : XYZ tristimulus bitmap
          XYZA : XYZ tristimulus + alpha channel
        """
        XYZA = 7
        """
          XYZA : XYZ tristimulus + alpha channel
        """
        Y = 0
        """
          Y : Single-channel luminance bitmap
          YA : Two-channel luminance + alpha bitmap
        """
        YA = 1
        """
          YA : Two-channel luminance + alpha bitmap
        """

        ...

    ptr = ...

    Float16 = 9
    """
      Float16 : 
    """
    Float32 = 10
    """
      Float32 : 
    """
    Float64 = 11
    """
      Float64 : 
    """
    Int16 = 4
    """
      Int16 : 
    """
    Int32 = 6
    """
      Int32 : 
    """
    Int64 = 8
    """
      Int64 : 
    """
    Int8 = 2
    """
      Int8 : 
    """
    Invalid = 0
    """
      Invalid : 
    """
    UInt16 = 3
    """
      UInt16 : 
    """
    UInt32 = 5
    """
      UInt32 : 
    """
    UInt64 = 7
    """
      UInt64 : 
    """
    UInt8 = 1
    """
      UInt8 : 
    """

    @overload
    def accumulate(self: mitsuba.Bitmap, bitmap: mitsuba.Bitmap, source_offset, target_offset, size) -> None:
        """
        Accumulate the contents of another bitmap into the region with the
        specified offset
        
        Out-of-bounds regions are safely ignored. It is assumed that ``bitmap
        != this``.
        
        Remark:
            This function throws an exception when the bitmaps use different
            component formats or channels.
        
        """
        ...

    @overload
    def accumulate(self: mitsuba.Bitmap, bitmap: mitsuba.Bitmap, target_offset) -> None:
        """
        Accumulate the contents of another bitmap into the region with the
        specified offset
        
        This convenience function calls the main ``accumulate()``
        implementation with ``size`` set to ``bitmap->size()`` and
        ``source_offset`` set to zero. Out-of-bounds regions are ignored. It
        is assumed that ``bitmap != this``.
        
        Remark:
            This function throws an exception when the bitmaps use different
            component formats or channels.
        
        """
        ...

    @overload
    def accumulate(self: mitsuba.Bitmap, bitmap: mitsuba.Bitmap) -> None:
        """
        Accumulate the contents of another bitmap into the region with the
        specified offset
        
        This convenience function calls the main ``accumulate()``
        implementation with ``size`` set to ``bitmap->size()`` and
        ``source_offset`` and ``target_offset`` set to zero. Out-of-bounds
        regions are ignored. It is assumed that ``bitmap != this``.
        
        Remark:
            This function throws an exception when the bitmaps use different
            component formats or channels.
        """
        ...

    def buffer_size(self: mitsuba.Bitmap) -> int:
        """
        Return the bitmap size in bytes (excluding metadata)
        """
        ...

    def bytes_per_pixel(self: mitsuba.Bitmap) -> int:
        """
        Return the number bytes of storage used per pixel
        """
        ...

    def channel_count(self: mitsuba.Bitmap) -> int:
        """
        Return the number of channels used by this bitmap
        """
        ...

    def clear(self: mitsuba.Bitmap) -> None:
        """
        Clear the bitmap to zero
        """
        ...

    def component_format(self: mitsuba.Bitmap) -> mitsuba.Struct.Type:
        """
        Return the component format of this bitmap
        """
        ...

    @overload
    def convert(self: mitsuba.Bitmap, pixel_format: object = None, component_format: object = None, srgb_gamma: object = None, alpha_transform: mitsuba.Bitmap.AlphaTransform = AlphaTransform.Empty) -> mitsuba.Bitmap:
        """
        Convert the bitmap into another pixel and/or component format
        
        This helper function can be used to efficiently convert a bitmap
        between different underlying representations. For instance, it can
        translate a uint8 sRGB bitmap to a linear float32 XYZ bitmap based on
        half-, single- or double-precision floating point-backed storage.
        
        This function roughly does the following:
        
        * For each pixel and channel, it converts the associated value into a
        normalized linear-space form (any gamma of the source bitmap is
        removed)
        
        * gamma correction (sRGB ramp) is applied if ``srgb_gamma`` is
        ``True``
        
        * The corrected value is clamped against the representable range of
        the desired component format.
        
        * The clamped gamma-corrected value is then written to the new bitmap
        
        If the pixel formats differ, this function will also perform basic
        conversions (e.g. spectrum to rgb, luminance to uniform spectrum
        values, etc.)
        
        Note that the alpha channel is assumed to be linear in both the source
        and target bitmap, hence it won't be affected by any gamma-related
        transformations.
        
        Remark:
            This ``convert()`` variant usually returns a new bitmap instance.
            When the conversion would just involve copying the original
            bitmap, the function becomes a no-op and returns the current
            instance.
        
        pixel_format Specifies the desired pixel format
        
        component_format Specifies the desired component format
        
        srgb_gamma Specifies whether a sRGB gamma ramp should be applied to
        the output values.
        
        """
        ...

    @overload
    def convert(self: mitsuba.Bitmap, target: mitsuba.Bitmap) -> None: ...
    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def has_alpha(self: mitsuba.Bitmap) -> bool:
        """
        Return whether this image has an alpha channel
        """
        ...

    def height(self: mitsuba.Bitmap) -> int:
        """
        Return the bitmap's height in pixels
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def metadata(self: mitsuba.Bitmap):
        """
        Return a Properties object containing the image metadata
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def pixel_count(self: mitsuba.Bitmap) -> int:
        """
        Return the total number of pixels
        """
        ...

    def pixel_format(self: mitsuba.Bitmap) -> mitsuba.Bitmap.PixelFormat:
        """
        Return the pixel format of this bitmap
        """
        ...

    def premultiplied_alpha(self: mitsuba.Bitmap) -> bool:
        """
        Return whether the bitmap uses premultiplied alpha
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    @overload
    def resample(self: mitsuba.Bitmap, target: mitsuba.Bitmap, rfilter, bc: Tuple[mitsuba.FilterBoundaryCondition, mitsuba.FilterBoundaryCondition] = (FilterBoundaryCondition.Clamp, FilterBoundaryCondition.Clamp), clamp: Tuple[float, float] = (-inf, inf), temp: mitsuba.Bitmap = None) -> None:
        """
        Up- or down-sample this image to a different resolution
        
        Uses the provided reconstruction filter and accounts for the requested
        horizontal and vertical boundary conditions when looking up data
        outside of the input domain.
        
        A minimum and maximum image value can be specified to prevent to
        prevent out-of-range values that are created by the resampling
        process.
        
        The optional ``temp`` parameter can be used to pass an image of
        resolution ``Vector2u(target->width(), this->height())`` to avoid
        intermediate memory allocations.
        
        Parameter ``target``:
            Pre-allocated bitmap of the desired target resolution
        
        Parameter ``rfilter``:
            A separable image reconstruction filter (default: 2-lobe Lanczos
            filter)
        
        Parameter ``bch``:
            Horizontal and vertical boundary conditions (default: clamp)
        
        Parameter ``clamp``:
            Filtered image pixels will be clamped to the following range.
            Default: -infinity..infinity (i.e. no clamping is used)
        
        Parameter ``temp``:
            Optional: image for intermediate computations
        
        """
        ...

    @overload
    def resample(self: mitsuba.Bitmap, res, rfilter, bc: Tuple[mitsuba.FilterBoundaryCondition, mitsuba.FilterBoundaryCondition] = (FilterBoundaryCondition.Clamp, FilterBoundaryCondition.Clamp), clamp: Tuple[float, float] = (-inf, inf)) -> mitsuba.Bitmap:
        """
        Up- or down-sample this image to a different resolution
        
        This version is similar to the above resample() function -- the main
        difference is that it does not work with preallocated bitmaps and
        takes the desired output resolution as first argument.
        
        Uses the provided reconstruction filter and accounts for the requested
        horizontal and vertical boundary conditions when looking up data
        outside of the input domain.
        
        A minimum and maximum image value can be specified to prevent to
        prevent out-of-range values that are created by the resampling
        process.
        
        Parameter ``res``:
            Desired output resolution
        
        Parameter ``rfilter``:
            A separable image reconstruction filter (default: 2-lobe Lanczos
            filter)
        
        Parameter ``bch``:
            Horizontal and vertical boundary conditions (default: clamp)
        
        Parameter ``clamp``:
            Filtered image pixels will be clamped to the following range.
            Default: -infinity..infinity (i.e. no clamping is used)
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_premultiplied_alpha(self: mitsuba.Bitmap, arg0: bool) -> None:
        """
        Specify whether the bitmap uses premultiplied alpha
        """
        ...

    def set_srgb_gamma(self: mitsuba.Bitmap, arg0: bool) -> None:
        """
        Specify whether the bitmap uses an sRGB gamma encoding
        """
        ...

    def size(self: mitsuba.Bitmap):
        """
        Return the bitmap dimensions in pixels
        """
        ...

    def split(self: mitsuba.Bitmap) -> List[Tuple[str, mitsuba.Bitmap]]:
        """
        Split an multi-channel image buffer (e.g. from an OpenEXR image with
        lots of AOVs) into its constituent layers
        """
        ...

    def srgb_gamma(self: mitsuba.Bitmap) -> bool:
        """
        Return whether the bitmap uses an sRGB gamma encoding
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def vflip(self: mitsuba.Bitmap) -> None:
        """
        Vertically flip the bitmap
        """
        ...

    def width(self: mitsuba.Bitmap) -> int:
        """
        Return the bitmap's width in pixels
        """
        ...

    @overload
    def write(self: mitsuba.Bitmap, stream: mitsuba.Stream, format: mitsuba.Bitmap.FileFormat = FileFormat.Auto, quality: int = -1) -> None:
        """
        Write an encoded form of the bitmap to a stream using the specified
        file format
        
        Parameter ``stream``:
            Target stream that will receive the encoded output
        
        Parameter ``format``:
            Target file format (OpenEXR, PNG, etc.) Detected from the filename
            by default.
        
        Parameter ``quality``:
            Depending on the file format, this parameter takes on a slightly
            different meaning:
        
        * PNG images: Controls how much libpng will attempt to compress the
        output (with 1 being the lowest and 9 denoting the highest
        compression). The default argument uses the compression level 5.
        
        * JPEG images: denotes the desired quality (between 0 and 100). The
        default argument (-1) uses the highest quality (100).
        
        * OpenEXR images: denotes the quality level of the DWAB compressor,
        with higher values corresponding to a lower quality. A value of 45 is
        recommended as the default for lossy compression. The default argument
        (-1) causes the implementation to switch to the lossless PIZ
        compressor.
        
        """
        ...

    @overload
    def write(self: mitsuba.Bitmap, path: mitsuba.filesystem.path, format: mitsuba.Bitmap.FileFormat = FileFormat.Auto, quality: int = -1) -> None:
        """
        Write an encoded form of the bitmap to a file using the specified file
        format
        
        Parameter ``path``:
            Target file path on disk
        
        Parameter ``format``:
            Target file format (FileFormat::OpenEXR, FileFormat::PNG, etc.)
            Detected from the filename by default.
        
        Parameter ``quality``:
            Depending on the file format, this parameter takes on a slightly
            different meaning:
        
        * PNG images: Controls how much libpng will attempt to compress the
        output (with 1 being the lowest and 9 denoting the highest
        compression). The default argument uses the compression level 5.
        
        * JPEG images: denotes the desired quality (between 0 and 100). The
        default argument (-1) uses the highest quality (100).
        
        * OpenEXR images: denotes the quality level of the DWAB compressor,
        with higher values corresponding to a lower quality. A value of 45 is
        recommended as the default for lossy compression. The default argument
        (-1) causes the implementation to switch to the lossless PIZ
        compressor.
        """
        ...

    def write_async(self: mitsuba.Bitmap, path: mitsuba.filesystem.path, format: mitsuba.Bitmap.FileFormat = FileFormat.Auto, quality: int = -1) -> None:
        """
        Equivalent to write(), but executes asynchronously on a different
        thread
        """
        ...

    ...

class ReconstructionFilter(Object):
    """
    Generic interface to separable image reconstruction filters
    
    When resampling bitmaps or adding samples to a rendering in progress,
    Mitsuba first convolves them with a image reconstruction filter.
    Various kinds are implemented as subclasses of this interface.
    
    Because image filters are generally too expensive to evaluate for each
    sample, the implementation of this class internally precomputes an
    discrete representation, whose resolution given by
    MI_FILTER_RESOLUTION.
    """

    ptr = ...

    def border_size(self: mitsuba.ReconstructionFilter) -> int:
        """
        Return the block border size required when rendering with this filter
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.ReconstructionFilter, x: float, active: bool = True) -> float:
        """
        Evaluate the filter function
        """
        ...

    def eval_discretized(self: mitsuba.ReconstructionFilter, x: float, active: bool = True) -> float:
        """
        Evaluate a discretized version of the filter (generally faster than
        'eval')
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def is_box_filter(self: mitsuba.ReconstructionFilter) -> bool:
        """
        Check whether this is a box filter?
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def radius(self: mitsuba.ReconstructionFilter) -> float:
        """
        Return the filter's width
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Bool: ...

class BoundingBox2f:
    """
    Generic n-dimensional bounding box data structure
    
    Maintains a minimum and maximum position along each dimension and
    provides various convenience functions for querying and modifying
    them.
    
    This class is parameterized by the underlying point data structure,
    which permits the use of different scalar types and dimensionalities,
    e.g.
    
    ```
    BoundingBox<Point3i> integer_bbox(Point3i(0, 1, 3), Point3i(4, 5, 6));
    BoundingBox<Point2d> double_bbox(Point2d(0.0, 1.0), Point2d(4.0, 5.0));
    ```
    
    Template parameter ``T``:
        The underlying point data type (e.g. ``Point2d``)
    """

    @overload
    def __init__(self: mitsuba.BoundingBox2f) -> None:
        """
        Create a new invalid bounding box
        
        Initializes the components of the minimum and maximum position to
        :math:`\infty` and :math:`-\infty`, respectively.
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BoundingBox2f, p: mitsuba.Point2f) -> None:
        """
        Create a collapsed bounding box from a single point
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BoundingBox2f, min: mitsuba.Point2f, max: mitsuba.Point2f) -> None:
        """
        Create a bounding box from two positions
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BoundingBox2f, arg0: mitsuba.BoundingBox2f) -> None:
        """
        Copy constructor
        """
        ...

    max = ...
    min = ...

    def center(self: mitsuba.BoundingBox2f) -> mitsuba.Point2f:
        """
        Return the center point
        """
        ...

    def clip(self: mitsuba.BoundingBox2f, arg0: mitsuba.BoundingBox2f) -> None:
        """
        Clip this bounding box to another bounding box
        """
        ...

    def collapsed(self: mitsuba.BoundingBox2f) -> bool:
        """
        Check whether this bounding box has collapsed to a point, line, or
        plane
        """
        ...

    @overload
    def contains(self: mitsuba.BoundingBox2f, p: mitsuba.Point2f, strict: bool = False) -> bool:
        """
        Check whether a point lies *on* or *inside* the bounding box
        
        Parameter ``p``:
            The point to be tested
        
        Template parameter ``Strict``:
            Set this parameter to ``True`` if the bounding box boundary should
            be excluded in the test
        
        Remark:
            In the Python bindings, the 'Strict' argument is a normal function
            parameter with default value ``False``.
        
        """
        ...

    @overload
    def contains(self: mitsuba.BoundingBox2f, bbox: mitsuba.BoundingBox2f, strict: bool = False) -> bool:
        """
        Check whether a specified bounding box lies *on* or *within* the
        current bounding box
        
        Note that by definition, an 'invalid' bounding box (where
        min=:math:`\infty` and max=:math:`-\infty`) does not cover any space.
        Hence, this method will always return *true* when given such an
        argument.
        
        Template parameter ``Strict``:
            Set this parameter to ``True`` if the bounding box boundary should
            be excluded in the test
        
        Remark:
            In the Python bindings, the 'Strict' argument is a normal function
            parameter with default value ``False``.
        """
        ...

    def corner(self: mitsuba.BoundingBox2f, arg0: int) -> mitsuba.Point2f:
        """
        Return the position of a bounding box corner
        """
        ...

    @overload
    def distance(self: mitsuba.BoundingBox2f, arg0: mitsuba.Point2f) -> float:
        """
        Calculate the shortest distance between the axis-aligned bounding box
        and the point ``p``.
        
        """
        ...

    @overload
    def distance(self: mitsuba.BoundingBox2f, arg0: mitsuba.BoundingBox2f) -> float:
        """
        Calculate the shortest distance between the axis-aligned bounding box
        and ``bbox``.
        """
        ...

    @overload
    def expand(self: mitsuba.BoundingBox2f, arg0: mitsuba.Point2f) -> None:
        """
        Expand the bounding box to contain another point
        
        """
        ...

    @overload
    def expand(self: mitsuba.BoundingBox2f, arg0: mitsuba.BoundingBox2f) -> None:
        """
        Expand the bounding box to contain another bounding box
        """
        ...

    def extents(self: mitsuba.BoundingBox2f) -> mitsuba.Vector2f:
        """
        Calculate the bounding box extents
        
        Returns:
            ``max - min``
        """
        ...

    def major_axis(self: mitsuba.BoundingBox2f) -> int:
        """
        Return the dimension index with the index associated side length
        """
        ...

    def minor_axis(self: mitsuba.BoundingBox2f) -> int:
        """
        Return the dimension index with the shortest associated side length
        """
        ...

    def overlaps(self: mitsuba.BoundingBox2f, bbox: mitsuba.BoundingBox2f, strict: bool = False) -> bool:
        """
        Check two axis-aligned bounding boxes for possible overlap.
        
        Parameter ``Strict``:
            Set this parameter to ``True`` if the bounding box boundary should
            be excluded in the test
        
        Remark:
            In the Python bindings, the 'Strict' argument is a normal function
            parameter with default value ``False``.
        
        Returns:
            ``True`` If overlap was detected.
        """
        ...

    def reset(self: mitsuba.BoundingBox2f) -> None:
        """
        Mark the bounding box as invalid.
        
        This operation sets the components of the minimum and maximum position
        to :math:`\infty` and :math:`-\infty`, respectively.
        """
        ...

    @overload
    def squared_distance(self: mitsuba.BoundingBox2f, arg0: mitsuba.Point2f) -> float:
        """
        Calculate the shortest squared distance between the axis-aligned
        bounding box and the point ``p``.
        
        """
        ...

    @overload
    def squared_distance(self: mitsuba.BoundingBox2f, arg0: mitsuba.BoundingBox2f) -> float:
        """
        Calculate the shortest squared distance between the axis-aligned
        bounding box and ``bbox``.
        """
        ...

    def surface_area(self: mitsuba.BoundingBox2f) -> float:
        """
        Calculate the 2-dimensional surface area of a 3D bounding box
        """
        ...

    def valid(self: mitsuba.BoundingBox2f) -> bool:
        """
        Check whether this is a valid bounding box
        
        A bounding box ``bbox`` is considered to be valid when
        
        ```
        bbox.min[i] <= bbox.max[i]
        ```
        
        holds for each component ``i``.
        """
        ...

    def volume(self: mitsuba.BoundingBox2f) -> float:
        """
        Calculate the n-dimensional volume of the bounding box
        """
        ...

    ...

class BoundingBox3f:
    """
    Generic n-dimensional bounding box data structure
    
    Maintains a minimum and maximum position along each dimension and
    provides various convenience functions for querying and modifying
    them.
    
    This class is parameterized by the underlying point data structure,
    which permits the use of different scalar types and dimensionalities,
    e.g.
    
    ```
    BoundingBox<Point3i> integer_bbox(Point3i(0, 1, 3), Point3i(4, 5, 6));
    BoundingBox<Point2d> double_bbox(Point2d(0.0, 1.0), Point2d(4.0, 5.0));
    ```
    
    Template parameter ``T``:
        The underlying point data type (e.g. ``Point2d``)
    """

    @overload
    def __init__(self: mitsuba.BoundingBox3f) -> None:
        """
        Create a new invalid bounding box
        
        Initializes the components of the minimum and maximum position to
        :math:`\infty` and :math:`-\infty`, respectively.
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BoundingBox3f, p: mitsuba.Point3f) -> None:
        """
        Create a collapsed bounding box from a single point
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BoundingBox3f, min: mitsuba.Point3f, max: mitsuba.Point3f) -> None:
        """
        Create a bounding box from two positions
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BoundingBox3f, arg0: mitsuba.BoundingBox3f) -> None:
        """
        Copy constructor
        """
        ...

    max = ...
    min = ...

    def bounding_sphere(self: mitsuba.BoundingBox3f):
        """
        Create a bounding sphere, which contains the axis-aligned box
        """
        ...

    def center(self: mitsuba.BoundingBox3f) -> mitsuba.Point3f:
        """
        Return the center point
        """
        ...

    def clip(self: mitsuba.BoundingBox3f, arg0: mitsuba.BoundingBox3f) -> None:
        """
        Clip this bounding box to another bounding box
        """
        ...

    def collapsed(self: mitsuba.BoundingBox3f) -> bool:
        """
        Check whether this bounding box has collapsed to a point, line, or
        plane
        """
        ...

    @overload
    def contains(self: mitsuba.BoundingBox3f, p: mitsuba.Point3f, strict: bool = False) -> bool:
        """
        Check whether a point lies *on* or *inside* the bounding box
        
        Parameter ``p``:
            The point to be tested
        
        Template parameter ``Strict``:
            Set this parameter to ``True`` if the bounding box boundary should
            be excluded in the test
        
        Remark:
            In the Python bindings, the 'Strict' argument is a normal function
            parameter with default value ``False``.
        
        """
        ...

    @overload
    def contains(self: mitsuba.BoundingBox3f, bbox: mitsuba.BoundingBox3f, strict: bool = False) -> bool:
        """
        Check whether a specified bounding box lies *on* or *within* the
        current bounding box
        
        Note that by definition, an 'invalid' bounding box (where
        min=:math:`\infty` and max=:math:`-\infty`) does not cover any space.
        Hence, this method will always return *true* when given such an
        argument.
        
        Template parameter ``Strict``:
            Set this parameter to ``True`` if the bounding box boundary should
            be excluded in the test
        
        Remark:
            In the Python bindings, the 'Strict' argument is a normal function
            parameter with default value ``False``.
        """
        ...

    def corner(self: mitsuba.BoundingBox3f, arg0: int) -> mitsuba.Point3f:
        """
        Return the position of a bounding box corner
        """
        ...

    @overload
    def distance(self: mitsuba.BoundingBox3f, arg0: mitsuba.Point3f) -> float:
        """
        Calculate the shortest distance between the axis-aligned bounding box
        and the point ``p``.
        
        """
        ...

    @overload
    def distance(self: mitsuba.BoundingBox3f, arg0: mitsuba.BoundingBox3f) -> float:
        """
        Calculate the shortest distance between the axis-aligned bounding box
        and ``bbox``.
        """
        ...

    @overload
    def expand(self: mitsuba.BoundingBox3f, arg0: mitsuba.Point3f) -> None:
        """
        Expand the bounding box to contain another point
        
        """
        ...

    @overload
    def expand(self: mitsuba.BoundingBox3f, arg0: mitsuba.BoundingBox3f) -> None:
        """
        Expand the bounding box to contain another bounding box
        """
        ...

    def extents(self: mitsuba.BoundingBox3f) -> mitsuba.Vector3f:
        """
        Calculate the bounding box extents
        
        Returns:
            ``max - min``
        """
        ...

    def major_axis(self: mitsuba.BoundingBox3f) -> int:
        """
        Return the dimension index with the index associated side length
        """
        ...

    def minor_axis(self: mitsuba.BoundingBox3f) -> int:
        """
        Return the dimension index with the shortest associated side length
        """
        ...

    def overlaps(self: mitsuba.BoundingBox3f, bbox: mitsuba.BoundingBox3f, strict: bool = False) -> bool:
        """
        Check two axis-aligned bounding boxes for possible overlap.
        
        Parameter ``Strict``:
            Set this parameter to ``True`` if the bounding box boundary should
            be excluded in the test
        
        Remark:
            In the Python bindings, the 'Strict' argument is a normal function
            parameter with default value ``False``.
        
        Returns:
            ``True`` If overlap was detected.
        """
        ...

    def ray_intersect(self: mitsuba.BoundingBox3f, ray: mitsuba.Ray3f) -> Tuple[bool, float, float]:
        """
        Check if a ray intersects a bounding box
        
        Note that this function ignores the ``maxt`` value associated with the
        ray.
        """
        ...

    def reset(self: mitsuba.BoundingBox3f) -> None:
        """
        Mark the bounding box as invalid.
        
        This operation sets the components of the minimum and maximum position
        to :math:`\infty` and :math:`-\infty`, respectively.
        """
        ...

    @overload
    def squared_distance(self: mitsuba.BoundingBox3f, arg0: mitsuba.Point3f) -> float:
        """
        Calculate the shortest squared distance between the axis-aligned
        bounding box and the point ``p``.
        
        """
        ...

    @overload
    def squared_distance(self: mitsuba.BoundingBox3f, arg0: mitsuba.BoundingBox3f) -> float:
        """
        Calculate the shortest squared distance between the axis-aligned
        bounding box and ``bbox``.
        """
        ...

    def surface_area(self: mitsuba.BoundingBox3f) -> float:
        """
        Calculate the 2-dimensional surface area of a 3D bounding box
        """
        ...

    def valid(self: mitsuba.BoundingBox3f) -> bool:
        """
        Check whether this is a valid bounding box
        
        A bounding box ``bbox`` is considered to be valid when
        
        ```
        bbox.min[i] <= bbox.max[i]
        ```
        
        holds for each component ``i``.
        """
        ...

    def volume(self: mitsuba.BoundingBox3f) -> float:
        """
        Calculate the n-dimensional volume of the bounding box
        """
        ...

    ...

class BoundingSphere3f:
    """
    Generic n-dimensional bounding sphere data structure
    """

    @overload
    def __init__(self: mitsuba.BoundingSphere3f) -> None:
        """
        Construct bounding sphere(s) at the origin having radius zero
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BoundingSphere3f, arg0: mitsuba.Point3f, arg1: float) -> None:
        """
        Create bounding sphere(s) from given center point(s) with given
        size(s)
        
        """
        ...

    @overload
    def __init__(self: mitsuba.BoundingSphere3f, arg0: mitsuba.BoundingSphere3f) -> None: ...
    center = ...
    radius = ...

    def contains(self: mitsuba.BoundingSphere3f, p: mitsuba.Point3f, strict: bool = False) -> bool:
        """
        Check whether a point lies *on* or *inside* the bounding sphere
        
        Parameter ``p``:
            The point to be tested
        
        Template parameter ``Strict``:
            Set this parameter to ``True`` if the bounding sphere boundary
            should be excluded in the test
        
        Remark:
            In the Python bindings, the 'Strict' argument is a normal function
            parameter with default value ``False``.
        """
        ...

    def empty(self: mitsuba.BoundingSphere3f) -> bool:
        """
        Return whether this bounding sphere has a radius of zero or less.
        """
        ...

    def expand(self: mitsuba.BoundingSphere3f, arg0: mitsuba.Point3f) -> None:
        """
        Expand the bounding sphere radius to contain another point.
        """
        ...

    def ray_intersect(self: mitsuba.BoundingSphere3f, ray: mitsuba.Ray3f) -> Tuple[bool, float, float]:
        """
        Check if a ray intersects a bounding box
        """
        ...

    ...

class ChainTransform3d(Transform3d):
    """
    Encapsulates a 4x4 homogeneous coordinate transformation along with
    its inverse transpose
    
    The Transform class provides a set of overloaded matrix-vector
    multiplication operators for vectors, points, and normals (all of them
    behave differently under homogeneous coordinate transformations, hence
    the need to represent them using separate types)
    """

    inverse_transpose = ...
    matrix = ...

    def assign(self: mitsuba.Transform3d, arg0: mitsuba.Transform3d) -> None: ...
    @overload
    def has_scale(self: mitsuba.Transform3d) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform3d) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        """
        ...

    def inverse(self: mitsuba.Transform3d) -> mitsuba.Transform3d:
        """
        Compute the inverse of this transformation (involves just shuffles, no
        arithmetic)
        """
        ...

    def rotate(self: mitsuba.ChainTransform3d, angle: float) -> mitsuba.ChainTransform3d:
        """
        Create a rotation transformation in 2D. The angle is specified in
        degrees
        """
        ...

    def scale(self: mitsuba.ChainTransform3d, v: mitsuba.Point2d) -> mitsuba.ChainTransform3d:
        """
        Create a scale transformation
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform3d, p: mitsuba.Point2d) -> mitsuba.Point2d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform3d, v: mitsuba.Vector2d) -> mitsuba.Vector2d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        """
        ...

    def translate(self: mitsuba.ChainTransform3d, v: mitsuba.Point2d) -> mitsuba.ChainTransform3d:
        """
        Create a translation transformation
        """
        ...

    def translation(self: mitsuba.Transform3d) -> mitsuba.Vector2d:
        """
        Get the translation part of a matrix
        """
        ...

    ...

class ChainTransform3f(Transform3f):
    """
    Encapsulates a 4x4 homogeneous coordinate transformation along with
    its inverse transpose
    
    The Transform class provides a set of overloaded matrix-vector
    multiplication operators for vectors, points, and normals (all of them
    behave differently under homogeneous coordinate transformations, hence
    the need to represent them using separate types)
    """

    inverse_transpose = ...
    matrix = ...

    def assign(self: mitsuba.Transform3f, arg0: mitsuba.Transform3f) -> None: ...
    @overload
    def has_scale(self: mitsuba.Transform3f) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform3f) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        """
        ...

    def inverse(self: mitsuba.Transform3f) -> mitsuba.Transform3f:
        """
        Compute the inverse of this transformation (involves just shuffles, no
        arithmetic)
        """
        ...

    def rotate(self: mitsuba.ChainTransform3f, angle: float) -> mitsuba.ChainTransform3f:
        """
        Create a rotation transformation in 2D. The angle is specified in
        degrees
        """
        ...

    def scale(self: mitsuba.ChainTransform3f, v: mitsuba.Point2f) -> mitsuba.ChainTransform3f:
        """
        Create a scale transformation
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform3f, p: mitsuba.Point2f) -> mitsuba.Point2f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform3f, v: mitsuba.Vector2f) -> mitsuba.Vector2f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        """
        ...

    def translate(self: mitsuba.ChainTransform3f, v: mitsuba.Point2f) -> mitsuba.ChainTransform3f:
        """
        Create a translation transformation
        """
        ...

    def translation(self: mitsuba.Transform3f) -> mitsuba.Vector2f:
        """
        Get the translation part of a matrix
        """
        ...

    ...

class ChainTransform4d(Transform4d):
    """
    Encapsulates a 4x4 homogeneous coordinate transformation along with
    its inverse transpose
    
    The Transform class provides a set of overloaded matrix-vector
    multiplication operators for vectors, points, and normals (all of them
    behave differently under homogeneous coordinate transformations, hence
    the need to represent them using separate types)
    """

    inverse_transpose = ...
    matrix = ...

    def assign(self: mitsuba.Transform4d, arg0: mitsuba.Transform4d) -> None: ...
    def extract(self: mitsuba.Transform4d) -> mitsuba.Transform3d:
        """
        Extract a lower-dimensional submatrix
        """
        ...

    def from_frame(self: mitsuba.ChainTransform4d, frame) -> mitsuba.ChainTransform4d:
        """
        Creates a transformation that converts from 'frame' to the standard
        basis
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform4d) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform4d) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        """
        ...

    def inverse(self: mitsuba.Transform4d) -> mitsuba.Transform4d:
        """
        Compute the inverse of this transformation (involves just shuffles, no
        arithmetic)
        """
        ...

    def look_at(self: mitsuba.ChainTransform4d, origin: mitsuba.Point3d, target: mitsuba.Point3d, up: mitsuba.Point3d) -> mitsuba.ChainTransform4d:
        """
        Create a look-at camera transformation
        
        Parameter ``origin``:
            Camera position
        
        Parameter ``target``:
            Target vector
        
        Parameter ``up``:
            Up vector
        """
        ...

    def orthographic(self: mitsuba.ChainTransform4d, near: float, far: float) -> mitsuba.ChainTransform4d:
        """
        Create an orthographic transformation, which maps Z to [0,1] and
        leaves the X and Y coordinates untouched.
        
        Parameter ``near``:
            Near clipping plane
        
        Parameter ``far``:
            Far clipping plane
        """
        ...

    def perspective(self: mitsuba.ChainTransform4d, fov: float, near: float, far: float) -> mitsuba.ChainTransform4d:
        """
        Create a perspective transformation. (Maps [near, far] to [0, 1])
        
        Projects vectors in camera space onto a plane at z=1:
        
        x_proj = x / z y_proj = y / z z_proj = (far * (z - near)) / (z * (far-
        near))
        
        Camera-space depths are not mapped linearly!
        
        Parameter ``fov``:
            Field of view in degrees
        
        Parameter ``near``:
            Near clipping plane
        
        Parameter ``far``:
            Far clipping plane
        """
        ...

    def rotate(self: mitsuba.ChainTransform4d, axis: mitsuba.Point3d, angle: float) -> mitsuba.ChainTransform4d:
        """
        Create a rotation transformation around an arbitrary axis in 3D. The
        angle is specified in degrees
        """
        ...

    def scale(self: mitsuba.ChainTransform4d, v: mitsuba.Point3d) -> mitsuba.ChainTransform4d:
        """
        Create a scale transformation
        """
        ...

    def to_frame(self: mitsuba.ChainTransform4d, frame) -> mitsuba.ChainTransform4d:
        """
        Creates a transformation that converts from the standard basis to
        'frame'
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4d, p: mitsuba.Point3d) -> mitsuba.Point3d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4d, ray):
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4d, v: mitsuba.Vector3d) -> mitsuba.Vector3d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4d, n: mitsuba.Normal3d) -> mitsuba.Normal3d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        """
        ...

    def translate(self: mitsuba.ChainTransform4d, v: mitsuba.Point3d) -> mitsuba.ChainTransform4d:
        """
        Create a translation transformation
        """
        ...

    def translation(self: mitsuba.Transform4d) -> mitsuba.Vector3d:
        """
        Get the translation part of a matrix
        """
        ...

    ...

class ChainTransform4f(Transform4f):
    """
    Encapsulates a 4x4 homogeneous coordinate transformation along with
    its inverse transpose
    
    The Transform class provides a set of overloaded matrix-vector
    multiplication operators for vectors, points, and normals (all of them
    behave differently under homogeneous coordinate transformations, hence
    the need to represent them using separate types)
    """

    inverse_transpose = ...
    matrix = ...

    def assign(self: mitsuba.Transform4f, arg0: mitsuba.Transform4f) -> None: ...
    def extract(self: mitsuba.Transform4f) -> mitsuba.Transform3f:
        """
        Extract a lower-dimensional submatrix
        """
        ...

    def from_frame(self: mitsuba.ChainTransform4f, frame: mitsuba.Frame3f) -> mitsuba.ChainTransform4f:
        """
        Creates a transformation that converts from 'frame' to the standard
        basis
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform4f) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform4f) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        """
        ...

    def inverse(self: mitsuba.Transform4f) -> mitsuba.Transform4f:
        """
        Compute the inverse of this transformation (involves just shuffles, no
        arithmetic)
        """
        ...

    def look_at(self: mitsuba.ChainTransform4f, origin: mitsuba.Point3f, target: mitsuba.Point3f, up: mitsuba.Point3f) -> mitsuba.ChainTransform4f:
        """
        Create a look-at camera transformation
        
        Parameter ``origin``:
            Camera position
        
        Parameter ``target``:
            Target vector
        
        Parameter ``up``:
            Up vector
        """
        ...

    def orthographic(self: mitsuba.ChainTransform4f, near: float, far: float) -> mitsuba.ChainTransform4f:
        """
        Create an orthographic transformation, which maps Z to [0,1] and
        leaves the X and Y coordinates untouched.
        
        Parameter ``near``:
            Near clipping plane
        
        Parameter ``far``:
            Far clipping plane
        """
        ...

    def perspective(self: mitsuba.ChainTransform4f, fov: float, near: float, far: float) -> mitsuba.ChainTransform4f:
        """
        Create a perspective transformation. (Maps [near, far] to [0, 1])
        
        Projects vectors in camera space onto a plane at z=1:
        
        x_proj = x / z y_proj = y / z z_proj = (far * (z - near)) / (z * (far-
        near))
        
        Camera-space depths are not mapped linearly!
        
        Parameter ``fov``:
            Field of view in degrees
        
        Parameter ``near``:
            Near clipping plane
        
        Parameter ``far``:
            Far clipping plane
        """
        ...

    def rotate(self: mitsuba.ChainTransform4f, axis: mitsuba.Point3f, angle: float) -> mitsuba.ChainTransform4f:
        """
        Create a rotation transformation around an arbitrary axis in 3D. The
        angle is specified in degrees
        """
        ...

    def scale(self: mitsuba.ChainTransform4f, v: mitsuba.Point3f) -> mitsuba.ChainTransform4f:
        """
        Create a scale transformation
        """
        ...

    def to_frame(self: mitsuba.ChainTransform4f, frame: mitsuba.Frame3f) -> mitsuba.ChainTransform4f:
        """
        Creates a transformation that converts from the standard basis to
        'frame'
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4f, p: mitsuba.Point3f) -> mitsuba.Point3f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4f, ray: mitsuba.Ray3f) -> mitsuba.Ray3f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4f, v: mitsuba.Vector3f) -> mitsuba.Vector3f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4f, n: mitsuba.Normal3f) -> mitsuba.Normal3f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        """
        ...

    def translate(self: mitsuba.ChainTransform4f, v: mitsuba.Point3f) -> mitsuba.ChainTransform4f:
        """
        Create a translation transformation
        """
        ...

    def translation(self: mitsuba.Transform4f) -> mitsuba.Vector3f:
        """
        Get the translation part of a matrix
        """
        ...

    ...

class Class:
    """
    Stores meta-information about Object instances.
    
    This class provides a thin layer of RTTI (run-time type information),
    which is useful for doing things like:
    
    * Checking if an object derives from a certain class
    
    * Determining the parent of a class at runtime
    
    * Instantiating a class by name
    
    * Unserializing a class from a binary data stream
    
    See also:
        ref, Object
    """

    def alias(self: mitsuba.Class) -> str:
        """
        Return the scene description-specific alias, if applicable
        """
        ...

    def name(self: mitsuba.Class) -> str:
        """
        Return the name of the class
        """
        ...

    def parent(self: mitsuba.Class) -> mitsuba.Class:
        """
        Return the Class object associated with the parent class of nullptr if
        it does not have one.
        """
        ...

    def variant(self: mitsuba.Class) -> str:
        """
        Return the variant of the class
        """
        ...

    ...

class Color0d:
    def __init__(self: mitsuba.Color0d, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Color0f:
    def __init__(self: mitsuba.Color0f, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Color1d:
    def __init__(self: mitsuba.Color1d, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Color1f:
    def __init__(self: mitsuba.Color1f, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Color3d:
    def __init__(self: mitsuba.Color3d, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Color3f:
    def __init__(self: mitsuba.Color3f, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Complex2f64:
    def __init__(self: mitsuba.Complex2f64, *args) -> None: ...
    imag = ...
    label = ...
    real = ...

    def assign(self, other): ...
    ...

class Complex2f:
    def __init__(self: mitsuba.Complex2f, *args) -> None: ...
    imag = ...
    label = ...
    real = ...

    def assign(self, other): ...
    ...

class ContinuousDistribution:
    """
    Continuous 1D probability distribution defined in terms of a regularly
    sampled linear interpolant
    
    This data structure represents a continuous 1D probability
    distribution that is defined as a linear interpolant of a regularly
    discretized signal. The class provides various routines for
    transforming uniformly distributed samples so that they follow the
    stored distribution. Note that unnormalized probability density
    functions (PDFs) will automatically be normalized during
    initialization. The associated scale factor can be retrieved using the
    function normalization().
    """

    @overload
    def __init__(self: mitsuba.ContinuousDistribution) -> None:
        """
        Continuous 1D probability distribution defined in terms of a regularly
        sampled linear interpolant
        
        This data structure represents a continuous 1D probability
        distribution that is defined as a linear interpolant of a regularly
        discretized signal. The class provides various routines for
        transforming uniformly distributed samples so that they follow the
        stored distribution. Note that unnormalized probability density
        functions (PDFs) will automatically be normalized during
        initialization. The associated scale factor can be retrieved using the
        function normalization().
        
        """
        ...

    @overload
    def __init__(self: mitsuba.ContinuousDistribution, arg0: mitsuba.ContinuousDistribution) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.ContinuousDistribution, range: mitsuba.Vector2f, pdf: mitsuba.ArrayXf) -> None:
        """
        Initialize from a given density function on the interval ``range``
        """
        ...

    def cdf(self: mitsuba.ContinuousDistribution) -> mitsuba.ArrayXf:
        """
        Return the unnormalized discrete cumulative distribution function over
        intervals
        """
        ...

    def empty(self: mitsuba.ContinuousDistribution) -> bool:
        """
        Is the distribution object empty/uninitialized?
        """
        ...

    def eval_cdf(self: mitsuba.ContinuousDistribution, x: float, active: bool = True) -> float:
        """
        Evaluate the unnormalized cumulative distribution function (CDF) at
        position ``p``
        """
        ...

    def eval_cdf_normalized(self: mitsuba.ContinuousDistribution, x: float, active: bool = True) -> float:
        """
        Evaluate the unnormalized cumulative distribution function (CDF) at
        position ``p``
        """
        ...

    def eval_pdf(self: mitsuba.ContinuousDistribution, x: float, active: bool = True) -> float:
        """
        Evaluate the unnormalized probability mass function (PDF) at position
        ``x``
        """
        ...

    def eval_pdf_normalized(self: mitsuba.ContinuousDistribution, x: float, active: bool = True) -> float:
        """
        Evaluate the normalized probability mass function (PDF) at position
        ``x``
        """
        ...

    def integral(self: mitsuba.ContinuousDistribution) -> float:
        """
        Return the original integral of PDF entries before normalization
        """
        ...

    def interval_resolution(self: mitsuba.ContinuousDistribution) -> float:
        """
        Return the minimum resolution of the discretization
        """
        ...

    def max(self: mitsuba.ContinuousDistribution) -> float: ...
    def normalization(self: mitsuba.ContinuousDistribution) -> float:
        """
        Return the normalization factor (i.e. the inverse of sum())
        """
        ...

    def pdf(self: mitsuba.ContinuousDistribution) -> mitsuba.ArrayXf:
        """
        Return the unnormalized discretized probability density function
        """
        ...

    def range(self: mitsuba.ContinuousDistribution) -> mitsuba.Vector2f:
        """
        Return the range of the distribution
        """
        ...

    def sample(self: mitsuba.ContinuousDistribution, value: float, active: bool = True) -> float:
        """
        %Transform a uniformly distributed sample to the stored distribution
        
        Parameter ``sample``:
            A uniformly distributed sample on the interval [0, 1].
        
        Returns:
            The sampled position.
        """
        ...

    def sample_pdf(self: mitsuba.ContinuousDistribution, value: float, active: bool = True) -> Tuple[float, float]:
        """
        %Transform a uniformly distributed sample to the stored distribution
        
        Parameter ``sample``:
            A uniformly distributed sample on the interval [0, 1].
        
        Returns:
            A tuple consisting of
        
        1. the sampled position. 2. the normalized probability density of the
        sample.
        """
        ...

    def size(self: mitsuba.ContinuousDistribution) -> int:
        """
        Return the number of discretizations
        """
        ...

    def update(self: mitsuba.ContinuousDistribution) -> None:
        """
        Update the internal state. Must be invoked when changing the pdf.
        """
        ...

    ...

class CppADIntegrator(SamplingIntegrator):
    def __init__(self: mitsuba.CppADIntegrator, arg0: mitsuba.Properties) -> None: ...
    hide_emitters = ...
    ptr = ...

    def aov_names(self: mitsuba.Integrator) -> List[str]:
        """
        For integrators that return one or more arbitrary output variables
        (AOVs), this function specifies a list of associated channel names.
        The default implementation simply returns an empty vector.
        """
        ...

    def cancel(self: mitsuba.Integrator) -> None:
        """
        Cancel a running render job (e.g. after receiving Ctrl-C)
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function renders the scene from the viewpoint of ``sensor``. All
        other parameters are optional and control different aspects of the
        rendering process. In particular:
        
        Parameter ``seed``:
            This parameter controls the initialization of the random number
            generator. It is crucial that you specify different seeds (e.g.,
            an increasing sequence) if subsequent ``render``() calls should
            produce statistically independent images.
        
        Parameter ``spp``:
            Set this parameter to a nonzero value to override the number of
            samples per pixel. This value then takes precedence over whatever
            was specified in the construction of ``sensor->sampler()``. This
            parameter may be useful in research applications where an image
            must be rendered multiple times using different quality levels.
        
        Parameter ``develop``:
            If set to ``True``, the implementation post-processes the data
            stored in ``sensor->film()``, returning the resulting image as a
            TensorXf. Otherwise, it returns an empty tensor.
        
        Parameter ``evaluate``:
            This parameter is only relevant for JIT variants of Mitsuba (LLVM,
            CUDA). If set to ``True``, the rendering step evaluates the
            generated image and waits for its completion. A log message also
            denotes the rendering time. Otherwise, the returned tensor
            (``develop=true``) or modified film (``develop=false``) represent
            the rendering task as an unevaluated computation graph.
        
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor: int = 0, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function is just a thin wrapper around the previous render()
        overload. It accepts a sensor *index* instead and renders the scene
        using sensor 0 by default.
        """
        ...

    @overload
    def render_backward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, grad_in: mitsuba.TensorXf, sensor, seed: int = 0, spp: int = 0) -> None: ...
    @overload
    def render_backward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, grad_in: mitsuba.TensorXf, sensor: int = 0, seed: int = 0, spp: int = 0) -> None: ...
    @overload
    def render_forward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, sensor, seed: int = 0, spp: int = 0) -> mitsuba.TensorXf: ...
    @overload
    def render_forward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, sensor: int = 0, seed: int = 0, spp: int = 0) -> mitsuba.TensorXf: ...
    def sample(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, sampler, ray: mitsuba.RayDifferential3f, medium: mitsuba.Medium = None, active: bool = True) -> Tuple[mitsuba.Color3f, bool, List[float]]:
        """
        Sample the incident radiance along a ray.
        
        Parameter ``scene``:
            The underlying scene in which the radiance function should be
            sampled
        
        Parameter ``sampler``:
            A source of (pseudo-/quasi-) random numbers
        
        Parameter ``ray``:
            A ray, optionally with differentials
        
        Parameter ``medium``:
            If the ray is inside a medium, this parameter holds a pointer to
            that medium
        
        Parameter ``aov``:
            Integrators may return one or more arbitrary output variables
            (AOVs) via this parameter. If ``nullptr`` is provided to this
            argument, no AOVs should be returned. Otherwise, the caller
            guarantees that space for at least ``aov_names().size()`` entries
            has been allocated.
        
        Parameter ``active``:
            A mask that indicates which SIMD lanes are active
        
        Returns:
            A pair containing a spectrum and a mask specifying whether a
            surface or medium interaction was sampled. False mask entries
            indicate that the ray "escaped" the scene, in which case the the
            returned spectrum contains the contribution of environment maps,
            if present. The mask can be used to estimate a suitable alpha
            channel of a rendered image.
        
        Remark:
            In the Python bindings, this function returns the ``aov`` output
            argument as an additional return value. In other words:
        
        ```
        (spec, mask, aov) = integrator.sample(scene, sampler, ray, medium, active)
        ```
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def should_stop(self: mitsuba.Integrator) -> bool:
        """
        Indicates whether cancel() or a timeout have occurred. Should be
        checked regularly in the integrator's main loop so that timeouts are
        enforced accurately.
        
        Note that accurate timeouts rely on m_render_timer, which needs to be
        reset at the beginning of the rendering phase.
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
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
class DefaultFormatter(Formatter):
    """
    The default formatter used to turn log messages into a human-readable
    form
    """

    def __init__(self: mitsuba.DefaultFormatter) -> None: ...
    ptr = ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def format(self: mitsuba.Formatter, level: mitsuba.LogLevel, class_: mitsuba.Class, thread, file: str, line: int, msg: str) -> str:
        """
        Turn a log message into a human-readable format
        
        Parameter ``level``:
            The importance of the debug message
        
        Parameter ``class_``:
            Originating class or ``nullptr``
        
        Parameter ``thread``:
            Thread, which is responsible for creating the message
        
        Parameter ``file``:
            File, which is responsible for creating the message
        
        Parameter ``line``:
            Associated line within the source file
        
        Parameter ``msg``:
            Text content associated with the log message
        """
        ...

    def has_class(self: mitsuba.DefaultFormatter) -> bool:
        """
        See also:
            set_has_class
        """
        ...

    def has_date(self: mitsuba.DefaultFormatter) -> bool:
        """
        See also:
            set_has_date
        """
        ...

    def has_log_level(self: mitsuba.DefaultFormatter) -> bool:
        """
        See also:
            set_has_log_level
        """
        ...

    def has_thread(self: mitsuba.DefaultFormatter) -> bool:
        """
        See also:
            set_has_thread
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_has_class(self: mitsuba.DefaultFormatter, arg0: bool) -> None:
        """
        Should class information be included? The default is yes.
        """
        ...

    def set_has_date(self: mitsuba.DefaultFormatter, arg0: bool) -> None:
        """
        Should date information be included? The default is yes.
        """
        ...

    def set_has_log_level(self: mitsuba.DefaultFormatter, arg0: bool) -> None:
        """
        Should log level information be included? The default is yes.
        """
        ...

    def set_has_thread(self: mitsuba.DefaultFormatter, arg0: bool) -> None:
        """
        Should thread information be included? The default is yes.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class DirectionSample3f(PositionSample3f):
    """
    Record for solid-angle based area sampling techniques
    
    This data structure is used in techniques that sample positions
    relative to a fixed reference position in the scene. For instance,
    *direct illumination strategies* importance sample the incident
    radiance received by a given surface location. Mitsuba uses this
    approach in a wider bidirectional sense: sampling the incident
    importance due to a sensor also uses the same data structures and
    strategies, which are referred to as *direct sampling*.
    
    This record inherits all fields from PositionSample and extends it
    with two useful quantities that are cached so that they don't need to
    be recomputed: the unit direction and distance from the reference
    position to the sampled point.
    """

    @overload
    def __init__(self: mitsuba.DirectionSample3f) -> None:
        """
        Construct an uninitialized direct sample
        
        """
        ...

    @overload
    def __init__(self: mitsuba.DirectionSample3f, other: mitsuba.PositionSample3f) -> None:
        """
        Construct from a position sample
        
        """
        ...

    @overload
    def __init__(self: mitsuba.DirectionSample3f, other: mitsuba.DirectionSample3f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.DirectionSample3f, p: mitsuba.Point3f, n: mitsuba.Normal3f, uv: mitsuba.Point2f, time: float, pdf: float, delta: bool, d: mitsuba.Vector3f, dist: float, emitter: mitsuba.Emitter) -> None:
        """
        Element-by-element constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.DirectionSample3f, scene: mitsuba.Scene, si: mitsuba.SurfaceInteraction3f, ref: mitsuba.Interaction3f) -> None:
        """
        Create a position sampling record from a surface intersection
        
        This is useful to determine the hypothetical sampling density on a
        surface after hitting it using standard ray tracing. This happens for
        instance in path tracing with multiple importance sampling.
        """
        ...

    d = ...
    "Unit direction from the reference point to the target shape"
    delta = ...
    """
    Set if the sample was drawn from a degenerate (Dirac delta)
    distribution
    """
    dist = ...
    "Distance from the reference point to the target shape"
    emitter = ...
    """
    Optional: pointer to an associated object
    
    In some uses of this record, sampling a position also involves
    choosing one of several objects (shapes, emitters, ..) on which the
    position lies. In that case, the ``object`` attribute stores a pointer
    to this object.
    """
    n = ...
    "Sampled surface normal (if applicable)"
    p = ...
    "Sampled position"
    pdf = ...
    "Probability density at the sample"
    time = ...
    "Associated time value"
    uv = ...
    """
    Optional: 2D sample position associated with the record
    
    In some uses of this record, a sampled position may be associated with
    an important 2D quantity, such as the texture coordinates on a
    triangle mesh or a position on the aperture of a sensor. When
    applicable, such positions are stored in the ``uv`` attribute.
    """

    def assign(self: mitsuba.DirectionSample3f, arg0: mitsuba.DirectionSample3f) -> None: ...
    ...

class DiscontinuityFlags:
    """
    This list of flags is used to control the behavior of discontinuity
    related routines.
    
    Members:
    
      Empty : No flags set (default value)
    
      PerimeterType : Open boundary or jumping normal type of discontinuity
    
      InteriorType : Smooth normal type of discontinuity
    
      DirectionLune : //! Encoding and projection flags
    
      DirectionSphere : //! Encoding and projection flags
    
      HeuristicWalk : //! Encoding and projection flags
    
      AllTypes : All types of discontinuities
    """

    def __init__(self: mitsuba.DiscontinuityFlags, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    AllTypes = 3
    """
      AllTypes : All types of discontinuities
    """
    DirectionLune = 4
    """
      DirectionLune : //! Encoding and projection flags
    """
    DirectionSphere = 8
    """
      DirectionSphere : //! Encoding and projection flags
    """
    Empty = 0
    """
      Empty : No flags set (default value)
    """
    HeuristicWalk = 16
    """
      HeuristicWalk : //! Encoding and projection flags
    """
    InteriorType = 2
    """
      InteriorType : Smooth normal type of discontinuity
    """
    PerimeterType = 1
    """
      PerimeterType : Open boundary or jumping normal type of discontinuity
    """

    ...

class DiscreteDistribution:
    """
    Discrete 1D probability distribution
    
    This data structure represents a discrete 1D probability distribution
    and provides various routines for transforming uniformly distributed
    samples so that they follow the stored distribution. Note that
    unnormalized probability mass functions (PMFs) will automatically be
    normalized during initialization. The associated scale factor can be
    retrieved using the function normalization().
    """

    @overload
    def __init__(self: mitsuba.DiscreteDistribution) -> None:
        """
        Discrete 1D probability distribution
        
        This data structure represents a discrete 1D probability distribution
        and provides various routines for transforming uniformly distributed
        samples so that they follow the stored distribution. Note that
        unnormalized probability mass functions (PMFs) will automatically be
        normalized during initialization. The associated scale factor can be
        retrieved using the function normalization().
        
        """
        ...

    @overload
    def __init__(self: mitsuba.DiscreteDistribution, arg0: mitsuba.DiscreteDistribution) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.DiscreteDistribution, pmf: mitsuba.ArrayXf) -> None:
        """
        Initialize from a given probability mass function
        """
        ...

    def cdf(self: mitsuba.DiscreteDistribution) -> mitsuba.ArrayXf:
        """
        Return the unnormalized cumulative distribution function
        """
        ...

    def empty(self: mitsuba.DiscreteDistribution) -> bool:
        """
        Is the distribution object empty/uninitialized?
        """
        ...

    def eval_cdf(self: mitsuba.DiscreteDistribution, index: int, active: bool = True) -> float:
        """
        Evaluate the unnormalized cumulative distribution function (CDF) at
        index ``index``
        """
        ...

    def eval_cdf_normalized(self: mitsuba.DiscreteDistribution, index: int, active: bool = True) -> float:
        """
        Evaluate the normalized cumulative distribution function (CDF) at
        index ``index``
        """
        ...

    def eval_pmf(self: mitsuba.DiscreteDistribution, index: int, active: bool = True) -> float:
        """
        Evaluate the unnormalized probability mass function (PMF) at index
        ``index``
        """
        ...

    def eval_pmf_normalized(self: mitsuba.DiscreteDistribution, index: int, active: bool = True) -> float:
        """
        Evaluate the normalized probability mass function (PMF) at index
        ``index``
        """
        ...

    def normalization(self: mitsuba.DiscreteDistribution) -> float:
        """
        Return the normalization factor (i.e. the inverse of sum())
        """
        ...

    def pmf(self: mitsuba.DiscreteDistribution) -> mitsuba.ArrayXf:
        """
        Return the unnormalized probability mass function
        """
        ...

    def sample(self: mitsuba.DiscreteDistribution, value: float, active: bool = True) -> int:
        """
        %Transform a uniformly distributed sample to the stored distribution
        
        Parameter ``sample``:
            A uniformly distributed sample on the interval [0, 1].
        
        Returns:
            The discrete index associated with the sample
        """
        ...

    def sample_pmf(self: mitsuba.DiscreteDistribution, value: float, active: bool = True) -> Tuple[int, float]:
        """
        %Transform a uniformly distributed sample to the stored distribution
        
        Parameter ``value``:
            A uniformly distributed sample on the interval [0, 1].
        
        Returns:
            A tuple consisting of
        
        1. the discrete index associated with the sample, and 2. the
        normalized probability value of the sample.
        """
        ...

    def sample_reuse(self: mitsuba.DiscreteDistribution, value: float, active: bool = True) -> Tuple[int, float]:
        """
        %Transform a uniformly distributed sample to the stored distribution
        
        The original sample is value adjusted so that it can be reused as a
        uniform variate.
        
        Parameter ``value``:
            A uniformly distributed sample on the interval [0, 1].
        
        Returns:
            A tuple consisting of
        
        1. the discrete index associated with the sample, and 2. the re-scaled
        sample value.
        """
        ...

    def sample_reuse_pmf(self: mitsuba.DiscreteDistribution, value: float, active: bool = True) -> Tuple[int, float, float]:
        """
        %Transform a uniformly distributed sample to the stored distribution.
        
        The original sample is value adjusted so that it can be reused as a
        uniform variate.
        
        Parameter ``value``:
            A uniformly distributed sample on the interval [0, 1].
        
        Returns:
            A tuple consisting of
        
        1. the discrete index associated with the sample 2. the re-scaled
        sample value 3. the normalized probability value of the sample
        """
        ...

    def size(self: mitsuba.DiscreteDistribution) -> int:
        """
        Return the number of entries
        """
        ...

    def sum(self: mitsuba.DiscreteDistribution) -> float:
        """
        Return the original sum of PMF entries before normalization
        """
        ...

    def update(self: mitsuba.DiscreteDistribution) -> None:
        """
        Update the internal state. Must be invoked when changing the pmf.
        """
        ...

    ...

class DiscreteDistribution2D:
    def __init__(self: mitsuba.DiscreteDistribution2D, data: numpy.ndarray[numpy.float32]) -> None: ...
    def eval(self: mitsuba.DiscreteDistribution2D, pos: mitsuba.Point2u, active: bool = True) -> float: ...
    def pdf(self: mitsuba.DiscreteDistribution2D, pos: mitsuba.Point2u, active: bool = True) -> float: ...
    def sample(self: mitsuba.DiscreteDistribution2D, sample: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.Point2u, float, mitsuba.Point2f]: ...
    ...

class DummyStream(Stream):
    """
    Stream implementation that never writes to disk, but keeps track of
    the size of the content being written. It can be used, for example, to
    measure the precise amount of memory needed to store serialized
    content.
    """

    def __init__(self: mitsuba.DummyStream) -> None: ...
    class EByteOrder:
        """
        Defines the byte order (endianness) to use in this Stream
        
        Members:
        
          EBigEndian : 
        
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        
          ENetworkByteOrder : x86, x86_64
        """

        def __init__(self: mitsuba.Stream.EByteOrder, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        EBigEndian = 0
        """
          EBigEndian : 
        """
        ELittleEndian = 1
        """
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        """

        ...

    ptr = ...

    EBigEndian = 0
    """
      EBigEndian : 
    """
    ELittleEndian = 1
    """
      ELittleEndian : PowerPC, SPARC, Motorola 68K
    """

    def byte_order(self: mitsuba.Stream) -> mitsuba.Stream.EByteOrder:
        """
        Returns the byte order of this stream.
        """
        ...

    def can_read(self: mitsuba.Stream) -> bool:
        """
        Can we read from the stream?
        """
        ...

    def can_write(self: mitsuba.Stream) -> bool:
        """
        Can we write to the stream?
        """
        ...

    def close(self: mitsuba.Stream) -> None:
        """
        Closes the stream.
        
        No further read or write operations are permitted.
        
        This function is idempotent. It may be called automatically by the
        destructor.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def flush(self: mitsuba.Stream) -> None:
        """
        Flushes the stream's buffers, if any
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def read(self: mitsuba.Stream, arg0: int) -> bytes:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def read_bool(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_double(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_float(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_line(self: mitsuba.Stream) -> str:
        """
        Convenience function for reading a line of text from an ASCII file
        """
        ...

    def read_single(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_string(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def seek(self: mitsuba.Stream, arg0: int) -> None:
        """
        Seeks to a position inside the stream.
        
        Seeking beyond the size of the buffer will not modify the length of
        its contents. However, a subsequent write should start at the sought
        position and update the size appropriately.
        """
        ...

    def set_byte_order(self: mitsuba.Stream, arg0: mitsuba.Stream.EByteOrder) -> None:
        """
        Sets the byte order to use in this stream.
        
        Automatic conversion will be performed on read and write operations to
        match the system's native endianness.
        
        No consistency is guaranteed if this method is called after performing
        some read and write operations on the system using a different
        endianness.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def size(self: mitsuba.Stream) -> int:
        """
        Returns the size of the stream
        """
        ...

    def skip(self: mitsuba.Stream, arg0: int) -> None:
        """
        Skip ahead by a given number of bytes
        """
        ...

    def tell(self: mitsuba.Stream) -> int:
        """
        Gets the current position inside the stream
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def truncate(self: mitsuba.Stream, arg0: int) -> None:
        """
        Truncates the stream to a given size.
        
        The position is updated to ``min(old_position, size)``. Throws an
        exception if in read-only mode.
        """
        ...

    def write(self: mitsuba.Stream, arg0: bytes) -> None:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def write_bool(self: mitsuba.Stream, arg0: bool) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_double(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_float(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_line(self: mitsuba.Stream, arg0: str) -> None:
        """
        Convenience function for writing a line of text to an ASCII file
        """
        ...

    def write_single(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_string(self: mitsuba.Stream, arg0: str) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    ...

class Emitter(Endpoint):
    def __init__(self: mitsuba.Emitter, arg0: mitsuba.Properties) -> None: ...
    m_flags = ...
    m_needs_sample_2 = ...
    m_needs_sample_3 = ...
    ptr = ...

    def bbox(self: mitsuba.Endpoint) -> mitsuba.BoundingBox3f:
        """
        Return an axis-aligned box bounding the spatial extents of the emitter
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.Endpoint, si, active: bool = True) -> mitsuba.Color3f:
        """
        Given a ray-surface intersection, return the emitted radiance or
        importance traveling along the reverse direction
        
        This function is e.g. used when an area light source has been hit by a
        ray in a path tracing-style integrator, and it subsequently needs to
        be queried for the emitted radiance along the negative ray direction.
        The default implementation throws an exception, which states that the
        method is not implemented.
        
        Parameter ``si``:
            An intersect record that specifies both the query position and
            direction (using the ``si.wi`` field)
        
        Returns:
            The emitted radiance or importance
        """
        ...

    def eval_direction(self: mitsuba.Endpoint, it, ds, active: bool = True) -> mitsuba.Color3f:
        """
        Re-evaluate the incident direct radiance/importance of the
        sample_direction() method.
        
        This function re-evaluates the incident direct radiance or importance
        and sample probability due to the endpoint so that division by
        ``ds.pdf`` equals the sampling weight returned by sample_direction().
        This may appear redundant, and indeed such a function would not find
        use in "normal" rendering algorithms.
        
        However, the ability to re-evaluate the contribution of a generated
        sample is important for differentiable rendering. For example, we
        might want to track derivatives in the sampled direction (``ds.d``)
        without also differentiating the sampling technique.
        
        In contrast to pdf_direction(), evaluating this function can yield a
        nonzero result in the case of emission profiles containing a Dirac
        delta term (e.g. point or directional lights).
        
        Parameter ``ref``:
            A 3D reference location within the scene, which may influence the
            sampling process.
        
        Parameter ``ds``:
            A direction sampling record, which specifies the query location.
        
        Returns:
            The incident direct radiance/importance associated with the
            sample.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def flags(self: mitsuba.Emitter, active: bool = True) -> int:
        """
        Flags for all components combined.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def is_environment(self: mitsuba.Emitter) -> bool:
        """
        Is this an environment map light emitter?
        """
        ...

    def medium(self: mitsuba.Endpoint) -> mitsuba.Medium:
        """
        Return a pointer to the medium that surrounds the emitter
        """
        ...

    def needs_sample_2(self: mitsuba.Endpoint) -> bool:
        """
        Does the method sample_ray() require a uniformly distributed 2D sample
        for the ``sample2`` parameter?
        """
        ...

    def needs_sample_3(self: mitsuba.Endpoint) -> bool:
        """
        Does the method sample_ray() require a uniformly distributed 2D sample
        for the ``sample3`` parameter?
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def pdf_direction(self: mitsuba.Endpoint, it, ds, active: bool = True) -> float:
        """
        Evaluate the probability density of the *direct* sampling method
        implemented by the sample_direction() method.
        
        The returned probability will always be zero when the
        emission/sensitivity profile contains a Dirac delta term (e.g. point
        or directional emitters/sensors).
        
        Parameter ``ds``:
            A direct sampling record, which specifies the query location.
        """
        ...

    def pdf_position(self: mitsuba.Endpoint, ps, active: bool = True) -> float:
        """
        Evaluate the probability density of the position sampling method
        implemented by sample_position().
        
        In simple cases, this will be the reciprocal of the endpoint's surface
        area.
        
        Parameter ``ps``:
            The sampled position record.
        
        Returns:
            The corresponding sampling density.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_direction(self: mitsuba.Endpoint, it, sample: mitsuba.Point2f, active: bool = True):
        """
        Given a reference point in the scene, sample a direction from the
        reference point towards the endpoint (ideally proportional to the
        emission/sensitivity profile)
        
        This operation is a generalization of direct illumination techniques
        to both emitters *and* sensors. A direction sampling method is given
        an arbitrary reference position in the scene and samples a direction
        from the reference point towards the endpoint (ideally proportional to
        the emission/sensitivity profile). This reduces the sampling domain
        from 4D to 2D, which often enables the construction of smarter
        specialized sampling techniques.
        
        Ideally, the implementation should importance sample the product of
        the emission profile and the geometry term between the reference point
        and the position on the endpoint.
        
        The default implementation throws an exception.
        
        Parameter ``ref``:
            A reference position somewhere within the scene.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``.
        
        Returns:
            A DirectionSample instance describing the generated sample along
            with a spectral importance weight.
        """
        ...

    def sample_position(self: mitsuba.Endpoint, ref: float, ds: mitsuba.Point2f, active: bool = True):
        """
        Importance sample the spatial component of the emission or importance
        profile of the endpoint.
        
        The default implementation throws an exception.
        
        Parameter ``time``:
            The scene time associated with the position to be sampled.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``.
        
        Returns:
            A PositionSample instance describing the generated sample along
            with an importance weight.
        """
        ...

    def sample_ray(self: mitsuba.Endpoint, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.Ray3f, mitsuba.Color3f]:
        """
        Importance sample a ray proportional to the endpoint's
        sensitivity/emission profile.
        
        The endpoint profile is a six-dimensional quantity that depends on
        time, wavelength, surface position, and direction. This function takes
        a given time value and five uniformly distributed samples on the
        interval [0, 1] and warps them so that the returned ray follows the
        profile. Any discrepancies between ideal and actual sampled profile
        are absorbed into a spectral importance weight that is returned along
        with the ray.
        
        Parameter ``time``:
            The scene time associated with the ray to be sampled
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the emission profile.
        
        Parameter ``sample2``:
            A uniformly distributed sample on the domain ``[0,1]^2``. For
            sensor endpoints, this argument corresponds to the sample position
            in fractional pixel coordinates relative to the crop window of the
            underlying film. This argument is ignored if ``needs_sample_2() ==
            false``.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``. For
            sensor endpoints, this argument determines the position on the
            aperture of the sensor. This argument is ignored if
            ``needs_sample_3() == false``.
        
        Returns:
            The sampled ray and (potentially spectrally varying) importance
            weights. The latter account for the difference between the profile
            and the actual used sampling density function.
        """
        ...

    def sample_wavelengths(self: mitsuba.Endpoint, si, sample: float, active: bool = True) -> Tuple[mitsuba.Color0f, mitsuba.Color3f]:
        """
        Importance sample a set of wavelengths according to the endpoint's
        sensitivity/emission spectrum.
        
        This function takes a uniformly distributed 1D sample and generates a
        sample that is approximately distributed according to the endpoint's
        spectral sensitivity/emission profile.
        
        For this, the input 1D sample is first replicated into
        ``Spectrum::Size`` separate samples using simple arithmetic
        transformations (see math::sample_shifted()), which can be interpreted
        as a type of Quasi-Monte-Carlo integration scheme. Following this, a
        standard technique (e.g. inverse transform sampling) is used to find
        the corresponding wavelengths. Any discrepancies between ideal and
        actual sampled profile are absorbed into a spectral importance weight
        that is returned along with the wavelengths.
        
        This function should not be called in RGB or monochromatic modes.
        
        Parameter ``si``:
            In the case of a spatially-varying spectral sensitivity/emission
            profile, this parameter conditions sampling on a specific spatial
            position. The ``si.uv`` field must be specified in this case.
        
        Parameter ``sample``:
            A 1D uniformly distributed random variate
        
        Returns:
            The set of sampled wavelengths and (potentially spectrally
            varying) importance weights. The latter account for the difference
            between the profile and the actual used sampling density function.
            In the case of emitters, the weight will include the emitted
            radiance.
        """
        ...

    def sampling_weight(self: mitsuba.Emitter) -> float:
        """
        The emitter's sampling weight.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_medium(self: mitsuba.Endpoint, medium: mitsuba.Medium) -> None:
        """
        Set the medium that surrounds the emitter.
        """
        ...

    def set_scene(self: mitsuba.Endpoint, scene: mitsuba.Scene) -> None:
        """
        Inform the emitter about the properties of the scene
        
        Various emitters that surround the scene (e.g. environment emitters)
        must be informed about the scene dimensions to operate correctly. This
        function is invoked by the Scene constructor.
        """
        ...

    def set_shape(self: mitsuba.Endpoint, shape: mitsuba.Shape) -> None:
        """
        Set the shape associated with this endpoint.
        """
        ...

    def shape(self: mitsuba.Endpoint) -> mitsuba.Shape:
        """
        Return the shape, to which the emitter is currently attached
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def world_transform(self: mitsuba.Endpoint) -> mitsuba.Transform4f:
        """
        Return the local space to world space transformation
        """
        ...

    ...

class EmitterFlags:
    """
    This list of flags is used to classify the different types of
    emitters.
    
    Members:
    
      Empty : No flags set (default value)
    
      DeltaPosition : The emitter lies at a single point in space
    
      DeltaDirection : The emitter emits light in a single direction
    
      Infinite : The emitter is placed at infinity (e.g. environment maps)
    
      Surface : The emitter is attached to a surface (e.g. area emitters)
    
      SpatiallyVarying : The emission depends on the UV coordinates
    
      Delta : Delta function in either position or direction
    """

    def __init__(self: mitsuba.EmitterFlags, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Delta = 3
    """
      DeltaPosition : The emitter lies at a single point in space
      DeltaDirection : The emitter emits light in a single direction
      Delta : Delta function in either position or direction
    """
    DeltaDirection = 2
    """
      DeltaDirection : The emitter emits light in a single direction
    """
    DeltaPosition = 1
    """
      DeltaPosition : The emitter lies at a single point in space
    """
    Empty = 0
    """
      Empty : No flags set (default value)
    """
    Infinite = 4
    """
      Infinite : The emitter is placed at infinity (e.g. environment maps)
    """
    SpatiallyVarying = 16
    """
      SpatiallyVarying : The emission depends on the UV coordinates
    """
    Surface = 8
    """
      Surface : The emitter is attached to a surface (e.g. area emitters)
    """

    ...

class Endpoint(Object):
    """
    Abstract interface subsuming emitters and sensors in Mitsuba.
    
    This class provides an abstract interface to emitters and sensors in
    Mitsuba, which are named *endpoints* since they represent the first
    and last vertices of a light path. Thanks to symmetries underlying the
    equations of light transport and scattering, sensors and emitters can
    be treated as essentially the same thing, their main difference being
    type of emitted radiation: light sources emit *radiance*, while
    sensors emit a conceptual radiation named *importance*. This class
    casts these symmetries into a unified API that enables access to both
    types of endpoints using the same set of functions.
    
    Subclasses of this interface must implement functions to evaluate and
    sample the emission/response profile, and to compute probability
    densities associated with the provided sampling techniques.
    
    In addition to :py:meth:`mitsuba.Endpoint.sample_ray`, which generates
    a sample from the profile, subclasses also provide a specialized
    *direction sampling* method in
    :py:meth:`mitsuba.Endpoint.sample_direction`. This is a generalization
    of direct illumination techniques to both emitters *and* sensors. A
    direction sampling method is given an arbitrary reference position in
    the scene and samples a direction from the reference point towards the
    endpoint (ideally proportional to the emission/sensitivity profile).
    This reduces the sampling domain from 4D to 2D, which often enables
    the construction of smarter specialized sampling techniques.
    
    When rendering scenes involving participating media, it is important
    to know what medium surrounds the sensors and emitters. For this
    reason, every endpoint instance keeps a reference to a medium (which
    may be set to ``nullptr`` when the endpoint is surrounded by vacuum).
    
    In the context of polarized simulation, the perfect symmetry between
    emitters and sensors technically breaks down: the former emit 4D
    *Stokes vectors* encoding the polarization state of light, while
    sensors are characterized by 4x4 *Mueller matrices* that transform the
    incident polarization prior to measurement. We sidestep this non-
    symmetry by simply using Mueller matrices everywhere: in the case of
    emitters, only the first column will be used (the remainder being
    filled with zeros). This API simplification comes at a small extra
    cost in terms of register usage and arithmetic. The JIT (LLVM, CUDA)
    variants of Mitsuba can recognize these redundancies and remove them
    retroactively.
    """

    ptr = ...

    def bbox(self: mitsuba.Endpoint) -> mitsuba.BoundingBox3f:
        """
        Return an axis-aligned box bounding the spatial extents of the emitter
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.Endpoint, si, active: bool = True) -> mitsuba.Color3f:
        """
        Given a ray-surface intersection, return the emitted radiance or
        importance traveling along the reverse direction
        
        This function is e.g. used when an area light source has been hit by a
        ray in a path tracing-style integrator, and it subsequently needs to
        be queried for the emitted radiance along the negative ray direction.
        The default implementation throws an exception, which states that the
        method is not implemented.
        
        Parameter ``si``:
            An intersect record that specifies both the query position and
            direction (using the ``si.wi`` field)
        
        Returns:
            The emitted radiance or importance
        """
        ...

    def eval_direction(self: mitsuba.Endpoint, it, ds, active: bool = True) -> mitsuba.Color3f:
        """
        Re-evaluate the incident direct radiance/importance of the
        sample_direction() method.
        
        This function re-evaluates the incident direct radiance or importance
        and sample probability due to the endpoint so that division by
        ``ds.pdf`` equals the sampling weight returned by sample_direction().
        This may appear redundant, and indeed such a function would not find
        use in "normal" rendering algorithms.
        
        However, the ability to re-evaluate the contribution of a generated
        sample is important for differentiable rendering. For example, we
        might want to track derivatives in the sampled direction (``ds.d``)
        without also differentiating the sampling technique.
        
        In contrast to pdf_direction(), evaluating this function can yield a
        nonzero result in the case of emission profiles containing a Dirac
        delta term (e.g. point or directional lights).
        
        Parameter ``ref``:
            A 3D reference location within the scene, which may influence the
            sampling process.
        
        Parameter ``ds``:
            A direction sampling record, which specifies the query location.
        
        Returns:
            The incident direct radiance/importance associated with the
            sample.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def medium(self: mitsuba.Endpoint) -> mitsuba.Medium:
        """
        Return a pointer to the medium that surrounds the emitter
        """
        ...

    def needs_sample_2(self: mitsuba.Endpoint) -> bool:
        """
        Does the method sample_ray() require a uniformly distributed 2D sample
        for the ``sample2`` parameter?
        """
        ...

    def needs_sample_3(self: mitsuba.Endpoint) -> bool:
        """
        Does the method sample_ray() require a uniformly distributed 2D sample
        for the ``sample3`` parameter?
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def pdf_direction(self: mitsuba.Endpoint, it, ds, active: bool = True) -> float:
        """
        Evaluate the probability density of the *direct* sampling method
        implemented by the sample_direction() method.
        
        The returned probability will always be zero when the
        emission/sensitivity profile contains a Dirac delta term (e.g. point
        or directional emitters/sensors).
        
        Parameter ``ds``:
            A direct sampling record, which specifies the query location.
        """
        ...

    def pdf_position(self: mitsuba.Endpoint, ps, active: bool = True) -> float:
        """
        Evaluate the probability density of the position sampling method
        implemented by sample_position().
        
        In simple cases, this will be the reciprocal of the endpoint's surface
        area.
        
        Parameter ``ps``:
            The sampled position record.
        
        Returns:
            The corresponding sampling density.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_direction(self: mitsuba.Endpoint, it, sample: mitsuba.Point2f, active: bool = True):
        """
        Given a reference point in the scene, sample a direction from the
        reference point towards the endpoint (ideally proportional to the
        emission/sensitivity profile)
        
        This operation is a generalization of direct illumination techniques
        to both emitters *and* sensors. A direction sampling method is given
        an arbitrary reference position in the scene and samples a direction
        from the reference point towards the endpoint (ideally proportional to
        the emission/sensitivity profile). This reduces the sampling domain
        from 4D to 2D, which often enables the construction of smarter
        specialized sampling techniques.
        
        Ideally, the implementation should importance sample the product of
        the emission profile and the geometry term between the reference point
        and the position on the endpoint.
        
        The default implementation throws an exception.
        
        Parameter ``ref``:
            A reference position somewhere within the scene.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``.
        
        Returns:
            A DirectionSample instance describing the generated sample along
            with a spectral importance weight.
        """
        ...

    def sample_position(self: mitsuba.Endpoint, ref: float, ds: mitsuba.Point2f, active: bool = True):
        """
        Importance sample the spatial component of the emission or importance
        profile of the endpoint.
        
        The default implementation throws an exception.
        
        Parameter ``time``:
            The scene time associated with the position to be sampled.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``.
        
        Returns:
            A PositionSample instance describing the generated sample along
            with an importance weight.
        """
        ...

    def sample_ray(self: mitsuba.Endpoint, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.Ray3f, mitsuba.Color3f]:
        """
        Importance sample a ray proportional to the endpoint's
        sensitivity/emission profile.
        
        The endpoint profile is a six-dimensional quantity that depends on
        time, wavelength, surface position, and direction. This function takes
        a given time value and five uniformly distributed samples on the
        interval [0, 1] and warps them so that the returned ray follows the
        profile. Any discrepancies between ideal and actual sampled profile
        are absorbed into a spectral importance weight that is returned along
        with the ray.
        
        Parameter ``time``:
            The scene time associated with the ray to be sampled
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the emission profile.
        
        Parameter ``sample2``:
            A uniformly distributed sample on the domain ``[0,1]^2``. For
            sensor endpoints, this argument corresponds to the sample position
            in fractional pixel coordinates relative to the crop window of the
            underlying film. This argument is ignored if ``needs_sample_2() ==
            false``.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``. For
            sensor endpoints, this argument determines the position on the
            aperture of the sensor. This argument is ignored if
            ``needs_sample_3() == false``.
        
        Returns:
            The sampled ray and (potentially spectrally varying) importance
            weights. The latter account for the difference between the profile
            and the actual used sampling density function.
        """
        ...

    def sample_wavelengths(self: mitsuba.Endpoint, si, sample: float, active: bool = True) -> Tuple[mitsuba.Color0f, mitsuba.Color3f]:
        """
        Importance sample a set of wavelengths according to the endpoint's
        sensitivity/emission spectrum.
        
        This function takes a uniformly distributed 1D sample and generates a
        sample that is approximately distributed according to the endpoint's
        spectral sensitivity/emission profile.
        
        For this, the input 1D sample is first replicated into
        ``Spectrum::Size`` separate samples using simple arithmetic
        transformations (see math::sample_shifted()), which can be interpreted
        as a type of Quasi-Monte-Carlo integration scheme. Following this, a
        standard technique (e.g. inverse transform sampling) is used to find
        the corresponding wavelengths. Any discrepancies between ideal and
        actual sampled profile are absorbed into a spectral importance weight
        that is returned along with the wavelengths.
        
        This function should not be called in RGB or monochromatic modes.
        
        Parameter ``si``:
            In the case of a spatially-varying spectral sensitivity/emission
            profile, this parameter conditions sampling on a specific spatial
            position. The ``si.uv`` field must be specified in this case.
        
        Parameter ``sample``:
            A 1D uniformly distributed random variate
        
        Returns:
            The set of sampled wavelengths and (potentially spectrally
            varying) importance weights. The latter account for the difference
            between the profile and the actual used sampling density function.
            In the case of emitters, the weight will include the emitted
            radiance.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_medium(self: mitsuba.Endpoint, medium: mitsuba.Medium) -> None:
        """
        Set the medium that surrounds the emitter.
        """
        ...

    def set_scene(self: mitsuba.Endpoint, scene: mitsuba.Scene) -> None:
        """
        Inform the emitter about the properties of the scene
        
        Various emitters that surround the scene (e.g. environment emitters)
        must be informed about the scene dimensions to operate correctly. This
        function is invoked by the Scene constructor.
        """
        ...

    def set_shape(self: mitsuba.Endpoint, shape: mitsuba.Shape) -> None:
        """
        Set the shape associated with this endpoint.
        """
        ...

    def shape(self: mitsuba.Endpoint) -> mitsuba.Shape:
        """
        Return the shape, to which the emitter is currently attached
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def world_transform(self: mitsuba.Endpoint) -> mitsuba.Transform4f:
        """
        Return the local space to world space transformation
        """
        ...

    ...

class FileResolver(Object):
    """
    Simple class for resolving paths on Linux/Windows/Mac OS
    
    This convenience class looks for a file or directory given its name
    and a set of search paths. The implementation walks through the search
    paths in order and stops once the file is found.
    """

    @overload
    def __init__(self: mitsuba.FileResolver) -> None:
        """
        Initialize a new file resolver with the current working directory
        
        """
        ...

    @overload
    def __init__(self: mitsuba.FileResolver, arg0: mitsuba.FileResolver) -> None:
        """
        Copy constructor
        """
        ...

    ptr = ...

    def append(self: mitsuba.FileResolver, arg0: mitsuba.filesystem.path) -> None:
        """
        Append an entry to the end of the list of search paths
        """
        ...

    def clear(self: mitsuba.FileResolver) -> None:
        """
        Clear the list of search paths
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def prepend(self: mitsuba.FileResolver, arg0: mitsuba.filesystem.path) -> None:
        """
        Prepend an entry at the beginning of the list of search paths
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def resolve(self: mitsuba.FileResolver, arg0: mitsuba.filesystem.path) -> mitsuba.filesystem.path:
        """
        Walk through the list of search paths and try to resolve the input
        path
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class FileStream(Stream):
    """
    Simple Stream implementation backed-up by a file.
    
    The underlying file abstraction is ``std::fstream``, and so most
    operations can be expected to behave similarly.
    """

    def __init__(self: mitsuba.FileStream, p: mitsuba.filesystem.path, mode: mitsuba.FileStream.EMode = EMode.ERead) -> None:
        """
        Constructs a new FileStream by opening the file pointed by ``p``.
        
        The file is opened in read-only or read/write mode as specified by
        ``mode``.
        
        Throws if trying to open a non-existing file in with write disabled.
        Throws an exception if the file cannot be opened / created.
        """
        ...

    class EByteOrder:
        """
        Defines the byte order (endianness) to use in this Stream
        
        Members:
        
          EBigEndian : 
        
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        
          ENetworkByteOrder : x86, x86_64
        """

        def __init__(self: mitsuba.Stream.EByteOrder, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        EBigEndian = 0
        """
          EBigEndian : 
        """
        ELittleEndian = 1
        """
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        """

        ...

    class EMode:
        """
        
        Members:
        
          ERead : Opens a file in (binary) read-only mode
        
          EReadWrite : Opens (but never creates) a file in (binary) read-write mode
        
          ETruncReadWrite : Opens (and truncates) a file in (binary) read-write mode
        """

        def __init__(self: mitsuba.FileStream.EMode, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        ERead = 0
        """
          ERead : Opens a file in (binary) read-only mode
          EReadWrite : Opens (but never creates) a file in (binary) read-write mode
        """
        EReadWrite = 1
        """
          EReadWrite : Opens (but never creates) a file in (binary) read-write mode
        """
        ETruncReadWrite = 2
        """
          ETruncReadWrite : Opens (and truncates) a file in (binary) read-write mode
        """

        ...

    ptr = ...

    EBigEndian = 0
    """
      EBigEndian : 
    """
    ELittleEndian = 1
    """
      ELittleEndian : PowerPC, SPARC, Motorola 68K
    """
    ERead = 0
    """
      ERead : Opens a file in (binary) read-only mode
      EReadWrite : Opens (but never creates) a file in (binary) read-write mode
    """
    EReadWrite = 1
    """
      EReadWrite : Opens (but never creates) a file in (binary) read-write mode
    """
    ETruncReadWrite = 2
    """
      ETruncReadWrite : Opens (and truncates) a file in (binary) read-write mode
    """

    def byte_order(self: mitsuba.Stream) -> mitsuba.Stream.EByteOrder:
        """
        Returns the byte order of this stream.
        """
        ...

    def can_read(self: mitsuba.Stream) -> bool:
        """
        Can we read from the stream?
        """
        ...

    def can_write(self: mitsuba.Stream) -> bool:
        """
        Can we write to the stream?
        """
        ...

    def close(self: mitsuba.Stream) -> None:
        """
        Closes the stream.
        
        No further read or write operations are permitted.
        
        This function is idempotent. It may be called automatically by the
        destructor.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def flush(self: mitsuba.Stream) -> None:
        """
        Flushes the stream's buffers, if any
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def path(self: mitsuba.FileStream) -> mitsuba.filesystem.path:
        """
        Return the path descriptor associated with this FileStream
        """
        ...

    def read(self: mitsuba.Stream, arg0: int) -> bytes:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def read_bool(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_double(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_float(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_line(self: mitsuba.Stream) -> str:
        """
        Convenience function for reading a line of text from an ASCII file
        """
        ...

    def read_single(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_string(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def seek(self: mitsuba.Stream, arg0: int) -> None:
        """
        Seeks to a position inside the stream.
        
        Seeking beyond the size of the buffer will not modify the length of
        its contents. However, a subsequent write should start at the sought
        position and update the size appropriately.
        """
        ...

    def set_byte_order(self: mitsuba.Stream, arg0: mitsuba.Stream.EByteOrder) -> None:
        """
        Sets the byte order to use in this stream.
        
        Automatic conversion will be performed on read and write operations to
        match the system's native endianness.
        
        No consistency is guaranteed if this method is called after performing
        some read and write operations on the system using a different
        endianness.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def size(self: mitsuba.Stream) -> int:
        """
        Returns the size of the stream
        """
        ...

    def skip(self: mitsuba.Stream, arg0: int) -> None:
        """
        Skip ahead by a given number of bytes
        """
        ...

    def tell(self: mitsuba.Stream) -> int:
        """
        Gets the current position inside the stream
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def truncate(self: mitsuba.Stream, arg0: int) -> None:
        """
        Truncates the stream to a given size.
        
        The position is updated to ``min(old_position, size)``. Throws an
        exception if in read-only mode.
        """
        ...

    def write(self: mitsuba.Stream, arg0: bytes) -> None:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def write_bool(self: mitsuba.Stream, arg0: bool) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_double(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_float(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_line(self: mitsuba.Stream, arg0: str) -> None:
        """
        Convenience function for writing a line of text to an ASCII file
        """
        ...

    def write_single(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_string(self: mitsuba.Stream, arg0: str) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    ...

class Film(Object):
    """
    Abstract film base class - used to store samples generated by
    Integrator implementations.
    
    To avoid lock-related bottlenecks when rendering with many cores,
    rendering threads first store results in an "image block", which is
    then committed to the film using the put() method.
    """

    def __init__(self: mitsuba.Film, props: mitsuba.Properties) -> None: ...
    ptr = ...

    def base_channels_count(self: mitsuba.Film) -> int:
        """
        Return the number of channels for the developed image (excluding AOVS)
        """
        ...

    def bitmap(self: mitsuba.Film, raw: bool = False) -> mitsuba.Bitmap:
        """
        Return a bitmap object storing the developed contents of the film
        """
        ...

    def clear(self: mitsuba.Film) -> None:
        """
        Clear the film contents to zero.
        """
        ...

    def create_block(self: mitsuba.Film, size: mitsuba.Vector2u = [0, 0], normalize: bool = False, borders: bool = False):
        """
        Return an ImageBlock instance, whose internal representation is
        compatible with that of the film.
        
        Image blocks created using this method can later be merged into the
        film using put_block().
        
        Parameter ``size``:
            Desired size of the returned image block.
        
        Parameter ``normalize``:
            Force normalization of filter weights in ImageBlock::put()? See
            the ImageBlock constructor for details.
        
        Parameter ``border``:
            Should ``ImageBlock`` add an additional border region around
            around the image boundary? See the ImageBlock constructor for
            details.
        """
        ...

    def crop_offset(self: mitsuba.Film) -> mitsuba.Point2u:
        """
        Return the offset of the crop window
        """
        ...

    def crop_size(self: mitsuba.Film) -> mitsuba.Vector2u:
        """
        Return the size of the crop window
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def develop(self: mitsuba.Film, raw: bool = False) -> mitsuba.TensorXf:
        """
        Return a image buffer object storing the developed image
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def flags(self: mitsuba.Film) -> int:
        """
        Flags for all properties combined.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def prepare(self: mitsuba.Film, aovs: List[str]) -> int:
        """
        Configure the film for rendering a specified set of extra channels
        (AOVS). Returns the total number of channels that the film will store
        """
        ...

    def prepare_sample(self: mitsuba.Film, spec: mitsuba.Color3f, wavelengths: mitsuba.Color0f, nChannels: int, weight: float = 1.0, alpha: float = 1.0, active: bool = True) -> List[float]:
        """
        Prepare spectrum samples to be in the format expected by the film
        
        It will be used if the Film contains the ``Special`` flag enabled.
        
        This method should be applied with films that deviate from HDR film
        behavior. Normally ``Films`` will store within the ``ImageBlock`` the
        samples following an RGB shape. But ``Films`` may want to store the
        samples with other structures (e.g. store several channels containing
        monochromatic information). In that situation, this method allows
        transforming the sample format generated by the integrators to the one
        that the Film will store inside the ImageBlock.
        
        Parameter ``spec``:
            Sample value associated with the specified wavelengths
        
        Parameter ``wavelengths``:
            Sample wavelengths in nanometers
        
        Parameter ``aovs``:
            Points to an array of length equal to the number of spectral
            sensitivities of the film, which specifies the sample value for
            each channel.
        
        Parameter ``weight``:
            Value to be added to the weight channel of the sample
        
        Parameter ``alpha``:
            Alpha value of the sample
        
        Parameter ``active``:
            Mask indicating if the lanes are active
        """
        ...

    def put_block(self: mitsuba.Film, block) -> None:
        """
        Merge an image block into the film. This methods should be thread-
        safe.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def rfilter(self: mitsuba.Film) -> mitsuba.ReconstructionFilter:
        """
        Return the image reconstruction filter (const version)
        """
        ...

    def sample_border(self: mitsuba.Film) -> bool:
        """
        Should regions slightly outside the image plane be sampled to improve
        the quality of the reconstruction at the edges? This only makes sense
        when reconstruction filters other than the box filter are used.
        """
        ...

    def schedule_storage(self: mitsuba.Film) -> None:
        """
        dr::schedule() variables that represent the internal film storage
        """
        ...

    def sensor_response_function(self: mitsuba.Film):
        """
        Returns the specific Sensor Response Function (SRF) used by the film
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def size(self: mitsuba.Film) -> mitsuba.Vector2u:
        """
        Ignoring the crop window, return the resolution of the underlying
        sensor
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def write(self: mitsuba.Film, path: mitsuba.filesystem.path) -> None:
        """
        Write the developed contents of the film to a file on disk
        """
        ...

    ...

class FilmFlags:
    """
    This list of flags is used to classify the different types of films.
    
    Members:
    
      Empty : No flags set (default value)
    
      Alpha : The film stores an alpha channel
    
      Spectral : The film stores a spectral representation of the image
    
      Special : The film provides a customized prepare_sample() routine that
    implements a special treatment of the samples before storing them in
    the Image Block.
    """

    def __init__(self: mitsuba.FilmFlags, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Alpha = 1
    """
      Alpha : The film stores an alpha channel
    """
    Empty = 0
    """
      Empty : No flags set (default value)
    """
    Special = 4
    """
      Special : The film provides a customized prepare_sample() routine that
    """
    Spectral = 2
    """
      Spectral : The film stores a spectral representation of the image
    """

    ...

class FilterBoundaryCondition:
    """
    When resampling data to a different resolution using
    Resampler::resample(), this enumeration specifies how lookups
    *outside* of the input domain are handled.
    
    See also:
        Resampler
    
    Members:
    
      Clamp : Clamp to the outermost sample position (default)
    
      Repeat : Assume that the input repeats in a periodic fashion
    
      Mirror : Assume that the input is mirrored along the boundary
    
      Zero : Assume that the input function is zero outside of the defined domain
    
      One : Assume that the input function is equal to one outside of the defined
    domain
    """

    def __init__(self: mitsuba.FilterBoundaryCondition, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Clamp = 0
    """
      Clamp : Clamp to the outermost sample position (default)
    """
    Mirror = 2
    """
      Mirror : Assume that the input is mirrored along the boundary
    """
    One = 4
    """
      One : Assume that the input function is equal to one outside of the defined
    """
    Repeat = 1
    """
      Repeat : Assume that the input repeats in a periodic fashion
    """
    Zero = 3
    """
      Zero : Assume that the input function is zero outside of the defined domain
    """

    ...

class Float: ...

class Float32: ...

class Float64: ...

class Formatter(Object):
    """
    Abstract interface for converting log information into a human-
    readable format
    """

    def __init__(self: mitsuba.Formatter) -> None: ...
    ptr = ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def format(self: mitsuba.Formatter, level: mitsuba.LogLevel, class_: mitsuba.Class, thread, file: str, line: int, msg: str) -> str:
        """
        Turn a log message into a human-readable format
        
        Parameter ``level``:
            The importance of the debug message
        
        Parameter ``class_``:
            Originating class or ``nullptr``
        
        Parameter ``thread``:
            Thread, which is responsible for creating the message
        
        Parameter ``file``:
            File, which is responsible for creating the message
        
        Parameter ``line``:
            Associated line within the source file
        
        Parameter ``msg``:
            Text content associated with the log message
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Frame3f:
    """
    Stores a three-dimensional orthonormal coordinate frame
    
    This class is used to convert between different cartesian coordinate
    systems and to efficiently evaluate trigonometric functions in a
    spherical coordinate system whose pole is aligned with the ``n`` axis
    (e.g. cos_theta(), sin_phi(), etc.).
    """

    @overload
    def __init__(self: mitsuba.Frame3f) -> None:
        """
        Construct a new coordinate frame from a single vector
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Frame3f, arg0: mitsuba.Frame3f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Frame3f, arg0: mitsuba.Vector3f, arg1: mitsuba.Vector3f, arg2: mitsuba.Vector3f) -> None: ...
    @overload
    def __init__(self: mitsuba.Frame3f, arg0: mitsuba.Vector3f) -> None: ...
    n = ...
    s = ...
    t = ...

    def assign(self: mitsuba.Frame3f, arg0: mitsuba.Frame3f) -> None: ...
    def to_local(self: mitsuba.Frame3f, v: mitsuba.Vector3f) -> mitsuba.Vector3f:
        """
        Convert from world coordinates to local coordinates
        """
        ...

    def to_world(self: mitsuba.Frame3f, v: mitsuba.Vector3f) -> mitsuba.Vector3f:
        """
        Convert from local coordinates to world coordinates
        """
        ...

    ...

class Hierarchical2D0:
    """
    Implements a hierarchical sample warping scheme for 2D distributions
    with linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed from a sequence of ``log2(max(res))``
    hierarchical sample warping steps, where ``res`` is the input array
    resolution. It is bijective and generally very well-behaved (i.e. low
    distortion), which makes it a good choice for structured point sets
    such as the Halton or Sobol sequence.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named Hierarchical2D0, Hierarchical2D1, and Hierarchical2D2
        for data that depends on 0, 1, and 2 parameters, respectively.
    """

    def __init__(self: mitsuba.Hierarchical2D0, data: numpy.ndarray[numpy.float32], param_values: List[List[float][0]] = [], normalize: bool = True, enable_sampling: bool = True) -> None:
        """
        Construct a hierarchical sample warping scheme for floating point data
        of resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Hierarchical2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the hierarchy needed for sample warping, which saves
        memory in case this functionality is not needed (e.g. if only the
        interpolation in ``eval()`` is used). In this case, ``sample()`` and
        ``invert()`` can still be called without triggering undefined
        behavior, but they will not return meaningful results.
        """
        ...

    def eval(self: mitsuba.Hierarchical2D0, pos: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.Hierarchical2D0, sample: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.Hierarchical2D0, sample: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class Hierarchical2D1:
    """
    Implements a hierarchical sample warping scheme for 2D distributions
    with linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed from a sequence of ``log2(max(res))``
    hierarchical sample warping steps, where ``res`` is the input array
    resolution. It is bijective and generally very well-behaved (i.e. low
    distortion), which makes it a good choice for structured point sets
    such as the Halton or Sobol sequence.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named Hierarchical2D0, Hierarchical2D1, and Hierarchical2D2
        for data that depends on 0, 1, and 2 parameters, respectively.
    """

    def __init__(self: mitsuba.Hierarchical2D1, data: numpy.ndarray[numpy.float32], param_values: List[List[float][1]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a hierarchical sample warping scheme for floating point data
        of resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Hierarchical2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the hierarchy needed for sample warping, which saves
        memory in case this functionality is not needed (e.g. if only the
        interpolation in ``eval()`` is used). In this case, ``sample()`` and
        ``invert()`` can still be called without triggering undefined
        behavior, but they will not return meaningful results.
        """
        ...

    def eval(self: mitsuba.Hierarchical2D1, pos: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.Hierarchical2D1, sample: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.Hierarchical2D1, sample: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class Hierarchical2D2:
    """
    Implements a hierarchical sample warping scheme for 2D distributions
    with linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed from a sequence of ``log2(max(res))``
    hierarchical sample warping steps, where ``res`` is the input array
    resolution. It is bijective and generally very well-behaved (i.e. low
    distortion), which makes it a good choice for structured point sets
    such as the Halton or Sobol sequence.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named Hierarchical2D0, Hierarchical2D1, and Hierarchical2D2
        for data that depends on 0, 1, and 2 parameters, respectively.
    """

    def __init__(self: mitsuba.Hierarchical2D2, data: numpy.ndarray[numpy.float32], param_values: List[List[float][2]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a hierarchical sample warping scheme for floating point data
        of resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Hierarchical2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the hierarchy needed for sample warping, which saves
        memory in case this functionality is not needed (e.g. if only the
        interpolation in ``eval()`` is used). In this case, ``sample()`` and
        ``invert()`` can still be called without triggering undefined
        behavior, but they will not return meaningful results.
        """
        ...

    def eval(self: mitsuba.Hierarchical2D2, pos: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.Hierarchical2D2, sample: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.Hierarchical2D2, sample: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class Hierarchical2D3:
    """
    Implements a hierarchical sample warping scheme for 2D distributions
    with linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed from a sequence of ``log2(max(res))``
    hierarchical sample warping steps, where ``res`` is the input array
    resolution. It is bijective and generally very well-behaved (i.e. low
    distortion), which makes it a good choice for structured point sets
    such as the Halton or Sobol sequence.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named Hierarchical2D0, Hierarchical2D1, and Hierarchical2D2
        for data that depends on 0, 1, and 2 parameters, respectively.
    """

    def __init__(self: mitsuba.Hierarchical2D3, data: numpy.ndarray[numpy.float32], param_values: List[List[float][3]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a hierarchical sample warping scheme for floating point data
        of resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Hierarchical2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the hierarchy needed for sample warping, which saves
        memory in case this functionality is not needed (e.g. if only the
        interpolation in ``eval()`` is used). In this case, ``sample()`` and
        ``invert()`` can still be called without triggering undefined
        behavior, but they will not return meaningful results.
        """
        ...

    def eval(self: mitsuba.Hierarchical2D3, pos: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.Hierarchical2D3, sample: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.Hierarchical2D3, sample: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class ImageBlock(Object):
    """
    Intermediate storage for an image or image sub-region being rendered
    
    This class facilitates parallel rendering of images in both scalar and
    JIT-based variants of Mitsuba.
    
    In scalar mode, image blocks represent independent rectangular image
    regions that are simultaneously processed by worker threads. They are
    finally merged into a master ImageBlock controlled by the Film
    instance via the put_block() method. The smaller image blocks can
    include a border region storing contributions that are slightly
    outside of the block, which is required to correctly account for image
    reconstruction filters.
    
    In JIT variants there is only a single ImageBlock, whose contents are
    computed in parallel. A border region is usually not needed in this
    case.
    
    In addition to receiving samples via the put() method, the image block
    can also be queried via the read() method, in which case the
    reconstruction filter is used to compute suitable interpolation
    weights. This is feature is useful for differentiable rendering, where
    one needs to evaluate the reverse-mode derivative of the put() method.
    """

    @overload
    def __init__(self: mitsuba.ImageBlock, size: mitsuba.Vector2u, offset: mitsuba.Point2i, channel_count: int, rfilter: mitsuba.ReconstructionFilter = None, border: bool = True, normalize: bool = False, coalesce: bool = False, compensate: bool = False, warn_negative: bool = True, warn_invalid: bool = True) -> None: ...
    @overload
    def __init__(self: mitsuba.ImageBlock, tensor: mitsuba.TensorXf, offset: mitsuba.Point2i = [0, 0], rfilter: mitsuba.ReconstructionFilter = None, border: bool = True, normalize: bool = False, coalesce: bool = False, compensate: bool = False, warn_negative: bool = True, warn_invalid: bool = True) -> None: ...
    ptr = ...

    def border_size(self: mitsuba.ImageBlock) -> int:
        """
        Return the border region used by the reconstruction filter
        """
        ...

    def channel_count(self: mitsuba.ImageBlock) -> int:
        """
        Return the number of channels stored by the image block
        """
        ...

    def clear(self: mitsuba.ImageBlock) -> None:
        """
        Clear the image block contents to zero.
        """
        ...

    def coalesce(self: mitsuba.ImageBlock) -> bool:
        """
        Try to coalesce reads/writes in JIT modes?
        """
        ...

    def compensate(self: mitsuba.ImageBlock) -> bool:
        """
        Use Kahan-style error-compensated floating point accumulation?
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def has_border(self: mitsuba.ImageBlock) -> bool:
        """
        Does the image block have a border region?
        """
        ...

    def height(self: mitsuba.ImageBlock) -> int:
        """
        Return the bitmap's height in pixels
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def normalize(self: mitsuba.ImageBlock) -> bool:
        """
        Re-normalize filter weights in put() and read()
        """
        ...

    def offset(self: mitsuba.ImageBlock) -> mitsuba.Point2i:
        """
        Return the current block offset
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    @overload
    def put(self: mitsuba.ImageBlock, pos: mitsuba.Point2f, wavelengths: mitsuba.Color0f, value: mitsuba.Color3f, alpha: float = 1.0, weight: float = 1, active: bool = True) -> None:
        """
        Accumulate a single sample or a wavefront of samples into the image
        block.
        
        Parameter ``pos``:
            Denotes the sample position in fractional pixel coordinates
        
        Parameter ``values``:
            Points to an array of length channel_count(), which specifies the
            sample value for each channel.
        
        """
        ...

    @overload
    def put(self: mitsuba.ImageBlock, pos: mitsuba.Point2f, values: List[float], active: bool = True) -> None: ...
    def put_block(self: mitsuba.ImageBlock, block: mitsuba.ImageBlock) -> None:
        """
        Accumulate another image block into this one
        """
        ...

    def read(self: mitsuba.ImageBlock, pos: mitsuba.Point2f, active: bool = True) -> List[float]: ...
    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def rfilter(self: mitsuba.ImageBlock) -> mitsuba.ReconstructionFilter:
        """
        Return the image reconstruction filter underlying the ImageBlock
        """
        ...

    def set_coalesce(self: mitsuba.ImageBlock, arg0: bool) -> None:
        """
        Try to coalesce reads/writes in JIT modes?
        """
        ...

    def set_compensate(self: mitsuba.ImageBlock, arg0: bool) -> None:
        """
        Use Kahan-style error-compensated floating point accumulation?
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_normalize(self: mitsuba.ImageBlock, arg0: bool) -> None:
        """
        Re-normalize filter weights in put() and read()
        """
        ...

    def set_offset(self: mitsuba.ImageBlock, offset: mitsuba.Point2i) -> None:
        """
        Set the current block offset.
        
        This corresponds to the offset from the top-left corner of a larger
        image (e.g. a Film) to the top-left corner of this ImageBlock
        instance.
        """
        ...

    def set_size(self: mitsuba.ImageBlock, size: mitsuba.Vector2u) -> None:
        """
        Set the block size. This potentially destroys the block's content.
        """
        ...

    def set_warn_invalid(self: mitsuba.ImageBlock, value: bool) -> None:
        """
        Warn when writing invalid (NaN, +/- infinity) sample values?
        """
        ...

    def set_warn_negative(self: mitsuba.ImageBlock, value: bool) -> None:
        """
        Warn when writing negative sample values?
        """
        ...

    def size(self: mitsuba.ImageBlock) -> mitsuba.Vector2u:
        """
        Return the current block size
        """
        ...

    def tensor(self: mitsuba.ImageBlock) -> mitsuba.TensorXf:
        """
        Return the underlying image tensor
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def warn_invalid(self: mitsuba.ImageBlock) -> bool:
        """
        Warn when writing invalid (NaN, +/- infinity) sample values?
        """
        ...

    def warn_negative(self: mitsuba.ImageBlock) -> bool:
        """
        Warn when writing negative sample values?
        """
        ...

    def width(self: mitsuba.ImageBlock) -> int:
        """
        Return the bitmap's width in pixels
        """
        ...

    ...

class Int: ...

class Int32: ...

class Int64: ...

class Integrator(Object):
    """
    Abstract integrator base class, which does not make any assumptions
    with regards to how radiance is computed.
    
    In Mitsuba, the different rendering techniques are collectively
    referred to as *integrators*, since they perform integration over a
    high-dimensional space. Each integrator represents a specific approach
    for solving the light transport equation---usually favored in certain
    scenarios, but at the same time affected by its own set of intrinsic
    limitations. Therefore, it is important to carefully select an
    integrator based on user-specified accuracy requirements and
    properties of the scene to be rendered.
    
    This is the base class of all integrators; it does not make any
    assumptions on how radiance is computed, which allows for many
    different kinds of implementations.
    """

    ptr = ...

    def aov_names(self: mitsuba.Integrator) -> List[str]:
        """
        For integrators that return one or more arbitrary output variables
        (AOVs), this function specifies a list of associated channel names.
        The default implementation simply returns an empty vector.
        """
        ...

    def cancel(self: mitsuba.Integrator) -> None:
        """
        Cancel a running render job (e.g. after receiving Ctrl-C)
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function renders the scene from the viewpoint of ``sensor``. All
        other parameters are optional and control different aspects of the
        rendering process. In particular:
        
        Parameter ``seed``:
            This parameter controls the initialization of the random number
            generator. It is crucial that you specify different seeds (e.g.,
            an increasing sequence) if subsequent ``render``() calls should
            produce statistically independent images.
        
        Parameter ``spp``:
            Set this parameter to a nonzero value to override the number of
            samples per pixel. This value then takes precedence over whatever
            was specified in the construction of ``sensor->sampler()``. This
            parameter may be useful in research applications where an image
            must be rendered multiple times using different quality levels.
        
        Parameter ``develop``:
            If set to ``True``, the implementation post-processes the data
            stored in ``sensor->film()``, returning the resulting image as a
            TensorXf. Otherwise, it returns an empty tensor.
        
        Parameter ``evaluate``:
            This parameter is only relevant for JIT variants of Mitsuba (LLVM,
            CUDA). If set to ``True``, the rendering step evaluates the
            generated image and waits for its completion. A log message also
            denotes the rendering time. Otherwise, the returned tensor
            (``develop=true``) or modified film (``develop=false``) represent
            the rendering task as an unevaluated computation graph.
        
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor: int = 0, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function is just a thin wrapper around the previous render()
        overload. It accepts a sensor *index* instead and renders the scene
        using sensor 0 by default.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def should_stop(self: mitsuba.Integrator) -> bool:
        """
        Indicates whether cancel() or a timeout have occurred. Should be
        checked regularly in the integrator's main loop so that timeouts are
        enforced accurately.
        
        Note that accurate timeouts rely on m_render_timer, which needs to be
        reset at the beginning of the rendering phase.
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Interaction3f:
    """
    Generic surface interaction data structure
    """

    @overload
    def __init__(self: mitsuba.Interaction3f) -> None:
        """
        Constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Interaction3f, arg0: mitsuba.Interaction3f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Interaction3f, t: float, time: float, wavelengths: mitsuba.Color0f, p: mitsuba.Point3f, n: mitsuba.Normal3f = 0) -> None:
        """
        //! @}
        """
        ...

    n = ...
    "Geometric normal (only valid for ``SurfaceInteraction``)"
    p = ...
    "Position of the interaction in world coordinates"
    t = ...
    "Distance traveled along the ray"
    time = ...
    "Time value associated with the interaction"
    wavelengths = ...
    "Wavelengths associated with the ray that produced this interaction"

    def assign(self: mitsuba.Interaction3f, arg0: mitsuba.Interaction3f) -> None: ...
    def is_valid(self: mitsuba.Interaction3f) -> bool:
        """
        Is the current interaction valid?
        """
        ...

    def spawn_ray(self: mitsuba.Interaction3f, d: mitsuba.Vector3f) -> mitsuba.Ray3f:
        """
        Spawn a semi-infinite ray towards the given direction
        """
        ...

    def spawn_ray_to(self: mitsuba.Interaction3f, t: mitsuba.Point3f) -> mitsuba.Ray3f:
        """
        Spawn a finite ray towards the given position
        """
        ...

    ...

class IrregularContinuousDistribution:
    """
    Continuous 1D probability distribution defined in terms of an
    *irregularly* sampled linear interpolant
    
    This data structure represents a continuous 1D probability
    distribution that is defined as a linear interpolant of an irregularly
    discretized signal. The class provides various routines for
    transforming uniformly distributed samples so that they follow the
    stored distribution. Note that unnormalized probability density
    functions (PDFs) will automatically be normalized during
    initialization. The associated scale factor can be retrieved using the
    function normalization().
    """

    @overload
    def __init__(self: mitsuba.IrregularContinuousDistribution) -> None:
        """
        Continuous 1D probability distribution defined in terms of an
        *irregularly* sampled linear interpolant
        
        This data structure represents a continuous 1D probability
        distribution that is defined as a linear interpolant of an irregularly
        discretized signal. The class provides various routines for
        transforming uniformly distributed samples so that they follow the
        stored distribution. Note that unnormalized probability density
        functions (PDFs) will automatically be normalized during
        initialization. The associated scale factor can be retrieved using the
        function normalization().
        
        """
        ...

    @overload
    def __init__(self: mitsuba.IrregularContinuousDistribution, arg0: mitsuba.IrregularContinuousDistribution) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.IrregularContinuousDistribution, nodes: mitsuba.ArrayXf, pdf: mitsuba.ArrayXf) -> None:
        """
        Initialize from a given density function discretized on nodes
        ``nodes``
        """
        ...

    def cdf(self: mitsuba.IrregularContinuousDistribution) -> mitsuba.ArrayXf:
        """
        Return the unnormalized discrete cumulative distribution function over
        intervals
        """
        ...

    def empty(self: mitsuba.IrregularContinuousDistribution) -> bool:
        """
        Is the distribution object empty/uninitialized?
        """
        ...

    def eval_cdf(self: mitsuba.IrregularContinuousDistribution, x: float, active: bool = True) -> float:
        """
        Evaluate the unnormalized cumulative distribution function (CDF) at
        position ``p``
        """
        ...

    def eval_cdf_normalized(self: mitsuba.IrregularContinuousDistribution, x: float, active: bool = True) -> float:
        """
        Evaluate the unnormalized cumulative distribution function (CDF) at
        position ``p``
        """
        ...

    def eval_pdf(self: mitsuba.IrregularContinuousDistribution, x: float, active: bool = True) -> float:
        """
        Evaluate the unnormalized probability mass function (PDF) at position
        ``x``
        """
        ...

    def eval_pdf_normalized(self: mitsuba.IrregularContinuousDistribution, x: float, active: bool = True) -> float:
        """
        Evaluate the normalized probability mass function (PDF) at position
        ``x``
        """
        ...

    def integral(self: mitsuba.IrregularContinuousDistribution) -> float:
        """
        Return the original integral of PDF entries before normalization
        """
        ...

    def interval_resolution(self: mitsuba.IrregularContinuousDistribution) -> float:
        """
        Return the minimum resolution of the discretization
        """
        ...

    def max(self: mitsuba.IrregularContinuousDistribution) -> float: ...
    def nodes(self: mitsuba.IrregularContinuousDistribution) -> mitsuba.ArrayXf:
        """
        Return the nodes of the underlying discretization
        """
        ...

    def normalization(self: mitsuba.IrregularContinuousDistribution) -> float:
        """
        Return the normalization factor (i.e. the inverse of sum())
        """
        ...

    def pdf(self: mitsuba.IrregularContinuousDistribution) -> mitsuba.ArrayXf:
        """
        Return the unnormalized discretized probability density function
        """
        ...

    def range(self: mitsuba.IrregularContinuousDistribution) -> mitsuba.Array2f:
        """
        Return the range of the distribution
        """
        ...

    def sample(self: mitsuba.IrregularContinuousDistribution, value: float, active: bool = True) -> float:
        """
        %Transform a uniformly distributed sample to the stored distribution
        
        Parameter ``sample``:
            A uniformly distributed sample on the interval [0, 1].
        
        Returns:
            The sampled position.
        """
        ...

    def sample_pdf(self: mitsuba.IrregularContinuousDistribution, value: float, active: bool = True) -> Tuple[float, float]:
        """
        %Transform a uniformly distributed sample to the stored distribution
        
        Parameter ``sample``:
            A uniformly distributed sample on the interval [0, 1].
        
        Returns:
            A tuple consisting of
        
        1. the sampled position. 2. the normalized probability density of the
        sample.
        """
        ...

    def size(self: mitsuba.IrregularContinuousDistribution) -> int:
        """
        Return the number of discretizations
        """
        ...

    def update(self: mitsuba.IrregularContinuousDistribution) -> None:
        """
        Update the internal state. Must be invoked when changing the pdf or
        range.
        """
        ...

    ...

def Log(level: mitsuba.LogLevel, msg: str) -> None: ...
class LogLevel:
    """
    Available Log message types
    
    Members:
    
      Trace : 
    
      Debug : Trace message, for extremely verbose debugging
    
      Info : Debug message, usually turned off
    
      Warn : More relevant debug / information message
    
      Error : Warning message
    """

    def __init__(self: mitsuba.LogLevel, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Debug = 100
    """
      Debug : Trace message, for extremely verbose debugging
    """
    Error = 400
    """
      Error : Warning message
    """
    Info = 200
    """
      Info : Debug message, usually turned off
    """
    Trace = 0
    """
      Trace : 
    """
    Warn = 300
    """
      Warn : More relevant debug / information message
    """

    ...

class Logger(Object):
    """
    Responsible for processing log messages
    
    Upon receiving a log message, the Logger class invokes a Formatter to
    convert it into a human-readable form. Following that, it sends this
    information to every registered Appender.
    """

    def __init__(self: mitsuba.Logger, arg0: mitsuba.LogLevel) -> None:
        """
        Construct a new logger with the given minimum log level
        """
        ...

    ptr = ...

    def add_appender(self: mitsuba.Logger, arg0: mitsuba.Appender) -> None:
        """
        Add an appender to this logger
        """
        ...

    def appender(self: mitsuba.Logger, arg0: int) -> mitsuba.Appender:
        """
        Return one of the appenders
        """
        ...

    def appender_count(self: mitsuba.Logger) -> int:
        """
        Return the number of registered appenders
        """
        ...

    def clear_appenders(self: mitsuba.Logger) -> None:
        """
        Remove all appenders from this logger
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def error_level(self: mitsuba.Logger) -> mitsuba.LogLevel:
        """
        Return the current error level
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def formatter(self: mitsuba.Logger) -> mitsuba.Formatter:
        """
        Return the logger's formatter implementation
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def log_level(self: mitsuba.Logger) -> mitsuba.LogLevel:
        """
        Return the current log level
        """
        ...

    def log_progress(self: mitsuba.Logger, progress: float, name: str, formatted: str, eta: str, ptr: capsule = None) -> None:
        """
        Process a progress message
        
        Parameter ``progress``:
            Percentage value in [0, 100]
        
        Parameter ``name``:
            Title of the progress message
        
        Parameter ``formatted``:
            Formatted string representation of the message
        
        Parameter ``eta``:
            Estimated time until 100% is reached.
        
        Parameter ``ptr``:
            Custom pointer payload. This is used to express the context of a
            progress message. When rendering a scene, it will usually contain
            a pointer to the associated ``RenderJob``.
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def read_log(self: mitsuba.Logger) -> str:
        """
        Return the contents of the log file as a string
        
        Throws a runtime exception upon failure
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def remove_appender(self: mitsuba.Logger, arg0: mitsuba.Appender) -> None:
        """
        Remove an appender from this logger
        """
        ...

    def set_error_level(self: mitsuba.Logger, arg0: mitsuba.LogLevel) -> None:
        """
        Set the error log level (this level and anything above will throw
        exceptions).
        
        The value provided here can be used for instance to turn warnings into
        errors. But *level* must always be less than Error, i.e. it isn't
        possible to cause errors not to throw an exception.
        """
        ...

    def set_formatter(self: mitsuba.Logger, arg0: mitsuba.Formatter) -> None:
        """
        Set the logger's formatter implementation
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_log_level(self: mitsuba.Logger, arg0: mitsuba.LogLevel) -> None:
        """
        Set the log level (everything below will be ignored)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Loop:
    def __init__(self: mitsuba.Loop, arg0: str, *args) -> None: ...
    def __call__(self: mitsuba.Loop, arg0: bool) -> bool: ...
    def init(self: mitsuba.Loop) -> None: ...
    def put(self: mitsuba.Loop, *args) -> None: ...
    def set_max_iterations(self: mitsuba.Loop, arg0: bool) -> None: ...
    def set_uniform(self: mitsuba.Loop, arg0: bool) -> None: ...
    ...

MI_AUTHORS = ...
"""
str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.
"""
MI_CIE_D65_NORMALIZATION = ...
"Convert a string or number to a floating point number, if possible."
MI_CIE_MAX = ...
"Convert a string or number to a floating point number, if possible."
MI_CIE_MIN = ...
"Convert a string or number to a floating point number, if possible."
MI_CIE_Y_NORMALIZATION = ...
"Convert a string or number to a floating point number, if possible."
MI_ENABLE_CUDA = ...
"""
bool(x) -> bool

Returns True when the argument x is true, False otherwise.
The builtins True and False are the only two instances of the class bool.
The class bool is a subclass of the class int, and cannot be subclassed.
"""
MI_FILTER_RESOLUTION = ...
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
MI_VERSION = ...
"""
str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.
"""
MI_VERSION_MAJOR = ...
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
MI_VERSION_MINOR = ...
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
MI_VERSION_PATCH = ...
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
MI_YEAR = ...
"""
str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.
"""
class MarginalContinuous2D0:
    """
    Implements a marginal sample warping scheme for 2D distributions with
    linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed via the inversion method, which is applied
    to a marginal distribution over rows, followed by a conditional
    distribution over columns.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    There are two variants of ``Marginal2D:`` when ``Continuous=false``,
    discrete marginal/conditional distributions are used to select a
    bilinear bilinear patch, followed by a continuous sampling step that
    chooses a specific position inside the patch. When
    ``Continuous=true``, continuous marginal/conditional distributions are
    used instead, and the second step is no longer needed. The latter
    scheme requires more computation and memory accesses but produces an
    overall smoother mapping.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named ``MarginalDiscrete2D0`` to ``MarginalDiscrete2D3`` and
        ``MarginalContinuous2D0`` to ``MarginalContinuous2D3`` for data
        that depends on 0 to 3 parameters.
    """

    def __init__(self: mitsuba.MarginalContinuous2D0, data: numpy.ndarray[numpy.float32], param_values: List[List[float][0]] = [], normalize: bool = True, enable_sampling: bool = True) -> None:
        """
        Construct a marginal sample warping scheme for floating point data of
        resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Marginal2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the cdf needed for sample warping, which saves memory in
        case this functionality is not needed (e.g. if only the interpolation
        in ``eval()`` is used).
        """
        ...

    def eval(self: mitsuba.MarginalContinuous2D0, pos: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.MarginalContinuous2D0, sample: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.MarginalContinuous2D0, sample: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class MarginalContinuous2D1:
    """
    Implements a marginal sample warping scheme for 2D distributions with
    linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed via the inversion method, which is applied
    to a marginal distribution over rows, followed by a conditional
    distribution over columns.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    There are two variants of ``Marginal2D:`` when ``Continuous=false``,
    discrete marginal/conditional distributions are used to select a
    bilinear bilinear patch, followed by a continuous sampling step that
    chooses a specific position inside the patch. When
    ``Continuous=true``, continuous marginal/conditional distributions are
    used instead, and the second step is no longer needed. The latter
    scheme requires more computation and memory accesses but produces an
    overall smoother mapping.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named ``MarginalDiscrete2D0`` to ``MarginalDiscrete2D3`` and
        ``MarginalContinuous2D0`` to ``MarginalContinuous2D3`` for data
        that depends on 0 to 3 parameters.
    """

    def __init__(self: mitsuba.MarginalContinuous2D1, data: numpy.ndarray[numpy.float32], param_values: List[List[float][1]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a marginal sample warping scheme for floating point data of
        resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Marginal2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the cdf needed for sample warping, which saves memory in
        case this functionality is not needed (e.g. if only the interpolation
        in ``eval()`` is used).
        """
        ...

    def eval(self: mitsuba.MarginalContinuous2D1, pos: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.MarginalContinuous2D1, sample: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.MarginalContinuous2D1, sample: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class MarginalContinuous2D2:
    """
    Implements a marginal sample warping scheme for 2D distributions with
    linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed via the inversion method, which is applied
    to a marginal distribution over rows, followed by a conditional
    distribution over columns.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    There are two variants of ``Marginal2D:`` when ``Continuous=false``,
    discrete marginal/conditional distributions are used to select a
    bilinear bilinear patch, followed by a continuous sampling step that
    chooses a specific position inside the patch. When
    ``Continuous=true``, continuous marginal/conditional distributions are
    used instead, and the second step is no longer needed. The latter
    scheme requires more computation and memory accesses but produces an
    overall smoother mapping.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named ``MarginalDiscrete2D0`` to ``MarginalDiscrete2D3`` and
        ``MarginalContinuous2D0`` to ``MarginalContinuous2D3`` for data
        that depends on 0 to 3 parameters.
    """

    def __init__(self: mitsuba.MarginalContinuous2D2, data: numpy.ndarray[numpy.float32], param_values: List[List[float][2]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a marginal sample warping scheme for floating point data of
        resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Marginal2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the cdf needed for sample warping, which saves memory in
        case this functionality is not needed (e.g. if only the interpolation
        in ``eval()`` is used).
        """
        ...

    def eval(self: mitsuba.MarginalContinuous2D2, pos: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.MarginalContinuous2D2, sample: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.MarginalContinuous2D2, sample: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class MarginalContinuous2D3:
    """
    Implements a marginal sample warping scheme for 2D distributions with
    linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed via the inversion method, which is applied
    to a marginal distribution over rows, followed by a conditional
    distribution over columns.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    There are two variants of ``Marginal2D:`` when ``Continuous=false``,
    discrete marginal/conditional distributions are used to select a
    bilinear bilinear patch, followed by a continuous sampling step that
    chooses a specific position inside the patch. When
    ``Continuous=true``, continuous marginal/conditional distributions are
    used instead, and the second step is no longer needed. The latter
    scheme requires more computation and memory accesses but produces an
    overall smoother mapping.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named ``MarginalDiscrete2D0`` to ``MarginalDiscrete2D3`` and
        ``MarginalContinuous2D0`` to ``MarginalContinuous2D3`` for data
        that depends on 0 to 3 parameters.
    """

    def __init__(self: mitsuba.MarginalContinuous2D3, data: numpy.ndarray[numpy.float32], param_values: List[List[float][3]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a marginal sample warping scheme for floating point data of
        resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Marginal2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the cdf needed for sample warping, which saves memory in
        case this functionality is not needed (e.g. if only the interpolation
        in ``eval()`` is used).
        """
        ...

    def eval(self: mitsuba.MarginalContinuous2D3, pos: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.MarginalContinuous2D3, sample: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.MarginalContinuous2D3, sample: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class MarginalDiscrete2D0:
    """
    Implements a marginal sample warping scheme for 2D distributions with
    linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed via the inversion method, which is applied
    to a marginal distribution over rows, followed by a conditional
    distribution over columns.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    There are two variants of ``Marginal2D:`` when ``Continuous=false``,
    discrete marginal/conditional distributions are used to select a
    bilinear bilinear patch, followed by a continuous sampling step that
    chooses a specific position inside the patch. When
    ``Continuous=true``, continuous marginal/conditional distributions are
    used instead, and the second step is no longer needed. The latter
    scheme requires more computation and memory accesses but produces an
    overall smoother mapping.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named ``MarginalDiscrete2D0`` to ``MarginalDiscrete2D3`` and
        ``MarginalContinuous2D0`` to ``MarginalContinuous2D3`` for data
        that depends on 0 to 3 parameters.
    """

    def __init__(self: mitsuba.MarginalDiscrete2D0, data: numpy.ndarray[numpy.float32], param_values: List[List[float][0]] = [], normalize: bool = True, enable_sampling: bool = True) -> None:
        """
        Construct a marginal sample warping scheme for floating point data of
        resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Marginal2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the cdf needed for sample warping, which saves memory in
        case this functionality is not needed (e.g. if only the interpolation
        in ``eval()`` is used).
        """
        ...

    def eval(self: mitsuba.MarginalDiscrete2D0, pos: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.MarginalDiscrete2D0, sample: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.MarginalDiscrete2D0, sample: mitsuba.Array2f, param: mitsuba.Array0f = [], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class MarginalDiscrete2D1:
    """
    Implements a marginal sample warping scheme for 2D distributions with
    linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed via the inversion method, which is applied
    to a marginal distribution over rows, followed by a conditional
    distribution over columns.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    There are two variants of ``Marginal2D:`` when ``Continuous=false``,
    discrete marginal/conditional distributions are used to select a
    bilinear bilinear patch, followed by a continuous sampling step that
    chooses a specific position inside the patch. When
    ``Continuous=true``, continuous marginal/conditional distributions are
    used instead, and the second step is no longer needed. The latter
    scheme requires more computation and memory accesses but produces an
    overall smoother mapping.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named ``MarginalDiscrete2D0`` to ``MarginalDiscrete2D3`` and
        ``MarginalContinuous2D0`` to ``MarginalContinuous2D3`` for data
        that depends on 0 to 3 parameters.
    """

    def __init__(self: mitsuba.MarginalDiscrete2D1, data: numpy.ndarray[numpy.float32], param_values: List[List[float][1]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a marginal sample warping scheme for floating point data of
        resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Marginal2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the cdf needed for sample warping, which saves memory in
        case this functionality is not needed (e.g. if only the interpolation
        in ``eval()`` is used).
        """
        ...

    def eval(self: mitsuba.MarginalDiscrete2D1, pos: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.MarginalDiscrete2D1, sample: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.MarginalDiscrete2D1, sample: mitsuba.Array2f, param: mitsuba.Array1f = [0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class MarginalDiscrete2D2:
    """
    Implements a marginal sample warping scheme for 2D distributions with
    linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed via the inversion method, which is applied
    to a marginal distribution over rows, followed by a conditional
    distribution over columns.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    There are two variants of ``Marginal2D:`` when ``Continuous=false``,
    discrete marginal/conditional distributions are used to select a
    bilinear bilinear patch, followed by a continuous sampling step that
    chooses a specific position inside the patch. When
    ``Continuous=true``, continuous marginal/conditional distributions are
    used instead, and the second step is no longer needed. The latter
    scheme requires more computation and memory accesses but produces an
    overall smoother mapping.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named ``MarginalDiscrete2D0`` to ``MarginalDiscrete2D3`` and
        ``MarginalContinuous2D0`` to ``MarginalContinuous2D3`` for data
        that depends on 0 to 3 parameters.
    """

    def __init__(self: mitsuba.MarginalDiscrete2D2, data: numpy.ndarray[numpy.float32], param_values: List[List[float][2]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a marginal sample warping scheme for floating point data of
        resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Marginal2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the cdf needed for sample warping, which saves memory in
        case this functionality is not needed (e.g. if only the interpolation
        in ``eval()`` is used).
        """
        ...

    def eval(self: mitsuba.MarginalDiscrete2D2, pos: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.MarginalDiscrete2D2, sample: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.MarginalDiscrete2D2, sample: mitsuba.Array2f, param: mitsuba.Array2f = [0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class MarginalDiscrete2D3:
    """
    Implements a marginal sample warping scheme for 2D distributions with
    linear interpolation and an optional dependence on additional
    parameters
    
    This class takes a rectangular floating point array as input and
    constructs internal data structures to efficiently map uniform
    variates from the unit square ``[0, 1]^2`` to a function on ``[0,
    1]^2`` that linearly interpolates the input array.
    
    The mapping is constructed via the inversion method, which is applied
    to a marginal distribution over rows, followed by a conditional
    distribution over columns.
    
    The implementation also supports *conditional distributions*, i.e. 2D
    distributions that depend on an arbitrary number of parameters
    (indicated via the ``Dimension`` template parameter).
    
    In this case, the input array should have dimensions ``N0 x N1 x ... x
    Nn x res.y() x res.x()`` (where the last dimension is contiguous in
    memory), and the ``param_res`` should be set to ``{ N0, N1, ..., Nn
    }``, and ``param_values`` should contain the parameter values where
    the distribution is discretized. Linear interpolation is used when
    sampling or evaluating the distribution for in-between parameter
    values.
    
    There are two variants of ``Marginal2D:`` when ``Continuous=false``,
    discrete marginal/conditional distributions are used to select a
    bilinear bilinear patch, followed by a continuous sampling step that
    chooses a specific position inside the patch. When
    ``Continuous=true``, continuous marginal/conditional distributions are
    used instead, and the second step is no longer needed. The latter
    scheme requires more computation and memory accesses but produces an
    overall smoother mapping.
    
    Remark:
        The Python API exposes explicitly instantiated versions of this
        class named ``MarginalDiscrete2D0`` to ``MarginalDiscrete2D3`` and
        ``MarginalContinuous2D0`` to ``MarginalContinuous2D3`` for data
        that depends on 0 to 3 parameters.
    """

    def __init__(self: mitsuba.MarginalDiscrete2D3, data: numpy.ndarray[numpy.float32], param_values: List[List[float][3]], normalize: bool = True, build_hierarchy: bool = True) -> None:
        """
        Construct a marginal sample warping scheme for floating point data of
        resolution ``size``.
        
        ``param_res`` and ``param_values`` are only needed for conditional
        distributions (see the text describing the Marginal2D class).
        
        If ``normalize`` is set to ``False``, the implementation will not re-
        scale the distribution so that it integrates to ``1``. It can still be
        sampled (proportionally), but returned density values will reflect the
        unnormalized values.
        
        If ``enable_sampling`` is set to ``False``, the implementation will
        not construct the cdf needed for sample warping, which saves memory in
        case this functionality is not needed (e.g. if only the interpolation
        in ``eval()`` is used).
        """
        ...

    def eval(self: mitsuba.MarginalDiscrete2D3, pos: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> float:
        """
        Evaluate the density at position ``pos``. The distribution is
        parameterized by ``param`` if applicable.
        """
        ...

    def invert(self: mitsuba.MarginalDiscrete2D3, sample: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Inverse of the mapping implemented in ``sample()``
        """
        ...

    def sample(self: mitsuba.MarginalDiscrete2D3, sample: mitsuba.Array2f, param: mitsuba.Array3f = [0.0, 0.0, 0.0], active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Given a uniformly distributed 2D sample, draw a sample from the
        distribution (parameterized by ``param`` if applicable)
        
        Returns the warped sample and associated probability density.
        """
        ...

    ...

class Mask: ...

class Matrix2f64:
    def __init__(self: mitsuba.Matrix2f64, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Matrix2f:
    def __init__(self: mitsuba.Matrix2f, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Matrix3f64:
    def __init__(self: mitsuba.Matrix3f64, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Matrix3f:
    def __init__(self: mitsuba.Matrix3f, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Matrix4f64:
    def __init__(self: mitsuba.Matrix4f64, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Matrix4f:
    def __init__(self: mitsuba.Matrix4f, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Medium(Object):
    def __init__(self: mitsuba.Medium, arg0: mitsuba.Properties) -> None: ...
    m_has_spectral_extinction = ...
    m_is_homogeneous = ...
    m_sample_emitters = ...
    ptr = ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def get_majorant(self: mitsuba.Medium, mi, active: bool = True) -> mitsuba.Color3f:
        """
        Returns the medium's majorant used for delta tracking
        """
        ...

    def get_scattering_coefficients(self: mitsuba.Medium, mi, active: bool = True) -> Tuple[mitsuba.Color3f, mitsuba.Color3f, mitsuba.Color3f]:
        """
        Returns the medium coefficients Sigma_s, Sigma_n and Sigma_t evaluated
        at a given MediumInteraction mi
        """
        ...

    def has_spectral_extinction(self: mitsuba.Medium) -> bool:
        """
        Returns whether this medium has a spectrally varying extinction
        """
        ...

    def id(self: mitsuba.Medium) -> str:
        """
        Return a string identifier
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def intersect_aabb(self: mitsuba.Medium, ray: mitsuba.Ray3f) -> Tuple[bool, float, float]:
        """
        Intersects a ray with the medium's bounding box
        """
        ...

    def is_homogeneous(self: mitsuba.Medium) -> bool:
        """
        Returns whether this medium is homogeneous
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def phase_function(self: mitsuba.Medium):
        """
        Return the phase function of this medium
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_interaction(self: mitsuba.Medium, ray: mitsuba.Ray3f, sample: float, channel: int, active: bool):
        """
        Sample a free-flight distance in the medium.
        
        This function samples a (tentative) free-flight distance according to
        an exponential transmittance. It is then up to the integrator to then
        decide whether the MediumInteraction corresponds to a real or null
        scattering event.
        
        Parameter ``ray``:
            Ray, along which a distance should be sampled
        
        Parameter ``sample``:
            A uniformly distributed random sample
        
        Parameter ``channel``:
            The channel according to which we will sample the free-flight
            distance. This argument is only used when rendering in RGB modes.
        
        Returns:
            This method returns a MediumInteraction. The MediumInteraction
            will always be valid, except if the ray missed the Medium's
            bounding box.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def transmittance_eval_pdf(self: mitsuba.Medium, mi, si, active: bool) -> Tuple[mitsuba.Color3f, mitsuba.Color3f]:
        """
        Compute the transmittance and PDF
        
        This function evaluates the transmittance and PDF of sampling a
        certain free-flight distance The returned PDF takes into account if a
        medium interaction occurred (mi.t <= si.t) or the ray left the medium
        (mi.t > si.t)
        
        The evaluated PDF is spectrally varying. This allows to account for
        the fact that the free-flight distance sampling distribution can
        depend on the wavelength.
        
        Returns:
            This method returns a pair of (Transmittance, PDF).
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def use_emitter_sampling(self: mitsuba.Medium) -> bool:
        """
        Returns whether this specific medium instance uses emitter sampling
        """
        ...

    ...

class MediumInteraction3f(Interaction3f):
    """
    Stores information related to a medium scattering interaction
    """

    @overload
    def __init__(self: mitsuba.MediumInteraction3f) -> None:
        """
        //! @}
        
        """
        ...

    @overload
    def __init__(self: mitsuba.MediumInteraction3f, arg0: mitsuba.MediumInteraction3f) -> None:
        """
        Copy constructor
        """
        ...

    combined_extinction = ...
    medium = ...
    "Pointer to the associated medium"
    mint = ...
    "mint used when sampling the given distance ``t``"
    n = ...
    "Geometric normal (only valid for ``SurfaceInteraction``)"
    p = ...
    "Position of the interaction in world coordinates"
    sh_frame = ...
    "Shading frame"
    sigma_n = ...
    sigma_s = ...
    sigma_t = ...
    t = ...
    "Distance traveled along the ray"
    time = ...
    "Time value associated with the interaction"
    wavelengths = ...
    "Wavelengths associated with the ray that produced this interaction"
    wi = ...
    "Incident direction in world frame"

    def assign(self: mitsuba.MediumInteraction3f, arg0: mitsuba.MediumInteraction3f) -> None: ...
    def is_valid(self: mitsuba.Interaction3f) -> bool:
        """
        Is the current interaction valid?
        """
        ...

    def spawn_ray(self: mitsuba.Interaction3f, d: mitsuba.Vector3f) -> mitsuba.Ray3f:
        """
        Spawn a semi-infinite ray towards the given direction
        """
        ...

    def spawn_ray_to(self: mitsuba.Interaction3f, t: mitsuba.Point3f) -> mitsuba.Ray3f:
        """
        Spawn a finite ray towards the given position
        """
        ...

    def to_local(self: mitsuba.MediumInteraction3f, v: mitsuba.Vector3f) -> mitsuba.Vector3f:
        """
        Convert a world-space vector into local shading coordinates (defined
        by ``wi``)
        """
        ...

    def to_world(self: mitsuba.MediumInteraction3f, v: mitsuba.Vector3f) -> mitsuba.Vector3f:
        """
        Convert a local shading-space (defined by ``wi``) vector into world
        space
        """
        ...

    ...

class MemoryMappedFile(Object):
    """
    Basic cross-platform abstraction for memory mapped files
    
    Remark:
        The Python API has one additional constructor
        <tt>MemoryMappedFile(filename, array)<tt>, which creates a new
        file, maps it into memory, and copies the array contents.
    """

    @overload
    def __init__(self: mitsuba.MemoryMappedFile, filename: mitsuba.filesystem.path, size: int) -> None:
        """
        Create a new memory-mapped file of the specified size
        
        """
        ...

    @overload
    def __init__(self: mitsuba.MemoryMappedFile, filename: mitsuba.filesystem.path, write: bool = False) -> None:
        """
        Map the specified file into memory
        
        """
        ...

    @overload
    def __init__(self: mitsuba.MemoryMappedFile, filename: mitsuba.filesystem.path, array: numpy.ndarray) -> None: ...
    ptr = ...

    def can_write(self: mitsuba.MemoryMappedFile) -> bool:
        """
        Return whether the mapped memory region can be modified
        """
        ...

    def data(self: mitsuba.MemoryMappedFile) -> capsule:
        """
        Return a pointer to the file contents in memory
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def filename(self: mitsuba.MemoryMappedFile) -> mitsuba.filesystem.path:
        """
        Return the associated filename
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def resize(self: mitsuba.MemoryMappedFile, arg0: int) -> None:
        """
        Resize the memory-mapped file
        
        This involves remapping the file, which will generally change the
        pointer obtained via data()
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def size(self: mitsuba.MemoryMappedFile) -> int:
        """
        Return the size of the mapped region
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class MemoryStream(Stream):
    """
    Simple memory buffer-based stream with automatic memory management. It
    always has read & write capabilities.
    
    The underlying memory storage of this implementation dynamically
    expands as data is written to the stream, à la ``std::vector``.
    """

    def __init__(self: mitsuba.MemoryStream, capacity: int = 512) -> None:
        """
        Creates a new memory stream, initializing the memory buffer with a
        capacity of ``capacity`` bytes. For best performance, set this
        argument to the estimated size of the content that will be written to
        the stream.
        """
        ...

    class EByteOrder:
        """
        Defines the byte order (endianness) to use in this Stream
        
        Members:
        
          EBigEndian : 
        
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        
          ENetworkByteOrder : x86, x86_64
        """

        def __init__(self: mitsuba.Stream.EByteOrder, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        EBigEndian = 0
        """
          EBigEndian : 
        """
        ELittleEndian = 1
        """
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        """

        ...

    ptr = ...

    EBigEndian = 0
    """
      EBigEndian : 
    """
    ELittleEndian = 1
    """
      ELittleEndian : PowerPC, SPARC, Motorola 68K
    """

    def byte_order(self: mitsuba.Stream) -> mitsuba.Stream.EByteOrder:
        """
        Returns the byte order of this stream.
        """
        ...

    def can_read(self: mitsuba.Stream) -> bool:
        """
        Can we read from the stream?
        """
        ...

    def can_write(self: mitsuba.Stream) -> bool:
        """
        Can we write to the stream?
        """
        ...

    def capacity(self: mitsuba.MemoryStream) -> int:
        """
        Return the current capacity of the underlying memory buffer
        """
        ...

    def close(self: mitsuba.Stream) -> None:
        """
        Closes the stream.
        
        No further read or write operations are permitted.
        
        This function is idempotent. It may be called automatically by the
        destructor.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def flush(self: mitsuba.Stream) -> None:
        """
        Flushes the stream's buffers, if any
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def owns_buffer(self: mitsuba.MemoryStream) -> bool:
        """
        Return whether or not the memory stream owns the underlying buffer
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def raw_buffer(self: mitsuba.MemoryStream) -> bytes: ...
    def read(self: mitsuba.Stream, arg0: int) -> bytes:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def read_bool(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_double(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_float(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_line(self: mitsuba.Stream) -> str:
        """
        Convenience function for reading a line of text from an ASCII file
        """
        ...

    def read_single(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_string(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def seek(self: mitsuba.Stream, arg0: int) -> None:
        """
        Seeks to a position inside the stream.
        
        Seeking beyond the size of the buffer will not modify the length of
        its contents. However, a subsequent write should start at the sought
        position and update the size appropriately.
        """
        ...

    def set_byte_order(self: mitsuba.Stream, arg0: mitsuba.Stream.EByteOrder) -> None:
        """
        Sets the byte order to use in this stream.
        
        Automatic conversion will be performed on read and write operations to
        match the system's native endianness.
        
        No consistency is guaranteed if this method is called after performing
        some read and write operations on the system using a different
        endianness.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def size(self: mitsuba.Stream) -> int:
        """
        Returns the size of the stream
        """
        ...

    def skip(self: mitsuba.Stream, arg0: int) -> None:
        """
        Skip ahead by a given number of bytes
        """
        ...

    def tell(self: mitsuba.Stream) -> int:
        """
        Gets the current position inside the stream
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def truncate(self: mitsuba.Stream, arg0: int) -> None:
        """
        Truncates the stream to a given size.
        
        The position is updated to ``min(old_position, size)``. Throws an
        exception if in read-only mode.
        """
        ...

    def write(self: mitsuba.Stream, arg0: bytes) -> None:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def write_bool(self: mitsuba.Stream, arg0: bool) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_double(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_float(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_line(self: mitsuba.Stream, arg0: str) -> None:
        """
        Convenience function for writing a line of text to an ASCII file
        """
        ...

    def write_single(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_string(self: mitsuba.Stream, arg0: str) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    ...

class Mesh(Shape):
    @overload
    def __init__(self: mitsuba.Mesh, props: mitsuba.Properties) -> None: ...
    @overload
    def __init__(self: mitsuba.Mesh, name: str, vertex_count: int, face_count: int, props: mitsuba.Properties = Properties(), has_vertex_normals: bool = False, has_vertex_texcoords: bool = False) -> None:
        """
        Creates a zero-initialized mesh with the given vertex and face counts
        
        The vertex and face buffers can be filled using the ``mi.traverse``
        mechanism. When initializing these buffers through another method, an
        explicit call to initialize must be made once all buffers are filled.
        """
        ...

    ptr = ...

    def add_attribute(self: mitsuba.Mesh, name: str, size: int, buffer: List[float]) -> None:
        """
        Add an attribute buffer with the given ``name`` and ``dim``
        """
        ...

    @overload
    def bbox(self: mitsuba.Shape) -> mitsuba.BoundingBox3f:
        """
        Return an axis aligned box that bounds all shape primitives (including
        any transformations that may have been applied to them)
        
        """
        ...

    @overload
    def bbox(self: mitsuba.Shape, index: int) -> mitsuba.BoundingBox3f:
        """
        Return an axis aligned box that bounds a single shape primitive
        (including any transformations that may have been applied to it)
        
        Remark:
            The default implementation simply calls bbox()
        
        """
        ...

    @overload
    def bbox(self: mitsuba.Shape, index: int, clip: mitsuba.BoundingBox3f) -> mitsuba.BoundingBox3f:
        """
        Return an axis aligned box that bounds a single shape primitive after
        it has been clipped to another bounding box.
        
        This is extremely important to construct high-quality kd-trees. The
        default implementation just takes the bounding box returned by
        bbox(ScalarIndex index) and clips it to *clip*.
        """
        ...

    def bsdf(self: mitsuba.Shape):
        """
        Return the shape's BSDF
        """
        ...

    def compute_surface_interaction(self: mitsuba.Shape, ray: mitsuba.Ray3f, pi, ray_flags: int = 14, active: bool = True):
        """
        Compute and return detailed information related to a surface
        interaction
        
        The implementation should at most compute the fields ``p``, ``uv``,
        ``n``, ``sh_frame``.n, ``dp_du``, ``dp_dv``, ``dn_du`` and ``dn_dv``.
        The ``flags`` parameter specifies which of those fields should be
        computed.
        
        The fields ``t``, ``time``, ``wavelengths``, ``shape``,
        ``prim_index``, ``instance``, will already have been initialized by
        the caller. The field ``wi`` is initialized by the caller following
        the call to compute_surface_interaction(), and ``duv_dx``, and
        ``duv_dy`` are left uninitialized.
        
        Parameter ``ray``:
            Ray associated with the ray intersection
        
        Parameter ``pi``:
            Data structure carrying information about the ray intersection
        
        Parameter ``ray_flags``:
            Flags specifying which information should be computed
        
        Parameter ``recursion_depth``:
            Integer specifying the recursion depth for nested virtual function
            call to this method (e.g. used for instancing).
        
        Returns:
            A data structure containing the detailed information
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def differential_motion(self: mitsuba.Shape, si, active: bool = True) -> mitsuba.Point3f:
        """
        Return the attached (AD) point on the shape's surface
        
        This method is only useful when using automatic differentiation. The
        immediate/primal return value of this method is exactly equal to
        \`si.p\`.
        
        The input `si` does not need to be explicitly detached, it is done by
        the method itself.
        
        If the shape cannot be differentiated, this method will return the
        detached input point.
        
        note:: The returned attached point is exactly the same as a point
        which is computed by calling compute_surface_interaction with the
        RayFlags::FollowShape flag.
        
        Parameter ``si``:
            The surface point for which the function will be evaluated.
        
        Not all fields of the object need to be filled. Only the `prim_index`,
        `p` and `uv` fields are required. Certain shapes will only use a
        subset of these.
        
        Returns:
            The same surface point as the input but attached (AD) to the
            shape's parameters.
        """
        ...

    def effective_primitive_count(self: mitsuba.Shape) -> int:
        """
        Return the number of primitives (triangles, hairs, ..) contributed to
        the scene by this shape
        
        Includes instanced geometry. The default implementation simply returns
        the same value as primitive_count().
        """
        ...

    def emitter(self: mitsuba.Shape):
        """
        Return the area emitter associated with this shape (if any)
        """
        ...

    def eval_attribute(self: mitsuba.Shape, name: str, si, active: bool = True) -> mitsuba.Color3f:
        """
        Evaluate a specific shape attribute at the given surface interaction.
        
        Shape attributes are user-provided fields that provide extra
        information at an intersection. An example of this would be a per-
        vertex or per-face color on a triangle mesh.
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An unpolarized spectral power distribution or reflectance value
        """
        ...

    def eval_attribute_1(self: mitsuba.Shape, name: str, si, active: bool = True) -> float:
        """
        Monochromatic evaluation of a shape attribute at the given surface
        interaction
        
        This function differs from eval_attribute() in that it provided raw
        access to scalar intensity/reflectance values without any color
        processing (e.g. spectral upsampling).
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An scalar intensity or reflectance value
        """
        ...

    def eval_attribute_3(self: mitsuba.Shape, name: str, si, active: bool = True) -> mitsuba.Color3f:
        """
        Trichromatic evaluation of a shape attribute at the given surface
        interaction
        
        This function differs from eval_attribute() in that it provided raw
        access to RGB intensity/reflectance values without any additional
        color processing (e.g. RGB-to-spectral upsampling).
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An trichromatic intensity or reflectance value
        """
        ...

    def eval_parameterization(self: mitsuba.Shape, uv: mitsuba.Point2f, ray_flags: int = 14, active: bool = True):
        """
        Parameterize the mesh using UV values
        
        This function maps a 2D UV value to a surface interaction data
        structure. Its behavior is only well-defined in regions where this
        mapping is bijective. The default implementation throws.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def exterior_medium(self: mitsuba.Shape):
        """
        Return the medium that lies on the exterior of this shape
        """
        ...

    def face_count(self: mitsuba.Mesh) -> int:
        """
        Return the total number of faces
        """
        ...

    def face_indices(self: mitsuba.Mesh, index: int, active: bool = True) -> mitsuba.Array3u:
        """
        Returns the vertex indices associated with triangle ``index``
        """
        ...

    def has_attribute(self: mitsuba.Shape, name: str, active: bool = True) -> bool:
        """
        Returns whether this shape contains the specified attribute.
        
        Parameter ``name``:
            Name of the attribute
        """
        ...

    def has_vertex_normals(self: mitsuba.Mesh) -> bool:
        """
        Does this mesh have per-vertex normals?
        """
        ...

    def has_vertex_texcoords(self: mitsuba.Mesh) -> bool:
        """
        Does this mesh have per-vertex texture coordinates?
        """
        ...

    def id(self: mitsuba.Shape) -> str:
        """
        Return a string identifier
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def initialize(self: mitsuba.Mesh) -> None:
        """
        Must be called once at the end of the construction of a Mesh
        
        This method computes internal data structures and notifies the parent
        sensor or emitter (if there is one) that this instance is their
        internal shape.
        """
        ...

    def interior_medium(self: mitsuba.Shape):
        """
        Return the medium that lies on the interior of this shape
        """
        ...

    def invert_silhouette_sample(self: mitsuba.Shape, ss, active: bool = True) -> mitsuba.Point3f:
        """
        Map a silhouette segment to a point in boundary sample space
        
        This method is the inverse of sample_silhouette(). The mapping from/to
        boundary sample space to/from boundary segments is bijective.
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``ss``:
            The sampled boundary segment
        
        Returns:
            The corresponding boundary sample space point
        """
        ...

    def is_emitter(self: mitsuba.Shape) -> bool:
        """
        Is this shape also an area emitter?
        """
        ...

    def is_medium_transition(self: mitsuba.Shape) -> bool:
        """
        Does the surface of this shape mark a medium transition?
        """
        ...

    def is_mesh(self: mitsuba.Shape) -> bool:
        """
        Is this shape a triangle mesh?
        """
        ...

    def is_sensor(self: mitsuba.Shape) -> bool:
        """
        Is this shape also an area sensor?
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def parameters_grad_enabled(self: mitsuba.Shape) -> bool:
        """
        Return whether any shape's parameters that introduce visibility
        discontinuities require gradients (default return false)
        """
        ...

    def pdf_direction(self: mitsuba.Shape, it, ps, active: bool = True) -> float:
        """
        Query the probability density of sample_direction()
        
        Parameter ``it``:
            A reference position somewhere within the scene.
        
        Parameter ``ps``:
            A position record describing the sample in question
        
        Returns:
            The probability density per unit solid angle
        """
        ...

    def pdf_position(self: mitsuba.Shape, ps, active: bool = True) -> float:
        """
        Query the probability density of sample_position() for a particular
        point on the surface.
        
        Parameter ``ps``:
            A position record describing the sample in question
        
        Returns:
            The probability density per unit area
        """
        ...

    def precompute_silhouette(self: mitsuba.Shape, viewpoint: mitsuba.Point3f) -> Tuple[mitsuba.ArrayXu, mitsuba.ArrayXf]:
        """
        Precompute the visible silhouette of this shape for a given viewpoint.
        
        This method is meant to be used for silhouettes that are shared
        between all threads, as is the case for primarily visible derivatives.
        
        The return values are respectively a list of indices and their
        corresponding weights. The semantic meaning of these indices is
        different for each shape. For example, a triangle mesh will return the
        indices of all of its edges that constitute its silhouette. These
        indices are meant to be re-used as an argument when calling
        sample_precomputed_silhouette.
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``viewpoint``:
            The viewpoint which defines the silhouette of the shape
        
        Returns:
            A list of indices used by the shape internally to represent
            silhouettes, and a list of the same length containing the
            (unnormalized) weights associated to each index.
        """
        ...

    def primitive_count(self: mitsuba.Shape) -> int:
        """
        Returns the number of sub-primitives that make up this shape
        
        Remark:
            The default implementation simply returns ``1``
        """
        ...

    def primitive_silhouette_projection(self: mitsuba.Shape, viewpoint: mitsuba.Point3f, si, flags: int, sample: float, active: bool = True):
        """
        Projects a point on the surface of the shape to its silhouette as seen
        from a specified viewpoint.
        
        This method only projects the `si.p` point within its primitive.
        
        Not all of the fields of the SilhouetteSample3f might be filled by
        this method. Each shape will at the very least fill its return value
        with enough information for it to be used by invert_silhouette_sample.
        
        The projection operation might not find the closest silhouette point
        to the given surface point. For example, it can be guided by a random
        number ``sample``. Not all shapes types need this random number, each
        shape implementation is free to define its own algorithm and
        guarantees about the projection operation.
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``viewpoint``:
            The viewpoint which defines the silhouette to project the point
            to.
        
        Parameter ``si``:
            The surface point which will be projected.
        
        Parameter ``flags``:
            Flags to select the type of SilhouetteSample3f to generate from
            the projection. Only one type of discontinuity can be used per
            call.
        
        Parameter ``sample``:
            A random number that can be used to define the projection
            operation.
        
        Returns:
            A boundary segment on the silhouette of the shape as seen from
            ``viewpoint``.
        """
        ...

    def ray_intersect(self: mitsuba.Shape, ray: mitsuba.Ray3f, ray_flags: int = 14, active: bool = True):
        """
        Test for an intersection and return detailed information
        
        This operation combines the prior ray_intersect_preliminary() and
        compute_surface_interaction() operations.
        
        Parameter ``ray``:
            The ray to be tested for an intersection
        
        Parameter ``flags``:
            Describe how the detailed information should be computed
        """
        ...

    def ray_intersect_preliminary(self: mitsuba.Shape, ray: mitsuba.Ray3f, prim_index: int = 0, active: bool = True):
        """
        Fast ray intersection
        
        Efficiently test whether the shape is intersected by the given ray,
        and return preliminary information about the intersection if that is
        the case.
        
        If the intersection is deemed relevant (e.g. the closest to the ray
        origin), detailed intersection information can later be obtained via
        the create_surface_interaction() method.
        
        Parameter ``ray``:
            The ray to be tested for an intersection
        
        Parameter ``prim_index``:
            Index of the primitive to be intersected. This index is ignored by
            a shape that contains a single primitive. Otherwise, if no index
            is provided, the ray intersection will be performed on the shape's
            first primitive at index 0.
        """
        ...

    def ray_intersect_triangle(self: mitsuba.Mesh, index: int, ray: mitsuba.Ray3f, active: bool = True): ...
    def ray_test(self: mitsuba.Shape, ray: mitsuba.Ray3f, active: bool = True) -> bool:
        """
        Fast ray shadow test
        
        Efficiently test whether the shape is intersected by the given ray.
        
        No details about the intersection are returned, hence the function is
        only useful for visibility queries. For most shapes, the
        implementation will simply forward the call to
        ray_intersect_preliminary(). When the shape actually contains a nested
        kd-tree, some optimizations are possible.
        
        Parameter ``ray``:
            The ray to be tested for an intersection
        
        Parameter ``prim_index``:
            Index of the primitive to be intersected
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_direction(self: mitsuba.Shape, it, sample: mitsuba.Point2f, active: bool = True):
        """
        Sample a direction towards this shape with respect to solid angles
        measured at a reference position within the scene
        
        An ideal implementation of this interface would achieve a uniform
        solid angle density within the surface region that is visible from the
        reference position ``it.p`` (though such an ideal implementation is
        usually neither feasible nor advisable due to poor efficiency).
        
        The function returns the sampled position and the inverse probability
        per unit solid angle associated with the sample.
        
        When the Shape subclass does not supply a custom implementation of
        this function, the Shape class reverts to a fallback approach that
        piggybacks on sample_position(). This will generally lead to a
        suboptimal sample placement and higher variance in Monte Carlo
        estimators using the samples.
        
        Parameter ``it``:
            A reference position somewhere within the scene.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``
        
        Returns:
            A DirectionSample instance describing the generated sample
        """
        ...

    def sample_position(self: mitsuba.Shape, time: float, sample: mitsuba.Point2f, active: bool = True):
        """
        Sample a point on the surface of this shape
        
        The sampling strategy is ideally uniform over the surface, though
        implementations are allowed to deviate from a perfectly uniform
        distribution as long as this is reflected in the returned probability
        density.
        
        Parameter ``time``:
            The scene time associated with the position sample
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``
        
        Returns:
            A PositionSample instance describing the generated sample
        """
        ...

    def sample_precomputed_silhouette(self: mitsuba.Shape, viewpoint: mitsuba.Point3f, sample1: int, sample2: float, active: bool = True):
        """
        Samples a boundary segement on the shape's silhouette using
        precomputed information computed in precompute_silhouette.
        
        This method is meant to be used for silhouettes that are shared
        between all threads, as is the case for primarily visible derivatives.
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``viewpoint``:
            The viewpoint that was used for the precomputed silhouette
            information
        
        Parameter ``sample1``:
            A sampled index from the return values of precompute_silhouette
        
        Parameter ``sample2``:
            A uniformly distributed sample in ``[0,1]``
        
        Returns:
            A boundary segment on the silhouette of the shape as seen from
            ``viewpoint``.
        """
        ...

    def sample_silhouette(self: mitsuba.Shape, sample: mitsuba.Point3f, flags: int, active: bool = True):
        """
        Map a point sample in boundary sample space to a silhouette segment
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``sample``:
            The boundary space sample (a point in the unit cube).
        
        Parameter ``flags``:
            Flags to select the type of silhouettes to sample from (see
            DiscontinuityFlags). Only one type of discontinuity can be sampled
            per call.
        
        Returns:
            Silhouette sample record.
        """
        ...

    def sensor(self: mitsuba.Shape):
        """
        Return the area sensor associated with this shape (if any)
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def shape_type(self: mitsuba.Shape) -> int:
        """
        Returns the shape type ShapeType of this shape
        """
        ...

    def silhouette_discontinuity_types(self: mitsuba.Shape) -> int:
        """
        //! @{ \name Silhouette sampling routines and other utilities
        """
        ...

    def silhouette_sampling_weight(self: mitsuba.Shape) -> float:
        """
        Return this shape's sampling weight w.r.t. all shapes in the scene
        """
        ...

    def surface_area(self: mitsuba.Shape) -> float:
        """
        Return the shape's surface area.
        
        The function assumes that the object is not undergoing some kind of
        time-dependent scaling.
        
        The default implementation throws an exception.
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def vertex_count(self: mitsuba.Mesh) -> int:
        """
        Return the total number of vertices
        """
        ...

    def vertex_normal(self: mitsuba.Mesh, index: int, active: bool = True) -> mitsuba.Normal3f:
        """
        Returns the normal direction of the vertex with index ``index``
        """
        ...

    def vertex_position(self: mitsuba.Mesh, index: int, active: bool = True) -> mitsuba.Point3f:
        """
        Returns the world-space position of the vertex with index ``index``
        """
        ...

    def vertex_texcoord(self: mitsuba.Mesh, index: int, active: bool = True) -> mitsuba.Point2f:
        """
        Returns the UV texture coordinates of the vertex with index ``index``
        """
        ...

    @overload
    def write_ply(self: mitsuba.Mesh, filename: str) -> None:
        """
        Write the mesh to a binary PLY file
        
        Parameter ``filename``:
            Target file path on disk
        
        """
        ...

    @overload
    def write_ply(self: mitsuba.Mesh, stream: mitsuba.Stream) -> None:
        """
        Write the mesh encoded in binary PLY format to a stream
        
        Parameter ``stream``:
            Target stream that will receive the encoded output
        """
        ...

    ...

class MicrofacetDistribution:
    """
    Implementation of the Beckman and GGX / Trowbridge-Reitz microfacet
    distributions and various useful sampling routines
    
    Based on the papers
    
    "Microfacet Models for Refraction through Rough Surfaces" by Bruce
    Walter, Stephen R. Marschner, Hongsong Li, and Kenneth E. Torrance
    
    and
    
    "Importance Sampling Microfacet-Based BSDFs using the Distribution of
    Visible Normals" by Eric Heitz and Eugene D'Eon
    
    The visible normal sampling code was provided by Eric Heitz and Eugene
    D'Eon. An improvement of the Beckmann model sampling routine is
    discussed in
    
    "An Improved Visible Normal Sampling Routine for the Beckmann
    Distribution" by Wenzel Jakob
    
    An improvement of the GGX model sampling routine is discussed in "A
    Simpler and Exact Sampling Routine for the GGX Distribution of Visible
    Normals" by Eric Heitz
    """

    @overload
    def __init__(self: mitsuba.MicrofacetDistribution, type: mitsuba.MicrofacetType, alpha: float, sample_visible: bool = True) -> None: ...
    @overload
    def __init__(self: mitsuba.MicrofacetDistribution, type: mitsuba.MicrofacetType, alpha_u: float, alpha_v: float, sample_visible: bool = True) -> None: ...
    @overload
    def __init__(self: mitsuba.MicrofacetDistribution, type: mitsuba.MicrofacetType, alpha: float, sample_visible: bool = True) -> None: ...
    @overload
    def __init__(self: mitsuba.MicrofacetDistribution, type: mitsuba.MicrofacetType, alpha_u: float, alpha_v: float, sample_visible: bool = True) -> None: ...
    @overload
    def __init__(self: mitsuba.MicrofacetDistribution, arg0: mitsuba.Properties) -> None: ...
    def G(self: mitsuba.MicrofacetDistribution, wi: mitsuba.Vector3f, wo: mitsuba.Vector3f, m: mitsuba.Vector3f) -> float:
        """
        Smith's separable shadowing-masking approximation
        """
        ...

    def alpha(self: mitsuba.MicrofacetDistribution) -> float:
        """
        Return the roughness (isotropic case)
        """
        ...

    def alpha_u(self: mitsuba.MicrofacetDistribution) -> float:
        """
        Return the roughness along the tangent direction
        """
        ...

    def alpha_v(self: mitsuba.MicrofacetDistribution) -> float:
        """
        Return the roughness along the bitangent direction
        """
        ...

    def eval(self: mitsuba.MicrofacetDistribution, m: mitsuba.Vector3f) -> float:
        """
        Evaluate the microfacet distribution function
        
        Parameter ``m``:
            The microfacet normal
        """
        ...

    def is_anisotropic(self: mitsuba.MicrofacetDistribution) -> bool:
        """
        Is this an anisotropic microfacet distribution?
        """
        ...

    def is_isotropic(self: mitsuba.MicrofacetDistribution) -> bool:
        """
        Is this an isotropic microfacet distribution?
        """
        ...

    def pdf(self: mitsuba.MicrofacetDistribution, wi: mitsuba.Vector3f, m: mitsuba.Vector3f) -> float:
        """
        Returns the density function associated with the sample() function.
        
        Parameter ``wi``:
            The incident direction (only relevant if visible normal sampling
            is used)
        
        Parameter ``m``:
            The microfacet normal
        """
        ...

    def sample(self: mitsuba.MicrofacetDistribution, wi: mitsuba.Vector3f, sample: mitsuba.Point2f) -> Tuple[mitsuba.Normal3f, float]:
        """
        Draw a sample from the microfacet normal distribution and return the
        associated probability density
        
        Parameter ``wi``:
            The incident direction. Only used if visible normal sampling is
            enabled.
        
        Parameter ``sample``:
            A uniformly distributed 2D sample
        
        Returns:
            A tuple consisting of the sampled microfacet normal and the
            associated solid angle density
        """
        ...

    def sample_visible(self: mitsuba.MicrofacetDistribution) -> bool:
        """
        Return whether or not only visible normals are sampled?
        """
        ...

    def sample_visible_11(self: mitsuba.MicrofacetDistribution, cos_theta_i: float, sample: mitsuba.Point2f) -> mitsuba.Vector2f:
        """
        Visible normal sampling code for the alpha=1 case
        """
        ...

    def scale_alpha(self: mitsuba.MicrofacetDistribution, value: float) -> None:
        """
        Scale the roughness values by some constant
        """
        ...

    def smith_g1(self: mitsuba.MicrofacetDistribution, v: mitsuba.Vector3f, m: mitsuba.Vector3f) -> float:
        """
        Smith's shadowing-masking function for a single direction
        
        Parameter ``v``:
            An arbitrary direction
        
        Parameter ``m``:
            The microfacet normal
        """
        ...

    def type(self: mitsuba.MicrofacetDistribution) -> mitsuba.MicrofacetType:
        """
        Return the distribution type
        """
        ...

    ...

class MicrofacetType:
    """
    Supported normal distribution functions
    
    Members:
    
      Beckmann : Beckmann distribution derived from Gaussian random surfaces
    
      GGX : GGX: Long-tailed distribution for very rough surfaces (aka.
    Trowbridge-Reitz distr.)
    """

    def __init__(self: mitsuba.MicrofacetType, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Beckmann = 0
    """
      Beckmann : Beckmann distribution derived from Gaussian random surfaces
    """
    GGX = 1
    """
      GGX : GGX: Long-tailed distribution for very rough surfaces (aka.
    """

    ...

class MonteCarloIntegrator(SamplingIntegrator):
    """
    Abstract integrator that performs *recursive* Monte Carlo sampling
    starting from the sensor
    
    This class is almost identical to SamplingIntegrator. It stores two
    additional fields that are helpful for recursive Monte Carlo
    techniques: the maximum path depth, and the depth at which the Russian
    Roulette path termination technique should start to become active.
    """

    hide_emitters = ...
    ptr = ...

    def aov_names(self: mitsuba.Integrator) -> List[str]:
        """
        For integrators that return one or more arbitrary output variables
        (AOVs), this function specifies a list of associated channel names.
        The default implementation simply returns an empty vector.
        """
        ...

    def cancel(self: mitsuba.Integrator) -> None:
        """
        Cancel a running render job (e.g. after receiving Ctrl-C)
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function renders the scene from the viewpoint of ``sensor``. All
        other parameters are optional and control different aspects of the
        rendering process. In particular:
        
        Parameter ``seed``:
            This parameter controls the initialization of the random number
            generator. It is crucial that you specify different seeds (e.g.,
            an increasing sequence) if subsequent ``render``() calls should
            produce statistically independent images.
        
        Parameter ``spp``:
            Set this parameter to a nonzero value to override the number of
            samples per pixel. This value then takes precedence over whatever
            was specified in the construction of ``sensor->sampler()``. This
            parameter may be useful in research applications where an image
            must be rendered multiple times using different quality levels.
        
        Parameter ``develop``:
            If set to ``True``, the implementation post-processes the data
            stored in ``sensor->film()``, returning the resulting image as a
            TensorXf. Otherwise, it returns an empty tensor.
        
        Parameter ``evaluate``:
            This parameter is only relevant for JIT variants of Mitsuba (LLVM,
            CUDA). If set to ``True``, the rendering step evaluates the
            generated image and waits for its completion. A log message also
            denotes the rendering time. Otherwise, the returned tensor
            (``develop=true``) or modified film (``develop=false``) represent
            the rendering task as an unevaluated computation graph.
        
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor: int = 0, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function is just a thin wrapper around the previous render()
        overload. It accepts a sensor *index* instead and renders the scene
        using sensor 0 by default.
        """
        ...

    @overload
    def render_backward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, grad_in: mitsuba.TensorXf, sensor, seed: int = 0, spp: int = 0) -> None: ...
    @overload
    def render_backward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, grad_in: mitsuba.TensorXf, sensor: int = 0, seed: int = 0, spp: int = 0) -> None: ...
    @overload
    def render_forward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, sensor, seed: int = 0, spp: int = 0) -> mitsuba.TensorXf: ...
    @overload
    def render_forward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, sensor: int = 0, seed: int = 0, spp: int = 0) -> mitsuba.TensorXf: ...
    def sample(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, sampler, ray: mitsuba.RayDifferential3f, medium: mitsuba.Medium = None, active: bool = True) -> Tuple[mitsuba.Color3f, bool, List[float]]:
        """
        Sample the incident radiance along a ray.
        
        Parameter ``scene``:
            The underlying scene in which the radiance function should be
            sampled
        
        Parameter ``sampler``:
            A source of (pseudo-/quasi-) random numbers
        
        Parameter ``ray``:
            A ray, optionally with differentials
        
        Parameter ``medium``:
            If the ray is inside a medium, this parameter holds a pointer to
            that medium
        
        Parameter ``aov``:
            Integrators may return one or more arbitrary output variables
            (AOVs) via this parameter. If ``nullptr`` is provided to this
            argument, no AOVs should be returned. Otherwise, the caller
            guarantees that space for at least ``aov_names().size()`` entries
            has been allocated.
        
        Parameter ``active``:
            A mask that indicates which SIMD lanes are active
        
        Returns:
            A pair containing a spectrum and a mask specifying whether a
            surface or medium interaction was sampled. False mask entries
            indicate that the ray "escaped" the scene, in which case the the
            returned spectrum contains the contribution of environment maps,
            if present. The mask can be used to estimate a suitable alpha
            channel of a rendered image.
        
        Remark:
            In the Python bindings, this function returns the ``aov`` output
            argument as an additional return value. In other words:
        
        ```
        (spec, mask, aov) = integrator.sample(scene, sampler, ray, medium, active)
        ```
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def should_stop(self: mitsuba.Integrator) -> bool:
        """
        Indicates whether cancel() or a timeout have occurred. Should be
        checked regularly in the integrator's main loop so that timeouts are
        enforced accurately.
        
        Note that accurate timeouts rely on m_render_timer, which needs to be
        reset at the beginning of the rendering phase.
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Normal3d:
    def __init__(self: mitsuba.Normal3d, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Normal3f:
    def __init__(self: mitsuba.Normal3f, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Object:
    """
    Object base class with builtin reference counting
    
    This class (in conjunction with the ``ref`` reference counter)
    constitutes the foundation of an efficient reference-counted object
    hierarchy. The implementation here is an alternative to standard
    mechanisms for reference counting such as ``std::shared_ptr`` from the
    STL.
    
    Why not simply use ``std::shared_ptr``? To be spec-compliant, such
    shared pointers must associate a special record with every instance,
    which stores at least two counters plus a deletion function.
    Allocating this record naturally incurs further overheads to maintain
    data structures within the memory allocator. In addition to this, the
    size of an individual ``shared_ptr`` references is at least two data
    words. All of this quickly adds up and leads to significant overheads
    for large collections of instances, hence the need for an alternative
    in Mitsuba.
    
    In contrast, the ``Object`` class allows for a highly efficient
    implementation that only adds 32 bits to the base object (for the
    counter) and has no overhead for references.
    """

    @overload
    def __init__(self: mitsuba.Object) -> None:
        """
        Default constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Object, arg0: mitsuba.Object) -> None:
        """
        Copy constructor
        """
        ...

    ptr = ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class OptixDenoiser(Object):
    """
    Wrapper for the OptiX AI denoiser
    
    The OptiX AI denoiser is wrapped in this object such that it can work
    directly with Mitsuba types and its conventions.
    
    The denoiser works best when applied to noisy renderings that were
    produced with a Film which used the `box` ReconstructionFilter. With a
    filter that spans multiple pixels, the denoiser might identify some
    local variance as a feature of the scene and will not denoise it.
    """

    def __init__(self: mitsuba.OptixDenoiser, input_size: mitsuba.Vector2u, albedo: bool = False, normals: bool = False, temporal: bool = False) -> None:
        """
        Constructs an OptiX denoiser
        
        Parameter ``input_size``:
            Resolution of noisy images that will be fed to the denoiser.
        
        Parameter ``albedo``:
            Whether or not albedo information will also be given to the
            denoiser.
        
        Parameter ``normals``:
            Whether or not shading normals information will also be given to
            the Denoiser.
        
        Returns:
            A callable object which will apply the OptiX denoiser.
        """
        ...

    @overload
    def __call__(self: mitsuba.OptixDenoiser, noisy: mitsuba.TensorXf, denoise_alpha: bool = True, albedo: mitsuba.TensorXf = [], normals: mitsuba.TensorXf = [], to_sensor: object = None, flow: mitsuba.TensorXf = [], previous_denoised: mitsuba.TensorXf = []) -> mitsuba.TensorXf:
        """
        Apply denoiser on inputs which are TensorXf objects.
        
        Parameter ``noisy``:
            The noisy input. (tensor shape: (width, height, 3 | 4))
        
        Parameter ``denoise_alpha``:
            Whether or not the alpha channel (if specified in the noisy input)
            should be denoised too. This parameter is optional, by default it
            is true.
        
        Parameter ``albedo``:
            Albedo information of the noisy rendering. This parameter is
            optional unless the OptixDenoiser was built with albedo support.
            (tensor shape: (width, height, 3))
        
        Parameter ``normals``:
            Shading normal information of the noisy rendering. The normals
            must be in the coordinate frame of the sensor which was used to
            render the noisy input. This parameter is optional unless the
            OptixDenoiser was built with normals support. (tensor shape:
            (width, height, 3))
        
        Parameter ``to_sensor``:
            A Transform4f which is applied to the ``normals`` parameter before
            denoising. This should be used to transform the normals into the
            correct coordinate frame. This parameter is optional, by default
            no transformation is applied.
        
        Parameter ``flow``:
            With temporal denoising, this parameter is the optical flow
            between the previous frame and the current one. It should capture
            the 2D motion of each individual pixel. When this parameter is
            unknown, it can been set to a zero-initialized TensorXf of the
            correct size and still produce convincing results. This parameter
            is optional unless the OptixDenoiser was built with temporal
            denoising support. (tensor shape: (width, height, 2))
        
        Parameter ``previous_denoised``:
            With temporal denoising, the previous denoised frame should be
            passed here. For the very first frame, the OptiX documentation
            recommends passing the noisy input for this argument. This
            parameter is optional unless the OptixDenoiser was built with
            temporal denoising support. (tensor shape: (width, height, 3 | 4))
        
        Returns:
            The denoised input.
        
        """
        ...

    @overload
    def __call__(self: mitsuba.OptixDenoiser, noisy: mitsuba.Bitmap, denoise_alpha: bool = True, albedo_ch: str = '', normals_ch: str = '', to_sensor: object = None, flow_ch: str = '', previous_denoised_ch: str = '', noisy_ch: str = '<root>') -> mitsuba.Bitmap:
        """
        Apply denoiser on inputs which are Bitmap objects.
        
        Parameter ``noisy``:
            The noisy input. When passing additional information like albedo
            or normals to the denoiser, this Bitmap object must be a
            MultiChannel bitmap.
        
        Parameter ``denoise_alpha``:
            Whether or not the alpha channel (if specified in the noisy input)
            should be denoised too. This parameter is optional, by default it
            is true.
        
        Parameter ``albedo_ch``:
            The name of the channel in the ``noisy`` parameter which contains
            the albedo information of the noisy rendering. This parameter is
            optional unless the OptixDenoiser was built with albedo support.
        
        Parameter ``normals_ch``:
            The name of the channel in the ``noisy`` parameter which contains
            the shading normal information of the noisy rendering. The normals
            must be in the coordinate frame of the sensor which was used to
            render the noisy input. This parameter is optional unless the
            OptixDenoiser was built with normals support.
        
        Parameter ``to_sensor``:
            A Transform4f which is applied to the ``normals`` parameter before
            denoising. This should be used to transform the normals into the
            correct coordinate frame. This parameter is optional, by default
            no transformation is applied.
        
        Parameter ``flow_ch``:
            With temporal denoising, this parameter is name of the channel in
            the ``noisy`` parameter which contains the optical flow between
            the previous frame and the current one. It should capture the 2D
            motion of each individual pixel. When this parameter is unknown,
            it can been set to a zero-initialized TensorXf of the correct size
            and still produce convincing results. This parameter is optional
            unless the OptixDenoiser was built with temporal denoising
            support.
        
        Parameter ``previous_denoised_ch``:
            With temporal denoising, this parameter is name of the channel in
            the ``noisy`` parameter which contains the previous denoised
            frame. For the very first frame, the OptiX documentation
            recommends passing the noisy input for this argument. This
            parameter is optional unless the OptixDenoiser was built with
            temporal denoising support.
        
        Parameter ``noisy_ch``:
            The name of the channel in the ``noisy`` parameter which contains
            the shading normal information of the noisy rendering.
        
        Returns:
            The denoised input.
        """
        ...

    ptr = ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class PCG32:
    @overload
    def __init__(self: mitsuba.PCG32, size: int = 1, initstate: int = 9600629759793949339, initseq: int = 15726070495360670683) -> None: ...
    @overload
    def __init__(self: mitsuba.PCG32, arg0: mitsuba.PCG32) -> None: ...
    inc = ...
    state = ...

    @overload
    def next_float32(self: mitsuba.PCG32) -> float: ...
    @overload
    def next_float32(self: mitsuba.PCG32, arg0: bool) -> float: ...
    @overload
    def next_float64(self: mitsuba.PCG32) -> float: ...
    @overload
    def next_float64(self: mitsuba.PCG32, arg0: bool) -> float: ...
    @overload
    def next_uint32(self: mitsuba.PCG32) -> int: ...
    @overload
    def next_uint32(self: mitsuba.PCG32, arg0: bool) -> int: ...
    def next_uint32_bounded(self: mitsuba.PCG32, bound: int, mask: bool = True) -> int: ...
    @overload
    def next_uint64(self: mitsuba.PCG32) -> int: ...
    @overload
    def next_uint64(self: mitsuba.PCG32, arg0: bool) -> int: ...
    def next_uint64_bounded(self: mitsuba.PCG32, bound: int, mask: bool = True) -> int: ...
    def seed(self: mitsuba.PCG32, size: int = 1, initstate: int = 9600629759793949339, initseq: int = 15726070495360670683) -> None: ...
    ...

class ParamFlags:
    """
    This list of flags is used to classify the different types of
    parameters exposed by the plugins.
    
    For instance, in the context of differentiable rendering, it is
    important to know which parameters can be differentiated, and which of
    those might introduce discontinuities in the Monte Carlo simulation.
    
    Members:
    
      Differentiable : Tracking gradients w.r.t. this parameter is allowed
    
      NonDifferentiable : Tracking gradients w.r.t. this parameter is not allowed
    
      Discontinuous : Tracking gradients w.r.t. this parameter will introduce
    discontinuities
    """

    def __init__(self: mitsuba.ParamFlags, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Differentiable = 0
    """
      Differentiable : Tracking gradients w.r.t. this parameter is allowed
    """
    Discontinuous = 2
    """
      Discontinuous : Tracking gradients w.r.t. this parameter will introduce
    """
    NonDifferentiable = 1
    """
      NonDifferentiable : Tracking gradients w.r.t. this parameter is not allowed
    """

    ...

class PhaseFunction(Object):
    def __init__(self: mitsuba.PhaseFunction, arg0: mitsuba.Properties) -> None: ...
    m_flags = ...
    ptr = ...

    def component_count(self: mitsuba.PhaseFunction, active: bool = True) -> int:
        """
        Number of components this phase function is comprised of.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval_pdf(self: mitsuba.PhaseFunction, ctx: mitsuba.PhaseFunctionContext, mi: mitsuba.MediumInteraction3f, wo: mitsuba.Vector3f, active: bool = True) -> Tuple[mitsuba.Color3f, float]:
        """
        Evaluates the phase function model value and PDF
        
        The function returns the value (which often equals the PDF) of the
        phase function in the query direction.
        
        Parameter ``ctx``:
            A phase function sampling context, contains information about the
            transport mode
        
        Parameter ``mi``:
            A medium interaction data structure describing the underlying
            medium position. The incident direction is obtained from the field
            ``mi.wi``.
        
        Parameter ``wo``:
            An outgoing direction to evaluate.
        
        Returns:
            The value and the sampling PDF of the phase function in direction
            wo
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    @overload
    def flags(self: mitsuba.PhaseFunction, index: int, active: bool = True) -> int:
        """
        Flags for a specific component of this phase function.
        
        """
        ...

    @overload
    def flags(self: mitsuba.PhaseFunction, active: bool = True) -> int:
        """
        Flags for this phase function.
        """
        ...

    def id(self: mitsuba.PhaseFunction) -> str:
        """
        Return a string identifier
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def max_projected_area(self: mitsuba.PhaseFunction) -> float:
        """
        Return the maximum projected area of the microflake distribution
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def projected_area(self: mitsuba.PhaseFunction, mi: mitsuba.MediumInteraction3f, active: bool = True) -> float:
        """
        Returns the microflake projected area
        
        The function returns the projected area of the microflake distribution
        defining the phase function. For non-microflake phase functions, e.g.
        isotropic or Henyey-Greenstein, this should return a value of 1.
        
        Parameter ``mi``:
            A medium interaction data structure describing the underlying
            medium position. The incident direction is obtained from the field
            ``mi.wi``.
        
        Returns:
            The projected area in direction ``mi.wi`` at position ``mi.p``
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample(self: mitsuba.PhaseFunction, ctx: mitsuba.PhaseFunctionContext, mi: mitsuba.MediumInteraction3f, sample1: float, sample2: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.Vector3f, mitsuba.Color3f, float]:
        """
        Importance sample the phase function model
        
        The function returns a sampled direction.
        
        Parameter ``ctx``:
            A phase function sampling context, contains information about the
            transport mode
        
        Parameter ``mi``:
            A medium interaction data structure describing the underlying
            medium position. The incident direction is obtained from the field
            ``mi.wi``.
        
        Parameter ``sample1``:
            A uniformly distributed sample on :math:`[0,1]`. It is used to
            select the phase function component in multi-component models.
        
        Parameter ``sample2``:
            A uniformly distributed sample on :math:`[0,1]^2`. It is used to
            generate the sampled direction.
        
        Returns:
            A sampled direction wo and its corresponding weight and PDF
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class PhaseFunctionContext:
    def __init__(self: mitsuba.PhaseFunctionContext, sampler, mode: mitsuba.TransportMode = TransportMode.Radiance) -> None:
        """
        //! @}
        """
        ...

    component = ...
    mode = ...
    "Transported mode (radiance or importance)"
    sampler = ...
    "Sampler object"
    type_mask = ...

    def reverse(self: mitsuba.PhaseFunctionContext) -> None:
        """
        Reverse the direction of light transport in the record
        
        This updates the transport mode (radiance to importance and vice
        versa).
        """
        ...

    ...

class PhaseFunctionFlags:
    """
    This enumeration is used to classify phase functions into different
    types, i.e. into isotropic, anisotropic and microflake phase
    functions.
    
    This can be used to optimize implementations to for example have less
    overhead if the phase function is not a microflake phase function.
    
    Members:
    
      Empty : 
    
      Isotropic : 
    
      Anisotropic : 
    
      Microflake : 
    """

    def __init__(self: mitsuba.PhaseFunctionFlags, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Anisotropic = 2
    """
      Anisotropic : 
    """
    Empty = 0
    """
      Empty : 
    """
    Isotropic = 1
    """
      Isotropic : 
    """
    Microflake = 4
    """
      Microflake : 
    """

    ...

class PluginManager:
    """
    The object factory is responsible for loading plugin modules and
    instantiating object instances.
    
    Ordinarily, this class will be used by making repeated calls to the
    create_object() methods. The generated instances are then assembled
    into a final object graph, such as a scene. One such examples is the
    SceneHandler class, which parses an XML scene file by essentially
    translating the XML elements into calls to create_object().
    """

    def create_object(self: mitsuba.PluginManager, arg0) -> object:
        """
        Instantiate a plugin, verify its type, and return the newly created
        object instance.
        
        Parameter ``props``:
            A Properties instance containing all information required to find
            and construct the plugin.
        
        Parameter ``class_type``:
            Expected type of the instance. An exception will be thrown if it
            turns out not to derive from this class.
        """
        ...

    def get_plugin_class(self: mitsuba.PluginManager, name: str, variant: str) -> mitsuba.Class:
        """
        Return the class corresponding to a plugin for a specific variant
        """
        ...

    ...

class Point0d:
    def __init__(self: mitsuba.Point0d, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Point0f:
    def __init__(self: mitsuba.Point0f, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Point0i:
    def __init__(self: mitsuba.Point0i, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Point0u:
    def __init__(self: mitsuba.Point0u, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Point1d:
    def __init__(self: mitsuba.Point1d, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Point1f:
    def __init__(self: mitsuba.Point1f, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Point1i:
    def __init__(self: mitsuba.Point1i, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Point1u:
    def __init__(self: mitsuba.Point1u, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Point2d:
    def __init__(self: mitsuba.Point2d, *args) -> None: ...
    label = ...
    x = ...
    y = ...

    def assign(self, other): ...
    ...

class Point2f:
    def __init__(self: mitsuba.Point2f, *args) -> None: ...
    label = ...
    x = ...
    y = ...

    def assign(self, other): ...
    ...

class Point2i:
    def __init__(self: mitsuba.Point2i, *args) -> None: ...
    label = ...
    x = ...
    y = ...

    def assign(self, other): ...
    ...

class Point2u:
    def __init__(self: mitsuba.Point2u, *args) -> None: ...
    label = ...
    x = ...
    y = ...

    def assign(self, other): ...
    ...

class Point3d:
    def __init__(self: mitsuba.Point3d, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Point3f:
    def __init__(self: mitsuba.Point3f, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Point3i:
    def __init__(self: mitsuba.Point3i, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Point3u:
    def __init__(self: mitsuba.Point3u, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Point4d:
    def __init__(self: mitsuba.Point4d, *args) -> None: ...
    label = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Point4f:
    def __init__(self: mitsuba.Point4f, *args) -> None: ...
    label = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Point4i:
    def __init__(self: mitsuba.Point4i, *args) -> None: ...
    label = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Point4u:
    def __init__(self: mitsuba.Point4u, *args) -> None: ...
    label = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class PositionSample3f:
    """
    Generic sampling record for positions
    
    This sampling record is used to implement techniques that draw a
    position from a point, line, surface, or volume domain in 3D and
    furthermore provide auxiliary information about the sample.
    
    Apart from returning the position and (optionally) the surface normal,
    the responsible sampling method must annotate the record with the
    associated probability density and delta.
    """

    @overload
    def __init__(self: mitsuba.PositionSample3f) -> None:
        """
        Construct an uninitialized position sample
        
        """
        ...

    @overload
    def __init__(self: mitsuba.PositionSample3f, other: mitsuba.PositionSample3f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.PositionSample3f, si: mitsuba.SurfaceInteraction3f) -> None:
        """
        Create a position sampling record from a surface intersection
        
        This is useful to determine the hypothetical sampling density on a
        surface after hitting it using standard ray tracing. This happens for
        instance in path tracing with multiple importance sampling.
        """
        ...

    delta = ...
    """
    Set if the sample was drawn from a degenerate (Dirac delta)
    distribution
    """
    n = ...
    "Sampled surface normal (if applicable)"
    p = ...
    "Sampled position"
    pdf = ...
    "Probability density at the sample"
    time = ...
    "Associated time value"
    uv = ...
    """
    Optional: 2D sample position associated with the record
    
    In some uses of this record, a sampled position may be associated with
    an important 2D quantity, such as the texture coordinates on a
    triangle mesh or a position on the aperture of a sensor. When
    applicable, such positions are stored in the ``uv`` attribute.
    """

    def assign(self: mitsuba.PositionSample3f, arg0: mitsuba.PositionSample3f) -> None: ...
    ...

class PreliminaryIntersection3f:
    """
    Stores preliminary information related to a ray intersection
    
    This data structure is used as return type for the
    Shape::ray_intersect_preliminary efficient ray intersection routine.
    It stores whether the shape is intersected by a given ray, and cache
    preliminary information about the intersection if that is the case.
    
    If the intersection is deemed relevant, detailed intersection
    information can later be obtained via the create_surface_interaction()
    method.
    """

    @overload
    def __init__(self: mitsuba.PreliminaryIntersection3f) -> None:
        """
        //! @}
        
        """
        ...

    @overload
    def __init__(self: mitsuba.PreliminaryIntersection3f, arg0: mitsuba.PreliminaryIntersection3f) -> None:
        """
        Copy constructor
        """
        ...

    instance = ...
    "Stores a pointer to the parent instance (if applicable)"
    prim_index = ...
    "Primitive index, e.g. the triangle ID (if applicable)"
    prim_uv = ...
    "2D coordinates on the primitive surface parameterization"
    shape = ...
    "Pointer to the associated shape"
    shape_index = ...
    "Shape index, e.g. the shape ID in shapegroup (if applicable)"
    t = ...
    "Distance traveled along the ray"

    def assign(self: mitsuba.PreliminaryIntersection3f, arg0: mitsuba.PreliminaryIntersection3f) -> None: ...
    def compute_surface_interaction(self: mitsuba.PreliminaryIntersection3f, ray: mitsuba.Ray3f, ray_flags: int = 14, active: bool = True) -> mitsuba.SurfaceInteraction3f:
        """
        Compute and return detailed information related to a surface
        interaction
        
        Parameter ``ray``:
            Ray associated with the ray intersection
        
        Parameter ``ray_flags``:
            Flags specifying which information should be computed
        
        Returns:
            A data structure containing the detailed information
        """
        ...

    def is_valid(self: mitsuba.PreliminaryIntersection3f) -> bool:
        """
        Is the current interaction valid?
        """
        ...

    ...

class ProjectiveCamera(Sensor):
    """
    Projective camera interface
    
    This class provides an abstract interface to several types of sensors
    that are commonly used in computer graphics, such as perspective and
    orthographic camera models.
    
    The interface is meant to be implemented by any kind of sensor, whose
    world to clip space transformation can be explained using only linear
    operations on homogeneous coordinates.
    
    A useful feature of ProjectiveCamera sensors is that their view can be
    rendered using the traditional OpenGL pipeline.
    """

    m_film = ...
    m_needs_sample_2 = ...
    m_needs_sample_3 = ...
    ptr = ...

    def bbox(self: mitsuba.Endpoint) -> mitsuba.BoundingBox3f:
        """
        Return an axis-aligned box bounding the spatial extents of the emitter
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.Sensor, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Given a ray-surface intersection, return the emitted radiance or
        importance traveling along the reverse direction
        
        This function is e.g. used when an area light source has been hit by a
        ray in a path tracing-style integrator, and it subsequently needs to
        be queried for the emitted radiance along the negative ray direction.
        The default implementation throws an exception, which states that the
        method is not implemented.
        
        Parameter ``si``:
            An intersect record that specifies both the query position and
            direction (using the ``si.wi`` field)
        
        Returns:
            The emitted radiance or importance
        """
        ...

    def eval_direction(self: mitsuba.Sensor, it: mitsuba.Interaction3f, ds: mitsuba.DirectionSample3f, active: bool = True) -> mitsuba.Color3f:
        """
        Re-evaluate the incident direct radiance/importance of the
        sample_direction() method.
        
        This function re-evaluates the incident direct radiance or importance
        and sample probability due to the endpoint so that division by
        ``ds.pdf`` equals the sampling weight returned by sample_direction().
        This may appear redundant, and indeed such a function would not find
        use in "normal" rendering algorithms.
        
        However, the ability to re-evaluate the contribution of a generated
        sample is important for differentiable rendering. For example, we
        might want to track derivatives in the sampled direction (``ds.d``)
        without also differentiating the sampling technique.
        
        In contrast to pdf_direction(), evaluating this function can yield a
        nonzero result in the case of emission profiles containing a Dirac
        delta term (e.g. point or directional lights).
        
        Parameter ``ref``:
            A 3D reference location within the scene, which may influence the
            sampling process.
        
        Parameter ``ds``:
            A direction sampling record, which specifies the query location.
        
        Returns:
            The incident direct radiance/importance associated with the
            sample.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def far_clip(self: mitsuba.ProjectiveCamera) -> float:
        """
        Return the far clip plane distance
        """
        ...

    def film(self: mitsuba.Sensor) -> mitsuba.Film:
        """
        Return the Film instance associated with this sensor
        """
        ...

    def focus_distance(self: mitsuba.ProjectiveCamera) -> float:
        """
        Return the distance to the focal plane
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def medium(self: mitsuba.Endpoint) -> mitsuba.Medium:
        """
        Return a pointer to the medium that surrounds the emitter
        """
        ...

    def near_clip(self: mitsuba.ProjectiveCamera) -> float:
        """
        Return the near clip plane distance
        """
        ...

    def needs_aperture_sample(self: mitsuba.Sensor) -> bool:
        """
        Does the sampling technique require a sample for the aperture
        position?
        """
        ...

    def needs_sample_2(self: mitsuba.Endpoint) -> bool:
        """
        Does the method sample_ray() require a uniformly distributed 2D sample
        for the ``sample2`` parameter?
        """
        ...

    def needs_sample_3(self: mitsuba.Endpoint) -> bool:
        """
        Does the method sample_ray() require a uniformly distributed 2D sample
        for the ``sample3`` parameter?
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def pdf_direction(self: mitsuba.Sensor, it: mitsuba.Interaction3f, ds: mitsuba.DirectionSample3f, active: bool = True) -> float:
        """
        Evaluate the probability density of the *direct* sampling method
        implemented by the sample_direction() method.
        
        The returned probability will always be zero when the
        emission/sensitivity profile contains a Dirac delta term (e.g. point
        or directional emitters/sensors).
        
        Parameter ``ds``:
            A direct sampling record, which specifies the query location.
        """
        ...

    def pdf_position(self: mitsuba.Sensor, ps: mitsuba.PositionSample3f, active: bool = True) -> float:
        """
        Evaluate the probability density of the position sampling method
        implemented by sample_position().
        
        In simple cases, this will be the reciprocal of the endpoint's surface
        area.
        
        Parameter ``ps``:
            The sampled position record.
        
        Returns:
            The corresponding sampling density.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_direction(self: mitsuba.Sensor, it: mitsuba.Interaction3f, sample: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.DirectionSample3f, mitsuba.Color3f]:
        """
        Given a reference point in the scene, sample a direction from the
        reference point towards the endpoint (ideally proportional to the
        emission/sensitivity profile)
        
        This operation is a generalization of direct illumination techniques
        to both emitters *and* sensors. A direction sampling method is given
        an arbitrary reference position in the scene and samples a direction
        from the reference point towards the endpoint (ideally proportional to
        the emission/sensitivity profile). This reduces the sampling domain
        from 4D to 2D, which often enables the construction of smarter
        specialized sampling techniques.
        
        Ideally, the implementation should importance sample the product of
        the emission profile and the geometry term between the reference point
        and the position on the endpoint.
        
        The default implementation throws an exception.
        
        Parameter ``ref``:
            A reference position somewhere within the scene.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``.
        
        Returns:
            A DirectionSample instance describing the generated sample along
            with a spectral importance weight.
        """
        ...

    def sample_position(self: mitsuba.Sensor, time: float, sample: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.PositionSample3f, float]:
        """
        Importance sample the spatial component of the emission or importance
        profile of the endpoint.
        
        The default implementation throws an exception.
        
        Parameter ``time``:
            The scene time associated with the position to be sampled.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``.
        
        Returns:
            A PositionSample instance describing the generated sample along
            with an importance weight.
        """
        ...

    def sample_ray(self: mitsuba.Sensor, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.Ray3f, mitsuba.Color3f]:
        """
        Importance sample a ray proportional to the endpoint's
        sensitivity/emission profile.
        
        The endpoint profile is a six-dimensional quantity that depends on
        time, wavelength, surface position, and direction. This function takes
        a given time value and five uniformly distributed samples on the
        interval [0, 1] and warps them so that the returned ray follows the
        profile. Any discrepancies between ideal and actual sampled profile
        are absorbed into a spectral importance weight that is returned along
        with the ray.
        
        Parameter ``time``:
            The scene time associated with the ray to be sampled
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the emission profile.
        
        Parameter ``sample2``:
            A uniformly distributed sample on the domain ``[0,1]^2``. For
            sensor endpoints, this argument corresponds to the sample position
            in fractional pixel coordinates relative to the crop window of the
            underlying film. This argument is ignored if ``needs_sample_2() ==
            false``.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``. For
            sensor endpoints, this argument determines the position on the
            aperture of the sensor. This argument is ignored if
            ``needs_sample_3() == false``.
        
        Returns:
            The sampled ray and (potentially spectrally varying) importance
            weights. The latter account for the difference between the profile
            and the actual used sampling density function.
        """
        ...

    @overload
    def sample_ray_differential(self: mitsuba.Sensor, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.RayDifferential3f, mitsuba.Color3f]:
        """
        Importance sample a ray differential proportional to the sensor's
        sensitivity profile.
        
        The sensor profile is a six-dimensional quantity that depends on time,
        wavelength, surface position, and direction. This function takes a
        given time value and five uniformly distributed samples on the
        interval [0, 1] and warps them so that the returned ray the profile.
        Any discrepancies between ideal and actual sampled profile are
        absorbed into a spectral importance weight that is returned along with
        the ray.
        
        In contrast to Endpoint::sample_ray(), this function returns
        differentials with respect to the X and Y axis in screen space.
        
        Parameter ``time``:
            The scene time associated with the ray_differential to be sampled
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the sensitivity profile.
        
        Parameter ``sample2``:
            This argument corresponds to the sample position in fractional
            pixel coordinates relative to the crop window of the underlying
            film.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``. This
            argument determines the position on the aperture of the sensor.
            This argument is ignored if ``needs_sample_3() == false``.
        
        Returns:
            The sampled ray differential and (potentially spectrally varying)
            importance weights. The latter account for the difference between
            the sensor profile and the actual used sampling density function.
        
        """
        ...

    @overload
    def sample_ray_differential(self: mitsuba.Sensor, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.RayDifferential3f, mitsuba.Color3f]:
        """
        Importance sample a ray differential proportional to the sensor's
        sensitivity profile.
        
        The sensor profile is a six-dimensional quantity that depends on time,
        wavelength, surface position, and direction. This function takes a
        given time value and five uniformly distributed samples on the
        interval [0, 1] and warps them so that the returned ray the profile.
        Any discrepancies between ideal and actual sampled profile are
        absorbed into a spectral importance weight that is returned along with
        the ray.
        
        In contrast to Endpoint::sample_ray(), this function returns
        differentials with respect to the X and Y axis in screen space.
        
        Parameter ``time``:
            The scene time associated with the ray_differential to be sampled
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the sensitivity profile.
        
        Parameter ``sample2``:
            This argument corresponds to the sample position in fractional
            pixel coordinates relative to the crop window of the underlying
            film.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``. This
            argument determines the position on the aperture of the sensor.
            This argument is ignored if ``needs_sample_3() == false``.
        
        Returns:
            The sampled ray differential and (potentially spectrally varying)
            importance weights. The latter account for the difference between
            the sensor profile and the actual used sampling density function.
        """
        ...

    def sample_wavelengths(self: mitsuba.Sensor, si: mitsuba.SurfaceInteraction3f, sample: float, active: bool = True) -> Tuple[mitsuba.Color0f, mitsuba.Color3f]:
        """
        Importance sample a set of wavelengths according to the endpoint's
        sensitivity/emission spectrum.
        
        This function takes a uniformly distributed 1D sample and generates a
        sample that is approximately distributed according to the endpoint's
        spectral sensitivity/emission profile.
        
        For this, the input 1D sample is first replicated into
        ``Spectrum::Size`` separate samples using simple arithmetic
        transformations (see math::sample_shifted()), which can be interpreted
        as a type of Quasi-Monte-Carlo integration scheme. Following this, a
        standard technique (e.g. inverse transform sampling) is used to find
        the corresponding wavelengths. Any discrepancies between ideal and
        actual sampled profile are absorbed into a spectral importance weight
        that is returned along with the wavelengths.
        
        This function should not be called in RGB or monochromatic modes.
        
        Parameter ``si``:
            In the case of a spatially-varying spectral sensitivity/emission
            profile, this parameter conditions sampling on a specific spatial
            position. The ``si.uv`` field must be specified in this case.
        
        Parameter ``sample``:
            A 1D uniformly distributed random variate
        
        Returns:
            The set of sampled wavelengths and (potentially spectrally
            varying) importance weights. The latter account for the difference
            between the profile and the actual used sampling density function.
            In the case of emitters, the weight will include the emitted
            radiance.
        """
        ...

    def sampler(self: mitsuba.Sensor) -> mitsuba.Sampler:
        """
        Return the sensor's sample generator
        
        This is the *root* sampler, which will later be forked a number of
        times to provide each participating worker thread with its own
        instance (see Scene::sampler()). Therefore, this sampler should never
        be used for anything except creating forks.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_medium(self: mitsuba.Endpoint, medium: mitsuba.Medium) -> None:
        """
        Set the medium that surrounds the emitter.
        """
        ...

    def set_scene(self: mitsuba.Endpoint, scene: mitsuba.Scene) -> None:
        """
        Inform the emitter about the properties of the scene
        
        Various emitters that surround the scene (e.g. environment emitters)
        must be informed about the scene dimensions to operate correctly. This
        function is invoked by the Scene constructor.
        """
        ...

    def set_shape(self: mitsuba.Endpoint, shape: mitsuba.Shape) -> None:
        """
        Set the shape associated with this endpoint.
        """
        ...

    def shape(self: mitsuba.Sensor) -> mitsuba.Shape:
        """
        Return the shape, to which the emitter is currently attached
        """
        ...

    def shutter_open(self: mitsuba.Sensor) -> float:
        """
        Return the time value of the shutter opening event
        """
        ...

    def shutter_open_time(self: mitsuba.Sensor) -> float:
        """
        Return the length, for which the shutter remains open
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def world_transform(self: mitsuba.Endpoint) -> mitsuba.Transform4f:
        """
        Return the local space to world space transformation
        """
        ...

    ...

class Properties:
    """
    Associative parameter map for constructing subclasses of Object.
    
    Note that the Python bindings for this class do not implement the
    various type-dependent getters and setters. Instead, they are accessed
    just like a normal Python map, e.g:
    
    ```
    myProps = mitsuba.core.Properties("plugin_name")
    myProps["stringProperty"] = "hello"
    myProps["spectrumProperty"] = mitsuba.core.Spectrum(1.0)
    ```
    
    or using the ``get(key, default)`` method.
    """

    @overload
    def __init__(self: mitsuba.Properties) -> None:
        """
        Construct an empty property container
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Properties, arg0: str) -> None:
        """
        Construct an empty property container with a specific plugin name
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Properties, arg0: mitsuba.Properties) -> None:
        """
        Copy constructor
        """
        ...

    class Type:
        """
        Members:
        
          Bool
        
          Long
        
          Float
        
          Array3f
        
          Transform3f
        
          Transform4f
        
          TensorHandle
        
          Color
        
          String
        
          NamedReference
        
          Object
        
          Pointer
        """

        def __init__(self: mitsuba.Properties.Type, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        Array3f = 3
        """
          Array3f
        """
        Bool = 0
        """
          Bool
        """
        Color = 8
        """
          Color
        """
        Float = 2
        """
          Float
        """
        Long = 1
        """
          Long
        """
        NamedReference = 10
        """
          NamedReference
        """
        Object = 11
        """
          Object
        """
        Pointer = 12
        """
          Pointer
        """
        String = 9
        """
          String
        """
        TensorHandle = 4
        """
          TensorHandle
        """
        Transform3f = 5
        """
          Transform3f
        """
        Transform4f = 6
        """
          Transform4f
        """

        ...

    def as_string(self: mitsuba.Properties, arg0: str) -> str:
        """
        Return one of the parameters (converting it to a string if necessary)
        """
        ...

    def copy_attribute(self: mitsuba.Properties, arg0: mitsuba.Properties, arg1: str, arg2: str) -> None:
        """
        Copy a single attribute from another Properties object and potentially
        rename it
        """
        ...

    def get(self: mitsuba.Properties, key: str, def_value: object = None) -> object:
        """
        Return the value for the specified key it exists, otherwise return default value
        """
        ...

    def has_property(self: mitsuba.Properties, arg0: str) -> bool:
        """
        Verify if a value with the specified name exists
        """
        ...

    def id(self: mitsuba.Properties) -> str:
        """
        Returns a unique identifier associated with this instance (or an empty
        string)
        """
        ...

    def mark_queried(self: mitsuba.Properties, arg0: str) -> bool:
        """
        Manually mark a certain property as queried
        
        Returns:
            ``True`` upon success
        """
        ...

    def merge(self: mitsuba.Properties, arg0: mitsuba.Properties) -> None:
        """
        Merge another properties record into the current one.
        
        Existing properties will be overwritten with the values from ``props``
        if they have the same name.
        """
        ...

    def named_references(self: mitsuba.Properties) -> List[Tuple[str, str]]: ...
    def plugin_name(self: mitsuba.Properties) -> str:
        """
        Get the associated plugin name
        """
        ...

    def property_names(self: mitsuba.Properties) -> List[str]:
        """
        Return an array containing the names of all stored properties
        """
        ...

    def remove_property(self: mitsuba.Properties, arg0: str) -> bool:
        """
        Remove a property with the specified name
        
        Returns:
            ``True`` upon success
        """
        ...

    def set_id(self: mitsuba.Properties, arg0: str) -> None:
        """
        Set the unique identifier associated with this instance
        """
        ...

    def set_plugin_name(self: mitsuba.Properties, arg0: str) -> None:
        """
        Set the associated plugin name
        """
        ...

    def string(self: mitsuba.Properties, arg0: str, arg1: str) -> object:
        """
        Retrieve a string value (use default value if no entry exists)
        """
        ...

    def type(self: mitsuba.Properties, arg0: str):
        """
        Returns the type of an existing property. If no property exists under
        that name, an error is logged and type ``void`` is returned.
        """
        ...

    def unqueried(self: mitsuba.Properties) -> List[str]:
        """
        Return the list of un-queried attributed
        """
        ...

    def was_queried(self: mitsuba.Properties, arg0: str) -> bool:
        """
        Check if a certain property was queried
        """
        ...

    ...

class PyObjectWrapper:
    def __init__(self: mitsuba.PyObjectWrapper, arg0: object) -> None: ...
    ...

class Quaternion4f64:
    def __init__(self: mitsuba.Quaternion4f64, *args) -> None: ...
    imag = ...
    label = ...
    real = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Quaternion4f:
    def __init__(self: mitsuba.Quaternion4f, *args) -> None: ...
    imag = ...
    label = ...
    real = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class RadicalInverse(Object):
    """
    Efficient implementation of a radical inverse function with prime
    bases including scrambled versions.
    
    This class is used to implement Halton and Hammersley sequences for
    QMC integration in Mitsuba.
    """

    def __init__(self: mitsuba.RadicalInverse, max_base: int = 8161, scramble: int = -1) -> None: ...
    ptr = ...

    def base(self: mitsuba.RadicalInverse, arg0: int) -> int:
        """
        Returns the n-th prime base used by the sequence
        
        These prime numbers are used as bases in the radical inverse function
        implementation.
        """
        ...

    def bases(self: mitsuba.RadicalInverse) -> int:
        """
        Return the number of prime bases for which precomputed tables are
        available
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.RadicalInverse, base_index: int, index: int) -> float:
        """
        Calculate the radical inverse function
        
        This function is used as a building block to construct Halton and
        Hammersley sequences. Roughly, it computes a b-ary representation of
        the input value ``index``, mirrors it along the decimal point, and
        returns the resulting fractional value. The implementation here uses
        prime numbers for ``b``.
        
        Parameter ``base_index``:
            Selects the n-th prime that is used as a base when computing the
            radical inverse function (0 corresponds to 2, 1->3, 2->5, etc.).
            The value specified here must be between 0 and 1023.
        
        Parameter ``index``:
            Denotes the index that should be mapped through the radical
            inverse function
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def inverse_permutation(self: mitsuba.RadicalInverse, arg0: int) -> int:
        """
        Return the inverse permutation corresponding to the given prime number
        basis
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def permutation(self: object, arg0: int) -> numpy.ndarray[numpy.uint16]:
        """
        Return the permutation corresponding to the given prime number basis
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def scramble(self: mitsuba.RadicalInverse) -> int:
        """
        Return the original scramble value
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Ray2f:
    """
    Simple n-dimensional ray segment data structure
    
    Along with the ray origin and direction, this data structure
    additionally stores a maximum ray position ``maxt``, a time value
    ``time`` as well a the wavelength information associated with the ray.
    """

    @overload
    def __init__(self: mitsuba.Ray2f) -> None:
        """
        Create an uninitialized ray
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Ray2f, other: mitsuba.Ray2f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Ray2f, o: mitsuba.Point2f, d: mitsuba.Vector2f, time: float = 0.0, wavelengths: mitsuba.Color0f = []) -> None:
        """
        Construct a new ray (o, d) with time
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Ray2f, o: mitsuba.Point2f, d: mitsuba.Vector2f, maxt: float, time: float, wavelengths: mitsuba.Color0f) -> None:
        """
        Construct a new ray (o, d) with bounds
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Ray2f, other: mitsuba.Ray2f, maxt: float) -> None:
        """
        Copy a ray, but change the maxt value
        """
        ...

    def __call__(self: mitsuba.Ray2f, t: float) -> mitsuba.Point2f:
        """
        Return the position of a point along the ray
        """
        ...

    d = ...
    "Ray direction"
    maxt = ...
    "Maximum position on the ray segment"
    o = ...
    "Ray origin"
    time = ...
    "Time value associated with this ray"
    wavelengths = ...
    "Wavelength associated with the ray"

    def assign(self: mitsuba.Ray2f, arg0: mitsuba.Ray2f) -> None: ...
    ...

class Ray3f:
    """
    Simple n-dimensional ray segment data structure
    
    Along with the ray origin and direction, this data structure
    additionally stores a maximum ray position ``maxt``, a time value
    ``time`` as well a the wavelength information associated with the ray.
    """

    @overload
    def __init__(self: mitsuba.Ray3f) -> None:
        """
        Create an uninitialized ray
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Ray3f, other: mitsuba.Ray3f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Ray3f, o: mitsuba.Point3f, d: mitsuba.Vector3f, time: float = 0.0, wavelengths: mitsuba.Color0f = []) -> None:
        """
        Construct a new ray (o, d) with time
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Ray3f, o: mitsuba.Point3f, d: mitsuba.Vector3f, maxt: float, time: float, wavelengths: mitsuba.Color0f) -> None:
        """
        Construct a new ray (o, d) with bounds
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Ray3f, other: mitsuba.Ray3f, maxt: float) -> None:
        """
        Copy a ray, but change the maxt value
        """
        ...

    def __call__(self: mitsuba.Ray3f, t: float) -> mitsuba.Point3f:
        """
        Return the position of a point along the ray
        """
        ...

    d = ...
    "Ray direction"
    maxt = ...
    "Maximum position on the ray segment"
    o = ...
    "Ray origin"
    time = ...
    "Time value associated with this ray"
    wavelengths = ...
    "Wavelength associated with the ray"

    def assign(self: mitsuba.Ray3f, arg0: mitsuba.Ray3f) -> None: ...
    ...

class RayDifferential3f(Ray3f):
    """
    Ray differential -- enhances the basic ray class with offset rays for
    two adjacent pixels on the view plane
    """

    @overload
    def __init__(self: mitsuba.RayDifferential3f) -> None:
        """
        Create an uninitialized ray
        
        """
        ...

    @overload
    def __init__(self: mitsuba.RayDifferential3f, ray: mitsuba.Ray3f) -> None: ...
    @overload
    def __init__(self: mitsuba.RayDifferential3f, o: mitsuba.Point3f, d: mitsuba.Vector3f, time: float = 0.0, wavelengths: mitsuba.Color0f = []) -> None:
        """
        Initialize without differentials.
        """
        ...

    def __call__(self: mitsuba.Ray3f, t: float) -> mitsuba.Point3f:
        """
        Return the position of a point along the ray
        """
        ...

    d = ...
    "Ray direction"
    d_x = ...
    d_y = ...
    has_differentials = ...
    maxt = ...
    "Maximum position on the ray segment"
    o = ...
    "Ray origin"
    o_x = ...
    o_y = ...
    time = ...
    "Time value associated with this ray"
    wavelengths = ...
    "Wavelength associated with the ray"

    def assign(self: mitsuba.RayDifferential3f, arg0: mitsuba.RayDifferential3f) -> None: ...
    def scale_differential(self: mitsuba.RayDifferential3f, amount: float) -> None: ...
    ...

class RayFlags:
    """
    Members:
    
      Empty : No flags set
    
      Minimal : Compute position and geometric normal
    
      UV : Compute UV coordinates
    
      dPdUV : Compute position partials wrt. UV coordinates
    
      dNGdUV : Compute the geometric normal partials wrt. the UV coordinates
    
      dNSdUV : Compute the shading normal partials wrt. the UV coordinates
    
      ShadingFrame : Compute shading normal and shading frame
    
      FollowShape : Derivatives of the SurfaceInteraction fields follow shape's motion
    
      DetachShape : Derivatives of the SurfaceInteraction fields ignore shape's motion
    
      All : //! Compound compute flags
    
      AllNonDifferentiable : Compute all fields of the surface interaction ignoring shape's motion
    """

    def __init__(self: mitsuba.RayFlags, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    All = 14
    """
      All : //! Compound compute flags
      AllNonDifferentiable : Compute all fields of the surface interaction ignoring shape's motion
    """
    AllNonDifferentiable = 270
    """
      AllNonDifferentiable : Compute all fields of the surface interaction ignoring shape's motion
    """
    DetachShape = 256
    """
      DetachShape : Derivatives of the SurfaceInteraction fields ignore shape's motion
    """
    Empty = 0
    """
      Empty : No flags set
    """
    FollowShape = 128
    """
      FollowShape : Derivatives of the SurfaceInteraction fields follow shape's motion
    """
    Minimal = 1
    """
      Minimal : Compute position and geometric normal
    """
    ShadingFrame = 8
    """
      ShadingFrame : Compute shading normal and shading frame
    """
    UV = 2
    """
      UV : Compute UV coordinates
    """
    dNGdUV = 16
    """
      dNGdUV : Compute the geometric normal partials wrt. the UV coordinates
    """
    dNSdUV = 32
    """
      dNSdUV : Compute the shading normal partials wrt. the UV coordinates
    """
    dPdUV = 4
    """
      dPdUV : Compute position partials wrt. UV coordinates
    """

    ...

class Resampler:
    """
    Utility class for efficiently resampling discrete datasets to
    different resolutions
    
    Template parameter ``Scalar``:
        Denotes the underlying floating point data type (i.e. ``half``,
        ``float``, or ``double``)
    """

    def __init__(self: mitsuba.Resampler, rfilter, source_res: int, target_res: int) -> None:
        """
        Create a new Resampler object that transforms between the specified
        resolutions
        
        This constructor precomputes all information needed to efficiently
        perform the desired resampling operation. For that reason, it is most
        efficient if it can be used over and over again (e.g. to resample the
        equal-sized rows of a bitmap)
        
        Parameter ``source_res``:
            Source resolution
        
        Parameter ``target_res``:
            Desired target resolution
        """
        ...

    def boundary_condition(self: mitsuba.Resampler) -> mitsuba.FilterBoundaryCondition:
        """
        Return the boundary condition that should be used when looking up
        samples outside of the defined input domain
        """
        ...

    def clamp(self: mitsuba.Resampler) -> Tuple[float, float]:
        """
        Returns the range to which resampled values will be clamped
        
        The default is -infinity to infinity (i.e. no clamping is used)
        """
        ...

    def resample(self: mitsuba.Resampler, source: numpy.ndarray[numpy.float32], source_stride: int, target: numpy.ndarray[numpy.float32], target_stride: int, channels: int) -> None:
        """
        Resample a multi-channel array and clamp the results to a specified
        valid range
        
        Parameter ``source``:
            Source array of samples
        
        Parameter ``target``:
            Target array of samples
        
        Parameter ``source_stride``:
            Stride of samples in the source array. A value of '1' implies that
            they are densely packed.
        
        Parameter ``target_stride``:
            Stride of samples in the source array. A value of '1' implies that
            they are densely packed.
        
        Parameter ``channels``:
            Number of channels to be resampled
        """
        ...

    def set_boundary_condition(self: mitsuba.Resampler, arg0: mitsuba.FilterBoundaryCondition) -> None:
        """
        Set the boundary condition that should be used when looking up samples
        outside of the defined input domain
        
        The default is FilterBoundaryCondition::Clamp
        """
        ...

    def set_clamp(self: mitsuba.Resampler, arg0: Tuple[float, float]) -> None:
        """
        If specified, resampled values will be clamped to the given range
        """
        ...

    def source_resolution(self: mitsuba.Resampler) -> int:
        """
        Return the reconstruction filter's source resolution
        """
        ...

    def taps(self: mitsuba.Resampler) -> int:
        """
        Return the number of taps used by the reconstruction filter
        """
        ...

    def target_resolution(self: mitsuba.Resampler) -> int:
        """
        Return the reconstruction filter's target resolution
        """
        ...

    ...

class Sampler(Object):
    """
    Base class of all sample generators.
    
    A *sampler* provides a convenient abstraction around methods that
    generate uniform pseudo- or quasi-random points within a conceptual
    infinite-dimensional unit hypercube \f$[0,1]^\infty$\f. This involves
    two main operations: by querying successive component values of such
    an infinite-dimensional point (next_1d(), next_2d()), or by discarding
    the current point and generating another one (advance()).
    
    Scalar and vectorized rendering algorithms interact with the sampler
    interface in a slightly different way:
    
    Scalar rendering algorithm:
    
    1. The rendering algorithm first invokes seed() to initialize the
    sampler state.
    
    2. The first pixel sample can now be computed, after which advance()
    needs to be invoked. This repeats until all pixel samples have been
    generated. Note that some implementations need to be configured for a
    certain number of pixel samples, and exceeding these will lead to an
    exception being thrown.
    
    3. While computing a pixel sample, the rendering algorithm usually
    requests 1D or 2D component blocks using the next_1d() and next_2d()
    functions before moving on to the next sample.
    
    A vectorized rendering algorithm effectively queries multiple sample
    generators that advance in parallel. This involves the following
    steps:
    
    1. The rendering algorithm invokes set_samples_per_wavefront() if each
    rendering step is split into multiple passes (in which case fewer
    samples should be returned per sample_1d() or sample_2d() call).
    
    2. The rendering algorithm then invokes seed() to initialize the
    sampler state, and to inform the sampler of the wavefront size, i.e.,
    how many sampler evaluations should be performed in parallel,
    accounting for all passes. The initialization ensures that the set of
    parallel samplers is mutually statistically independent (in a
    pseudo/quasi-random sense).
    
    3. advance() can be used to advance to the next point.
    
    4. As in the scalar approach, the rendering algorithm can request
    batches of (pseudo-) random numbers using the next_1d() and next_2d()
    functions.
    """

    def __init__(self: mitsuba.Sampler, props: mitsuba.Properties) -> None: ...
    ptr = ...

    def advance(self: mitsuba.Sampler) -> None:
        """
        Advance to the next sample.
        
        A subsequent call to ``next_1d`` or ``next_2d`` will access the first
        1D or 2D components of this sample.
        """
        ...

    def clone(self: mitsuba.Sampler) -> mitsuba.Sampler:
        """
        Create a clone of this sampler.
        
        Subsequent calls to the cloned sampler will produce the same random
        numbers as the original sampler.
        
        Remark:
            This method relies on the overload of the copy constructor.
        
        May throw an exception if not supported.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def fork(self: mitsuba.Sampler) -> mitsuba.Sampler:
        """
        Create a fork of this sampler.
        
        A subsequent call to ``seed`` is necessary to properly initialize the
        internal state of the sampler.
        
        May throw an exception if not supported.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def loop_put(self: mitsuba.Sampler, loop) -> None:
        """
        Register internal state of this sampler with a symbolic loop
        """
        ...

    def next_1d(self: mitsuba.Sampler, active: bool = True) -> float:
        """
        Retrieve the next component value from the current sample
        """
        ...

    def next_2d(self: mitsuba.Sampler, active: bool = True) -> mitsuba.Point2f:
        """
        Retrieve the next two component values from the current sample
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_count(self: mitsuba.Sampler) -> int:
        """
        Return the number of samples per pixel
        """
        ...

    def schedule_state(self: mitsuba.Sampler) -> None:
        """
        dr::schedule() variables that represent the internal sampler state
        """
        ...

    def seed(self: mitsuba.Sampler, seed: int, wavefront_size: int = 4294967295) -> None:
        """
        Deterministically seed the underlying RNG, if applicable.
        
        In the context of wavefront ray tracing & dynamic arrays, this
        function must be called with ``wavefront_size`` matching the size of
        the wavefront.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_sample_count(self: mitsuba.Sampler, spp: int) -> None:
        """
        Set the number of samples per pixel
        """
        ...

    def set_samples_per_wavefront(self: mitsuba.Sampler, samples_per_wavefront: int) -> None:
        """
        Set the number of samples per pixel per pass in wavefront modes
        (default is 1)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def wavefront_size(self: mitsuba.Sampler) -> int:
        """
        Return the size of the wavefront (or 0, if not seeded)
        """
        ...

    ...

class SamplingIntegrator(Integrator):
    """
    Abstract integrator that performs Monte Carlo sampling starting from
    the sensor
    
    Subclasses of this interface must implement the sample() method, which
    performs Monte Carlo integration to return an unbiased statistical
    estimate of the radiance value along a given ray.
    
    The render() method then repeatedly invokes this estimator to compute
    all pixels of the image.
    """

    def __init__(self: mitsuba.SamplingIntegrator, arg0: mitsuba.Properties) -> None: ...
    hide_emitters = ...
    ptr = ...

    def aov_names(self: mitsuba.Integrator) -> List[str]:
        """
        For integrators that return one or more arbitrary output variables
        (AOVs), this function specifies a list of associated channel names.
        The default implementation simply returns an empty vector.
        """
        ...

    def cancel(self: mitsuba.Integrator) -> None:
        """
        Cancel a running render job (e.g. after receiving Ctrl-C)
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function renders the scene from the viewpoint of ``sensor``. All
        other parameters are optional and control different aspects of the
        rendering process. In particular:
        
        Parameter ``seed``:
            This parameter controls the initialization of the random number
            generator. It is crucial that you specify different seeds (e.g.,
            an increasing sequence) if subsequent ``render``() calls should
            produce statistically independent images.
        
        Parameter ``spp``:
            Set this parameter to a nonzero value to override the number of
            samples per pixel. This value then takes precedence over whatever
            was specified in the construction of ``sensor->sampler()``. This
            parameter may be useful in research applications where an image
            must be rendered multiple times using different quality levels.
        
        Parameter ``develop``:
            If set to ``True``, the implementation post-processes the data
            stored in ``sensor->film()``, returning the resulting image as a
            TensorXf. Otherwise, it returns an empty tensor.
        
        Parameter ``evaluate``:
            This parameter is only relevant for JIT variants of Mitsuba (LLVM,
            CUDA). If set to ``True``, the rendering step evaluates the
            generated image and waits for its completion. A log message also
            denotes the rendering time. Otherwise, the returned tensor
            (``develop=true``) or modified film (``develop=false``) represent
            the rendering task as an unevaluated computation graph.
        
        """
        ...

    @overload
    def render(self: mitsuba.Integrator, scene: mitsuba.Scene, sensor: int = 0, seed: int = 0, spp: int = 0, develop: bool = True, evaluate: bool = True) -> mitsuba.TensorXf:
        """
        Render the scene
        
        This function is just a thin wrapper around the previous render()
        overload. It accepts a sensor *index* instead and renders the scene
        using sensor 0 by default.
        """
        ...

    @overload
    def render_backward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, grad_in: mitsuba.TensorXf, sensor, seed: int = 0, spp: int = 0) -> None: ...
    @overload
    def render_backward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, grad_in: mitsuba.TensorXf, sensor: int = 0, seed: int = 0, spp: int = 0) -> None: ...
    @overload
    def render_forward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, sensor, seed: int = 0, spp: int = 0) -> mitsuba.TensorXf: ...
    @overload
    def render_forward(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, params: object, sensor: int = 0, seed: int = 0, spp: int = 0) -> mitsuba.TensorXf: ...
    def sample(self: mitsuba.SamplingIntegrator, scene: mitsuba.Scene, sampler, ray: mitsuba.RayDifferential3f, medium: mitsuba.Medium = None, active: bool = True) -> Tuple[mitsuba.Color3f, bool, List[float]]:
        """
        Sample the incident radiance along a ray.
        
        Parameter ``scene``:
            The underlying scene in which the radiance function should be
            sampled
        
        Parameter ``sampler``:
            A source of (pseudo-/quasi-) random numbers
        
        Parameter ``ray``:
            A ray, optionally with differentials
        
        Parameter ``medium``:
            If the ray is inside a medium, this parameter holds a pointer to
            that medium
        
        Parameter ``aov``:
            Integrators may return one or more arbitrary output variables
            (AOVs) via this parameter. If ``nullptr`` is provided to this
            argument, no AOVs should be returned. Otherwise, the caller
            guarantees that space for at least ``aov_names().size()`` entries
            has been allocated.
        
        Parameter ``active``:
            A mask that indicates which SIMD lanes are active
        
        Returns:
            A pair containing a spectrum and a mask specifying whether a
            surface or medium interaction was sampled. False mask entries
            indicate that the ray "escaped" the scene, in which case the the
            returned spectrum contains the contribution of environment maps,
            if present. The mask can be used to estimate a suitable alpha
            channel of a rendered image.
        
        Remark:
            In the Python bindings, this function returns the ``aov`` output
            argument as an additional return value. In other words:
        
        ```
        (spec, mask, aov) = integrator.sample(scene, sampler, ray, medium, active)
        ```
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def should_stop(self: mitsuba.Integrator) -> bool:
        """
        Indicates whether cancel() or a timeout have occurred. Should be
        checked regularly in the integrator's main loop so that timeouts are
        enforced accurately.
        
        Note that accurate timeouts rely on m_render_timer, which needs to be
        reset at the beginning of the rendering phase.
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class ScalarBool: ...

class ScalarFloat: ...

class ScalarFloat32: ...

class ScalarFloat64: ...

class ScalarInt: ...

class ScalarInt32: ...

class ScalarInt64: ...

class ScalarMask: ...

class Transform3d:
    """
    Encapsulates a 4x4 homogeneous coordinate transformation along with
    its inverse transpose
    
    The Transform class provides a set of overloaded matrix-vector
    multiplication operators for vectors, points, and normals (all of them
    behave differently under homogeneous coordinate transformations, hence
    the need to represent them using separate types)
    """

    @overload
    def __init__(self: mitsuba.Transform3d) -> None:
        """
        Initialize with the identity matrix
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform3d, arg0: mitsuba.Transform3d) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform3d, arg0: numpy.ndarray) -> None: ...
    @overload
    def __init__(self: mitsuba.Transform3d, arg0: list) -> None: ...
    @overload
    def __init__(self: mitsuba.Transform3d, arg0: mitsuba.Matrix3f64) -> None:
        """
        Initialize the transformation from the given matrix (and compute its
        inverse transpose)
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform3d, arg0: mitsuba.Matrix3f64, arg1: mitsuba.Matrix3f64) -> None:
        """
        Initialize from a matrix and its inverse transpose
        """
        ...

    inverse_transpose = ...
    matrix = ...

    def assign(self: mitsuba.Transform3d, arg0: mitsuba.Transform3d) -> None: ...
    @overload
    def has_scale(self: mitsuba.Transform3d) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform3d) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        """
        ...

    def inverse(self: mitsuba.Transform3d) -> mitsuba.Transform3d:
        """
        Compute the inverse of this transformation (involves just shuffles, no
        arithmetic)
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform3d, p: mitsuba.Point2d) -> mitsuba.Point2d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform3d, v: mitsuba.Vector2d) -> mitsuba.Vector2d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        """
        ...

    def translation(self: mitsuba.Transform3d) -> mitsuba.Vector2d:
        """
        Get the translation part of a matrix
        """
        ...

    ...

class Transform3f:
    """
    Encapsulates a 4x4 homogeneous coordinate transformation along with
    its inverse transpose
    
    The Transform class provides a set of overloaded matrix-vector
    multiplication operators for vectors, points, and normals (all of them
    behave differently under homogeneous coordinate transformations, hence
    the need to represent them using separate types)
    """

    @overload
    def __init__(self: mitsuba.Transform3f) -> None:
        """
        Initialize with the identity matrix
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform3f, arg0: mitsuba.Transform3f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform3f, arg0: numpy.ndarray) -> None: ...
    @overload
    def __init__(self: mitsuba.Transform3f, arg0: list) -> None: ...
    @overload
    def __init__(self: mitsuba.Transform3f, arg0: mitsuba.Matrix3f) -> None:
        """
        Initialize the transformation from the given matrix (and compute its
        inverse transpose)
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform3f, arg0: mitsuba.Matrix3f, arg1: mitsuba.Matrix3f) -> None:
        """
        Initialize from a matrix and its inverse transpose
        """
        ...

    inverse_transpose = ...
    matrix = ...

    def assign(self: mitsuba.Transform3f, arg0: mitsuba.Transform3f) -> None: ...
    @overload
    def has_scale(self: mitsuba.Transform3f) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform3f) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        """
        ...

    def inverse(self: mitsuba.Transform3f) -> mitsuba.Transform3f:
        """
        Compute the inverse of this transformation (involves just shuffles, no
        arithmetic)
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform3f, p: mitsuba.Point2f) -> mitsuba.Point2f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform3f, v: mitsuba.Vector2f) -> mitsuba.Vector2f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        """
        ...

    def translation(self: mitsuba.Transform3f) -> mitsuba.Vector2f:
        """
        Get the translation part of a matrix
        """
        ...

    ...

class Transform4d:
    """
    Encapsulates a 4x4 homogeneous coordinate transformation along with
    its inverse transpose
    
    The Transform class provides a set of overloaded matrix-vector
    multiplication operators for vectors, points, and normals (all of them
    behave differently under homogeneous coordinate transformations, hence
    the need to represent them using separate types)
    """

    @overload
    def __init__(self: mitsuba.Transform4d) -> None:
        """
        Initialize with the identity matrix
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform4d, arg0: mitsuba.Transform4d) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform4d, arg0: numpy.ndarray) -> None: ...
    @overload
    def __init__(self: mitsuba.Transform4d, arg0: list) -> None: ...
    @overload
    def __init__(self: mitsuba.Transform4d, arg0: mitsuba.Matrix4f64) -> None:
        """
        Initialize the transformation from the given matrix (and compute its
        inverse transpose)
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform4d, arg0: mitsuba.Matrix4f64, arg1: mitsuba.Matrix4f64) -> None:
        """
        Initialize from a matrix and its inverse transpose
        """
        ...

    inverse_transpose = ...
    matrix = ...

    def assign(self: mitsuba.Transform4d, arg0: mitsuba.Transform4d) -> None: ...
    def extract(self: mitsuba.Transform4d) -> mitsuba.Transform3d:
        """
        Extract a lower-dimensional submatrix
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform4d) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform4d) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        """
        ...

    def inverse(self: mitsuba.Transform4d) -> mitsuba.Transform4d:
        """
        Compute the inverse of this transformation (involves just shuffles, no
        arithmetic)
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4d, p: mitsuba.Point3d) -> mitsuba.Point3d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4d, ray):
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4d, v: mitsuba.Vector3d) -> mitsuba.Vector3d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4d, n: mitsuba.Normal3d) -> mitsuba.Normal3d:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        """
        ...

    def translation(self: mitsuba.Transform4d) -> mitsuba.Vector3d:
        """
        Get the translation part of a matrix
        """
        ...

    ...

class Transform4f:
    """
    Encapsulates a 4x4 homogeneous coordinate transformation along with
    its inverse transpose
    
    The Transform class provides a set of overloaded matrix-vector
    multiplication operators for vectors, points, and normals (all of them
    behave differently under homogeneous coordinate transformations, hence
    the need to represent them using separate types)
    """

    @overload
    def __init__(self: mitsuba.Transform4f) -> None:
        """
        Initialize with the identity matrix
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform4f, arg0: mitsuba.Transform4f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform4f, arg0: numpy.ndarray) -> None: ...
    @overload
    def __init__(self: mitsuba.Transform4f, arg0: list) -> None: ...
    @overload
    def __init__(self: mitsuba.Transform4f, arg0: mitsuba.Matrix4f) -> None:
        """
        Initialize the transformation from the given matrix (and compute its
        inverse transpose)
        
        """
        ...

    @overload
    def __init__(self: mitsuba.Transform4f, arg0: mitsuba.Matrix4f, arg1: mitsuba.Matrix4f) -> None:
        """
        Initialize from a matrix and its inverse transpose
        """
        ...

    inverse_transpose = ...
    matrix = ...

    def assign(self: mitsuba.Transform4f, arg0: mitsuba.Transform4f) -> None: ...
    def extract(self: mitsuba.Transform4f) -> mitsuba.Transform3f:
        """
        Extract a lower-dimensional submatrix
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform4f) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        
        """
        ...

    @overload
    def has_scale(self: mitsuba.Transform4f) -> bool:
        """
        Test for a scale component in each transform matrix by checking
        whether ``M . M^T == I`` (where ``M`` is the matrix in question and
        ``I`` is the identity).
        """
        ...

    def inverse(self: mitsuba.Transform4f) -> mitsuba.Transform4f:
        """
        Compute the inverse of this transformation (involves just shuffles, no
        arithmetic)
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4f, p: mitsuba.Point3f) -> mitsuba.Point3f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4f, ray: mitsuba.Ray3f) -> mitsuba.Ray3f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4f, v: mitsuba.Vector3f) -> mitsuba.Vector3f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        
        """
        ...

    @overload
    def transform_affine(self: mitsuba.Transform4f, n: mitsuba.Normal3f) -> mitsuba.Normal3f:
        """
        Transform a 3D vector/point/normal/ray by a transformation that is
        known to be an affine 3D transformation (i.e. no perspective)
        """
        ...

    def translation(self: mitsuba.Transform4f) -> mitsuba.Vector3f:
        """
        Get the translation part of a matrix
        """
        ...

    ...

class ScalarUInt: ...

class ScalarUInt32: ...

class ScalarUInt64: ...

class Vector0d:
    def __init__(self: mitsuba.Vector0d, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Vector0f:
    def __init__(self: mitsuba.Vector0f, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Vector0i:
    def __init__(self: mitsuba.Vector0i, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Vector0u:
    def __init__(self: mitsuba.Vector0u, *args) -> None: ...
    label = ...

    def assign(self, other): ...
    ...

class Vector1d:
    def __init__(self: mitsuba.Vector1d, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Vector1f:
    def __init__(self: mitsuba.Vector1f, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Vector1i:
    def __init__(self: mitsuba.Vector1i, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Vector1u:
    def __init__(self: mitsuba.Vector1u, *args) -> None: ...
    label = ...
    x = ...

    def assign(self, other): ...
    ...

class Vector2d:
    def __init__(self: mitsuba.Vector2d, *args) -> None: ...
    label = ...
    x = ...
    y = ...

    def assign(self, other): ...
    ...

class Vector2f:
    def __init__(self: mitsuba.Vector2f, *args) -> None: ...
    label = ...
    x = ...
    y = ...

    def assign(self, other): ...
    ...

class Vector2i:
    def __init__(self: mitsuba.Vector2i, *args) -> None: ...
    label = ...
    x = ...
    y = ...

    def assign(self, other): ...
    ...

class Vector2u:
    def __init__(self: mitsuba.Vector2u, *args) -> None: ...
    label = ...
    x = ...
    y = ...

    def assign(self, other): ...
    ...

class Vector3d:
    def __init__(self: mitsuba.Vector3d, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Vector3f:
    def __init__(self: mitsuba.Vector3f, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Vector3i:
    def __init__(self: mitsuba.Vector3i, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Vector3u:
    def __init__(self: mitsuba.Vector3u, *args) -> None: ...
    label = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Vector4d:
    def __init__(self: mitsuba.Vector4d, *args) -> None: ...
    label = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Vector4f:
    def __init__(self: mitsuba.Vector4f, *args) -> None: ...
    label = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Vector4i:
    def __init__(self: mitsuba.Vector4i, *args) -> None: ...
    label = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Vector4u:
    def __init__(self: mitsuba.Vector4u, *args) -> None: ...
    label = ...
    w = ...
    x = ...
    y = ...
    z = ...

    def assign(self, other): ...
    ...

class Scene(Object):
    """
    Central scene data structure
    
    Mitsuba's scene class encapsulates a tree of mitsuba Object instances
    including emitters, sensors, shapes, materials, participating media,
    the integrator (i.e. the method used to render the image) etc.
    
    It organizes these objects into groups that can be accessed through
    getters (see shapes(), emitters(), sensors(), etc.), and it provides
    three key abstractions implemented on top of these groups,
    specifically:
    
    * Ray intersection queries and shadow ray tests (See
    \ray_intersect_preliminary(), ray_intersect(), and ray_test()).
    
    * Sampling rays approximately proportional to the emission profile of
    light sources in the scene (see sample_emitter_ray())
    
    * Sampling directions approximately proportional to the direct
    radiance from emitters received at a given scene location (see
    sample_emitter_direction()).
    """

    def __init__(self: mitsuba.Scene, arg0: mitsuba.Properties) -> None: ...
    ptr = ...

    def bbox(self: mitsuba.Scene) -> mitsuba.BoundingBox3f:
        """
        Return a bounding box surrounding the scene
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def emitters(self: mitsuba.Scene):
        """
        Return the list of emitters
        """
        ...

    def emitters_dr(self: mitsuba.Scene):
        """
        Return the list of emitters as a Dr.Jit array
        """
        ...

    def environment(self: mitsuba.Scene):
        """
        Return the environment emitter (if any)
        """
        ...

    def eval_emitter_direction(self: mitsuba.Scene, ref, ds, active: bool = True) -> mitsuba.Color3f:
        """
        Re-evaluate the incident direct radiance of the
        sample_emitter_direction() method.
        
        This function re-evaluates the incident direct radiance and sample
        probability due to the emitter *so that division by * ``ds.pdf``
        equals the sampling weight returned by sample_emitter_direction().
        This may appear redundant, and indeed such a function would not find
        use in "normal" rendering algorithms.
        
        However, the ability to re-evaluate the contribution of a direct
        illumination sample is important for differentiable rendering. For
        example, we might want to track derivatives in the sampled direction
        (``ds.d``) without also differentiating the sampling technique.
        
        In contrast to pdf_emitter_direction(), evaluating this function can
        yield a nonzero result in the case of emission profiles containing a
        Dirac delta term (e.g. point or directional lights).
        
        Parameter ``ref``:
            A 3D reference location within the scene, which may influence the
            sampling process.
        
        Parameter ``ds``:
            A direction sampling record, which specifies the query location.
        
        Returns:
            The incident radiance and discrete or solid angle density of the
            sample.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def integrator(self: mitsuba.Scene) -> object:
        """
        Return the scene's integrator
        """
        ...

    def invert_silhouette_sample(self: mitsuba.Scene, ss, active: bool = True) -> mitsuba.Point3f:
        """
        Map a silhouette segment to a point in boundary sample space
        
        This method is the inverse of sample_silhouette(). The mapping from
        boundary sample space to boundary segments is bijective.
        
        Parameter ``ss``:
            The sampled boundary segment
        
        Returns:
            The corresponding boundary sample space point
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def pdf_emitter(self: mitsuba.Scene, index: int, active: bool = True) -> float:
        """
        Evaluate the discrete probability of the sample_emitter() technique
        for the given a emitter index.
        """
        ...

    def pdf_emitter_direction(self: mitsuba.Scene, ref, ds, active: bool = True) -> float:
        """
        Evaluate the PDF of direct illumination sampling
        
        This function evaluates the probability density (per unit solid angle)
        of the sampling technique implemented by the sample_emitter_direct()
        function. The returned probability will always be zero when the
        emission profile contains a Dirac delta term (e.g. point or
        directional emitters/sensors).
        
        Parameter ``ref``:
            A 3D reference location within the scene, which may influence the
            sampling process.
        
        Parameter ``ds``:
            A direction sampling record, which specifies the query location.
        
        Returns:
            The solid angle density of the sample
        """
        ...

    @overload
    def ray_intersect(self: mitsuba.Scene, ray: mitsuba.Ray3f, active: bool = True):
        """
        Intersect a ray with the shapes comprising the scene and return a
        detailed data structure describing the intersection, if one is found.
        
        In vectorized variants of Mitsuba (``cuda_*`` or ``llvm_*``), the
        function processes arrays of rays and returns arrays of surface
        interactions following the usual conventions.
        
        This method is a convenience wrapper of the generalized version of
        ``ray_intersect``() below. It assumes that incoherent rays are being
        traced, and that the user desires access to all fields of the
        SurfaceInteraction. In other words, it simply invokes the general
        ``ray_intersect``() overload with ``coherent=false`` and ``ray_flags``
        equal to RayFlags::All.
        
        Parameter ``ray``:
            A 3D ray including maximum extent (Ray::maxt) and time (Ray::time)
            information, which matters when the shapes are in motion
        
        Returns:
            A detailed surface interaction record. Its ``is_valid()`` method
            should be queried to check if an intersection was actually found.
        
        """
        ...

    @overload
    def ray_intersect(self: mitsuba.Scene, ray: mitsuba.Ray3f, ray_flags: int, coherent: bool, active: bool = True):
        """
        Intersect a ray with the shapes comprising the scene and return a
        detailed data structure describing the intersection, if one is found
        
        In vectorized variants of Mitsuba (``cuda_*`` or ``llvm_*``), the
        function processes arrays of rays and returns arrays of surface
        interactions following the usual conventions.
        
        This generalized ray intersection method exposes two additional flags
        to control the intersection process. Internally, it is split into two
        steps:
        
        <ol>
        
        * Finding a PreliminaryInteraction using the ray tracing backend
        underlying the current variant (i.e., Mitsuba's builtin kd-tree,
        Embree, or OptiX). This is done using the ray_intersect_preliminary()
        function that is also available directly below (and preferable if a
        full SurfaceInteraction is not needed.).
        
        * Expanding the PreliminaryInteraction into a full SurfaceInteraction
        (this part happens within Mitsuba/Dr.Jit and tracks derivative
        information in AD variants of the system).
        
        </ol>
        
        The SurfaceInteraction data structure is large, and computing its
        contents in the second step requires a non-trivial amount of
        computation and sequence of memory accesses. The ``ray_flags``
        parameter can be used to specify that only a sub-set of the full
        intersection data structure actually needs to be computed, which can
        improve performance.
        
        In the context of differentiable rendering, the ``ray_flags``
        parameter also influences how derivatives propagate between the input
        ray, the shape parameters, and the computed intersection (see
        RayFlags::FollowShape and RayFlags::DetachShape for details on this).
        The default, RayFlags::All, propagates derivatives through all steps
        of the intersection computation.
        
        The ``coherent`` flag is a hint that can improve performance in the
        first step of finding the PreliminaryInteraction if the input set of
        rays is coherent (e.g., when they are generated by
        Sensor::sample_ray(), which means that adjacent rays will traverse
        essentially the same region of space). This flag is currently only
        used by the combination of ``llvm_*`` variants and the Embree ray
        tracing backend.
        
        Parameter ``ray``:
            A 3D ray including maximum extent (Ray::maxt) and time (Ray::time)
            information, which matters when the shapes are in motion
        
        Parameter ``ray_flags``:
            An integer combining flag bits from RayFlags (merged using binary
            or).
        
        Parameter ``coherent``:
            Setting this flag to ``True`` can noticeably improve performance
            when ``ray`` contains a coherent set of rays (e.g. primary camera
            rays), and when using ``llvm_*`` variants of the renderer along
            with Embree. It has no effect in scalar or CUDA/OptiX variants.
        
        Returns:
            A detailed surface interaction record. Its ``is_valid()`` method
            should be queried to check if an intersection was actually found.
        """
        ...

    def ray_intersect_preliminary(self: mitsuba.Scene, ray: mitsuba.Ray3f, coherent: bool = False, active: bool = True):
        """
        Intersect a ray with the shapes comprising the scene and return
        preliminary information, if one is found
        
        This function invokes the ray tracing backend underlying the current
        variant (i.e., Mitsuba's builtin kd-tree, Embree, or OptiX) and
        returns preliminary intersection information consisting of
        
        * the ray distance up to the intersection (if one is found).
        
        * the intersected shape and primitive index.
        
        * local UV coordinates of the intersection within the primitive.
        
        * A pointer to the intersected shape or instance.
        
        The information is only preliminary at this point, because it lacks
        various other information (geometric and shading frame, texture
        coordinates, curvature, etc.) that is generally needed by shading
        models. In variants of Mitsuba that perform automatic differentiation,
        it is important to know that computation done by the ray tracing
        backend is not reflected in Dr.Jit's computation graph. The
        ray_intersect() method will re-evaluate certain parts of the
        computation with derivative tracking to rectify this.
        
        In vectorized variants of Mitsuba (``cuda_*`` or ``llvm_*``), the
        function processes arrays of rays and returns arrays of preliminary
        intersection records following the usual conventions.
        
        The ``coherent`` flag is a hint that can improve performance if the
        input set of rays is coherent (e.g., when they are generated by
        Sensor::sample_ray(), which means that adjacent rays will traverse
        essentially the same region of space). This flag is currently only
        used by the combination of ``llvm_*`` variants and the Embree ray
        intersector.
        
        Parameter ``ray``:
            A 3D ray including maximum extent (Ray::maxt) and time (Ray::time)
            information, which matters when the shapes are in motion
        
        Parameter ``coherent``:
            Setting this flag to ``True`` can noticeably improve performance
            when ``ray`` contains a coherent set of rays (e.g. primary camera
            rays), and when using ``llvm_*`` variants of the renderer along
            with Embree. It has no effect in scalar or CUDA/OptiX variants.
        
        Returns:
            A preliminary surface interaction record. Its ``is_valid()``
            method should be queried to check if an intersection was actually
            found.
        """
        ...

    @overload
    def ray_test(self: mitsuba.Scene, ray: mitsuba.Ray3f, active: bool = True) -> bool:
        """
        Intersect a ray with the shapes comprising the scene and return a
        boolean specifying whether or not an intersection was found.
        
        In vectorized variants of Mitsuba (``cuda_*`` or ``llvm_*``), the
        function processes arrays of rays and returns arrays of booleans
        following the usual conventions.
        
        Testing for the mere presence of intersections is considerably faster
        than finding an actual intersection, hence this function should be
        preferred over ray_intersect() when geometric information about the
        first visible intersection is not needed.
        
        This method is a convenience wrapper of the generalized version of
        ``ray_test``() below, which assumes that incoherent rays are being
        traced. In other words, it simply invokes the general ``ray_test``()
        overload with ``coherent=false``.
        
        Parameter ``ray``:
            A 3D ray including maximum extent (Ray::maxt) and time (Ray::time)
            information, which matters when the shapes are in motion
        
        Returns:
            ``True`` if an intersection was found
        
        """
        ...

    @overload
    def ray_test(self: mitsuba.Scene, ray: mitsuba.Ray3f, coherent: bool, active: bool = True) -> bool:
        """
        Intersect a ray with the shapes comprising the scene and return a
        boolean specifying whether or not an intersection was found.
        
        In vectorized variants of Mitsuba (``cuda_*`` or ``llvm_*``), the
        function processes arrays of rays and returns arrays of booleans
        following the usual conventions.
        
        Testing for the mere presence of intersections is considerably faster
        than finding an actual intersection, hence this function should be
        preferred over ray_intersect() when geometric information about the
        first visible intersection is not needed.
        
        The ``coherent`` flag is a hint that can improve performance in the
        first step of finding the PreliminaryInteraction if the input set of
        rays is coherent, which means that adjacent rays will traverse
        essentially the same region of space. This flag is currently only used
        by the combination of ``llvm_*`` variants and the Embree ray tracing
        backend.
        
        Parameter ``ray``:
            A 3D ray including maximum extent (Ray::maxt) and time (Ray::time)
            information, which matters when the shapes are in motion
        
        Parameter ``coherent``:
            Setting this flag to ``True`` can noticeably improve performance
            when ``ray`` contains a coherent set of rays (e.g. primary camera
            rays), and when using ``llvm_*`` variants of the renderer along
            with Embree. It has no effect in scalar or CUDA/OptiX variants.
        
        Returns:
            ``True`` if an intersection was found
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_emitter(self: mitsuba.Scene, sample: float, active: bool = True) -> Tuple[int, float, float]:
        """
        Sample one emitter in the scene and rescale the input sample for
        reuse.
        
        Currently, the sampling scheme implemented by the Scene class is very
        simplistic (uniform).
        
        Parameter ``sample``:
            A uniformly distributed number in [0, 1).
        
        Returns:
            The index of the chosen emitter along with the sampling weight
            (equal to the inverse PDF), and the transformed random sample for
            reuse.
        """
        ...

    def sample_emitter_direction(self: mitsuba.Scene, ref, sample: mitsuba.Point2f, test_visibility: bool = True, active: bool = True):
        """
        Direct illumination sampling routine
        
        This method implements stochastic connections to emitters, which is
        variously known as *emitter sampling*, *direct illumination sampling*,
        or *next event estimation*.
        
        The function expects a 3D reference location ``ref`` as input, which
        may influence the sampling process. Normally, this would be the
        location of a surface position being shaded. Ideally, the
        implementation of this function should then draw samples proportional
        to the scene's emission profile and the inverse square distance
        between the reference point and the sampled emitter position. However,
        approximations are acceptable as long as these are reflected in the
        returned Monte Carlo sampling weight.
        
        Parameter ``ref``:
            A 3D reference location within the scene, which may influence the
            sampling process.
        
        Parameter ``sample``:
            A uniformly distributed 2D random variate
        
        Parameter ``test_visibility``:
            When set to ``True``, a shadow ray will be cast to ensure that the
            sampled emitter position and the reference point are mutually
            visible.
        
        Returns:
            A tuple ``(ds, spec)`` where
        
        * ``ds`` is a fully populated DirectionSample3f data structure, which
        provides further detail about the sampled emitter position (e.g. its
        surface normal, solid angle density, whether Dirac delta distributions
        were involved, etc.)
        
        *
        
        * ``spec`` is a Monte Carlo sampling weight specifying the ratio of
        the radiance incident from the emitter and the sample probability per
        unit solid angle.
        """
        ...

    def sample_emitter_ray(self: mitsuba.Scene, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool):
        """
        Sample a ray according to the emission profile of scene emitters
        
        This function combines both steps of choosing a ray origin on a light
        source and an outgoing ray direction. It does not return any auxiliary
        sampling information and is mainly meant to be used by unidirectional
        rendering techniques like particle tracing.
        
        Sampling is ideally perfectly proportional to the emission profile,
        though approximations are acceptable as long as these are reflected in
        the returned Monte Carlo sampling weight.
        
        Parameter ``time``:
            The scene time associated with the ray to be sampled.
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the emission profile.
        
        Parameter ``sample2``:
            A uniformly distributed sample on the domain ``[0,1]^2``.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``.
        
        Returns:
            A tuple ``(ray, weight, emitter, radiance)``, where
        
        * ``ray`` is the sampled ray (e.g. starting on the surface of an area
        emitter)
        
        * ``weight`` returns the emitted radiance divided by the spatio-
        directional sampling density
        
        * ``emitter`` is a pointer specifying the sampled emitter
        """
        ...

    def sample_silhouette(self: mitsuba.Scene, sample: mitsuba.Point3f, flags: int, active: bool = True):
        """
        Map a point sample in boundary sample space to a silhouette segment
        
        This method will sample a SilhouetteSample3f object from all the
        shapes in the scene that are being differentiated and have non-zero
        sampling weight (see Shape::silhouette_sampling_weight).
        
        Parameter ``sample``:
            The boundary space sample (a point in the unit cube).
        
        Parameter ``flags``:
            Flags to select the type of silhouettes to sample from (see
            DiscontinuityFlags). Multiple types of discontinuities can be
            sampled in a single call. If a single type of silhouette is
            specified, shapes that do not have that types might still be
            sampled. In which case, the SilhouetteSample3f field
            ``discontinuity_type`` will be DiscontinuityFlags::Empty.
        
        Returns:
            Silhouette sample record.
        """
        ...

    def sensors(self: mitsuba.Scene) -> list:
        """
        Return the list of sensors
        """
        ...

    def sensors_dr(self: mitsuba.Scene):
        """
        Return the list of sensors as a Dr.Jit array
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def shapes(self: mitsuba.Scene) -> list:
        """
        Return the list of shapes
        """
        ...

    def shapes_dr(self: mitsuba.Scene):
        """
        Return the list of shapes as a Dr.Jit array
        """
        ...

    def shapes_grad_enabled(self: mitsuba.Scene) -> bool:
        """
        Specifies whether any of the scene's shape parameters have gradient
        tracking enabled
        """
        ...

    def silhouette_shapes(self: mitsuba.Scene) -> list:
        """
        Return the list of shapes that can have their silhouette sampled
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

from collections.abc import Mapping
class SceneParameters(Mapping):
    """
        Dictionary-like object that references various parameters used in a Mitsuba
        scene graph. Parameters can be read and written using standard syntax
        (``parameter_map[key]``). The class exposes several non-standard functions,
        specifically :py:meth:`~mitsuba.SceneParameters.torch()`,
        :py:meth:`~mitsuba.SceneParameters.update()`, and
        :py:meth:`~mitsuba.SceneParameters.keep()`.
        
    """

    def copy(self): ...
    def flags(self, key: 'str'):
        """
        Return parameter flags
        """
        ...

    def get(self, key, default=None):
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        ...

    def items(self): ...
    def keep(self, keys: 'None | str | list[str]') -> 'None':
        """
        
        Reduce the size of the dictionary by only keeping elements,
        whose keys are defined by 'keys'.
        
        Parameter ``keys`` (``None``, ``str``, ``[str]``):
        Specifies which parameters should be kept. Regex are supported to define
        a subset of parameters at once. If set to ``None``, all differentiable
        scene parameters will be loaded.
        
        """
        ...

    def keys(self): ...
    def set_dirty(self, key: 'str'):
        """
        
        Marks a specific parameter and its parent objects as dirty. A subsequent call
        to :py:meth:`~mitsuba.SceneParameters.update()` will refresh their internal
        state.
        
        This method should rarely be called explicitly. The
        :py:class:`~mitsuba.SceneParameters` will detect most operations on
        its values and automatically flag them as dirty. A common exception to
        the detection mechanism is the :py:meth:`~drjit.scatter` operation which
        needs an explicit call to :py:meth:`~mitsuba.SceneParameters.set_dirty()`.
        
        """
        ...

    def update(self, values: 'dict' = None) -> 'list[tuple[Any, set]]':
        """
        
        This function should be called at the end of a sequence of writes
        to the dictionary. It automatically notifies all modified Mitsuba
        objects and their parent objects that they should refresh their
        internal state. For instance, the scene may rebuild the kd-tree
        when a shape was modified, etc.
        
        The return value of this function is a list of tuples where each tuple
        corresponds to a Mitsuba node/object that is updated. The tuple's first
        element is the node itself. The second element is the set of keys that
        the node is being updated for.
        
        Parameter ``values`` (``dict``):
        Optional dictionary-like object containing a set of keys and values
        to be used to overwrite scene parameters. This operation will happen
        before propagating the update further into the scene internal state.
        
        """
        ...

    def values(self):
        """
        D.values() -> an object providing a view on D's values
        """
        ...

    ...

class ScopedSetThreadEnvironment:
    """
    RAII-style class to temporarily switch to another thread's logger/file
    resolver
    """

    def __init__(self: mitsuba.ScopedSetThreadEnvironment, arg0: mitsuba.ThreadEnvironment) -> None: ...
    ...

class Sensor(Endpoint):
    def __init__(self: mitsuba.Sensor, arg0: mitsuba.Properties) -> None: ...
    m_film = ...
    m_needs_sample_2 = ...
    m_needs_sample_3 = ...
    ptr = ...

    def bbox(self: mitsuba.Endpoint) -> mitsuba.BoundingBox3f:
        """
        Return an axis-aligned box bounding the spatial extents of the emitter
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.Sensor, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Given a ray-surface intersection, return the emitted radiance or
        importance traveling along the reverse direction
        
        This function is e.g. used when an area light source has been hit by a
        ray in a path tracing-style integrator, and it subsequently needs to
        be queried for the emitted radiance along the negative ray direction.
        The default implementation throws an exception, which states that the
        method is not implemented.
        
        Parameter ``si``:
            An intersect record that specifies both the query position and
            direction (using the ``si.wi`` field)
        
        Returns:
            The emitted radiance or importance
        """
        ...

    def eval_direction(self: mitsuba.Sensor, it: mitsuba.Interaction3f, ds: mitsuba.DirectionSample3f, active: bool = True) -> mitsuba.Color3f:
        """
        Re-evaluate the incident direct radiance/importance of the
        sample_direction() method.
        
        This function re-evaluates the incident direct radiance or importance
        and sample probability due to the endpoint so that division by
        ``ds.pdf`` equals the sampling weight returned by sample_direction().
        This may appear redundant, and indeed such a function would not find
        use in "normal" rendering algorithms.
        
        However, the ability to re-evaluate the contribution of a generated
        sample is important for differentiable rendering. For example, we
        might want to track derivatives in the sampled direction (``ds.d``)
        without also differentiating the sampling technique.
        
        In contrast to pdf_direction(), evaluating this function can yield a
        nonzero result in the case of emission profiles containing a Dirac
        delta term (e.g. point or directional lights).
        
        Parameter ``ref``:
            A 3D reference location within the scene, which may influence the
            sampling process.
        
        Parameter ``ds``:
            A direction sampling record, which specifies the query location.
        
        Returns:
            The incident direct radiance/importance associated with the
            sample.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def film(self: mitsuba.Sensor) -> mitsuba.Film:
        """
        Return the Film instance associated with this sensor
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def medium(self: mitsuba.Endpoint) -> mitsuba.Medium:
        """
        Return a pointer to the medium that surrounds the emitter
        """
        ...

    def needs_aperture_sample(self: mitsuba.Sensor) -> bool:
        """
        Does the sampling technique require a sample for the aperture
        position?
        """
        ...

    def needs_sample_2(self: mitsuba.Endpoint) -> bool:
        """
        Does the method sample_ray() require a uniformly distributed 2D sample
        for the ``sample2`` parameter?
        """
        ...

    def needs_sample_3(self: mitsuba.Endpoint) -> bool:
        """
        Does the method sample_ray() require a uniformly distributed 2D sample
        for the ``sample3`` parameter?
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def pdf_direction(self: mitsuba.Sensor, it: mitsuba.Interaction3f, ds: mitsuba.DirectionSample3f, active: bool = True) -> float:
        """
        Evaluate the probability density of the *direct* sampling method
        implemented by the sample_direction() method.
        
        The returned probability will always be zero when the
        emission/sensitivity profile contains a Dirac delta term (e.g. point
        or directional emitters/sensors).
        
        Parameter ``ds``:
            A direct sampling record, which specifies the query location.
        """
        ...

    def pdf_position(self: mitsuba.Sensor, ps: mitsuba.PositionSample3f, active: bool = True) -> float:
        """
        Evaluate the probability density of the position sampling method
        implemented by sample_position().
        
        In simple cases, this will be the reciprocal of the endpoint's surface
        area.
        
        Parameter ``ps``:
            The sampled position record.
        
        Returns:
            The corresponding sampling density.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_direction(self: mitsuba.Sensor, it: mitsuba.Interaction3f, sample: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.DirectionSample3f, mitsuba.Color3f]:
        """
        Given a reference point in the scene, sample a direction from the
        reference point towards the endpoint (ideally proportional to the
        emission/sensitivity profile)
        
        This operation is a generalization of direct illumination techniques
        to both emitters *and* sensors. A direction sampling method is given
        an arbitrary reference position in the scene and samples a direction
        from the reference point towards the endpoint (ideally proportional to
        the emission/sensitivity profile). This reduces the sampling domain
        from 4D to 2D, which often enables the construction of smarter
        specialized sampling techniques.
        
        Ideally, the implementation should importance sample the product of
        the emission profile and the geometry term between the reference point
        and the position on the endpoint.
        
        The default implementation throws an exception.
        
        Parameter ``ref``:
            A reference position somewhere within the scene.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``.
        
        Returns:
            A DirectionSample instance describing the generated sample along
            with a spectral importance weight.
        """
        ...

    def sample_position(self: mitsuba.Sensor, time: float, sample: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.PositionSample3f, float]:
        """
        Importance sample the spatial component of the emission or importance
        profile of the endpoint.
        
        The default implementation throws an exception.
        
        Parameter ``time``:
            The scene time associated with the position to be sampled.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``.
        
        Returns:
            A PositionSample instance describing the generated sample along
            with an importance weight.
        """
        ...

    def sample_ray(self: mitsuba.Sensor, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.Ray3f, mitsuba.Color3f]:
        """
        Importance sample a ray proportional to the endpoint's
        sensitivity/emission profile.
        
        The endpoint profile is a six-dimensional quantity that depends on
        time, wavelength, surface position, and direction. This function takes
        a given time value and five uniformly distributed samples on the
        interval [0, 1] and warps them so that the returned ray follows the
        profile. Any discrepancies between ideal and actual sampled profile
        are absorbed into a spectral importance weight that is returned along
        with the ray.
        
        Parameter ``time``:
            The scene time associated with the ray to be sampled
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the emission profile.
        
        Parameter ``sample2``:
            A uniformly distributed sample on the domain ``[0,1]^2``. For
            sensor endpoints, this argument corresponds to the sample position
            in fractional pixel coordinates relative to the crop window of the
            underlying film. This argument is ignored if ``needs_sample_2() ==
            false``.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``. For
            sensor endpoints, this argument determines the position on the
            aperture of the sensor. This argument is ignored if
            ``needs_sample_3() == false``.
        
        Returns:
            The sampled ray and (potentially spectrally varying) importance
            weights. The latter account for the difference between the profile
            and the actual used sampling density function.
        """
        ...

    @overload
    def sample_ray_differential(self: mitsuba.Sensor, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.RayDifferential3f, mitsuba.Color3f]:
        """
        Importance sample a ray differential proportional to the sensor's
        sensitivity profile.
        
        The sensor profile is a six-dimensional quantity that depends on time,
        wavelength, surface position, and direction. This function takes a
        given time value and five uniformly distributed samples on the
        interval [0, 1] and warps them so that the returned ray the profile.
        Any discrepancies between ideal and actual sampled profile are
        absorbed into a spectral importance weight that is returned along with
        the ray.
        
        In contrast to Endpoint::sample_ray(), this function returns
        differentials with respect to the X and Y axis in screen space.
        
        Parameter ``time``:
            The scene time associated with the ray_differential to be sampled
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the sensitivity profile.
        
        Parameter ``sample2``:
            This argument corresponds to the sample position in fractional
            pixel coordinates relative to the crop window of the underlying
            film.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``. This
            argument determines the position on the aperture of the sensor.
            This argument is ignored if ``needs_sample_3() == false``.
        
        Returns:
            The sampled ray differential and (potentially spectrally varying)
            importance weights. The latter account for the difference between
            the sensor profile and the actual used sampling density function.
        
        """
        ...

    @overload
    def sample_ray_differential(self: mitsuba.Sensor, time: float, sample1: float, sample2: mitsuba.Point2f, sample3: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.RayDifferential3f, mitsuba.Color3f]:
        """
        Importance sample a ray differential proportional to the sensor's
        sensitivity profile.
        
        The sensor profile is a six-dimensional quantity that depends on time,
        wavelength, surface position, and direction. This function takes a
        given time value and five uniformly distributed samples on the
        interval [0, 1] and warps them so that the returned ray the profile.
        Any discrepancies between ideal and actual sampled profile are
        absorbed into a spectral importance weight that is returned along with
        the ray.
        
        In contrast to Endpoint::sample_ray(), this function returns
        differentials with respect to the X and Y axis in screen space.
        
        Parameter ``time``:
            The scene time associated with the ray_differential to be sampled
        
        Parameter ``sample1``:
            A uniformly distributed 1D value that is used to sample the
            spectral dimension of the sensitivity profile.
        
        Parameter ``sample2``:
            This argument corresponds to the sample position in fractional
            pixel coordinates relative to the crop window of the underlying
            film.
        
        Parameter ``sample3``:
            A uniformly distributed sample on the domain ``[0,1]^2``. This
            argument determines the position on the aperture of the sensor.
            This argument is ignored if ``needs_sample_3() == false``.
        
        Returns:
            The sampled ray differential and (potentially spectrally varying)
            importance weights. The latter account for the difference between
            the sensor profile and the actual used sampling density function.
        """
        ...

    def sample_wavelengths(self: mitsuba.Sensor, si: mitsuba.SurfaceInteraction3f, sample: float, active: bool = True) -> Tuple[mitsuba.Color0f, mitsuba.Color3f]:
        """
        Importance sample a set of wavelengths according to the endpoint's
        sensitivity/emission spectrum.
        
        This function takes a uniformly distributed 1D sample and generates a
        sample that is approximately distributed according to the endpoint's
        spectral sensitivity/emission profile.
        
        For this, the input 1D sample is first replicated into
        ``Spectrum::Size`` separate samples using simple arithmetic
        transformations (see math::sample_shifted()), which can be interpreted
        as a type of Quasi-Monte-Carlo integration scheme. Following this, a
        standard technique (e.g. inverse transform sampling) is used to find
        the corresponding wavelengths. Any discrepancies between ideal and
        actual sampled profile are absorbed into a spectral importance weight
        that is returned along with the wavelengths.
        
        This function should not be called in RGB or monochromatic modes.
        
        Parameter ``si``:
            In the case of a spatially-varying spectral sensitivity/emission
            profile, this parameter conditions sampling on a specific spatial
            position. The ``si.uv`` field must be specified in this case.
        
        Parameter ``sample``:
            A 1D uniformly distributed random variate
        
        Returns:
            The set of sampled wavelengths and (potentially spectrally
            varying) importance weights. The latter account for the difference
            between the profile and the actual used sampling density function.
            In the case of emitters, the weight will include the emitted
            radiance.
        """
        ...

    def sampler(self: mitsuba.Sensor) -> mitsuba.Sampler:
        """
        Return the sensor's sample generator
        
        This is the *root* sampler, which will later be forked a number of
        times to provide each participating worker thread with its own
        instance (see Scene::sampler()). Therefore, this sampler should never
        be used for anything except creating forks.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_medium(self: mitsuba.Endpoint, medium: mitsuba.Medium) -> None:
        """
        Set the medium that surrounds the emitter.
        """
        ...

    def set_scene(self: mitsuba.Endpoint, scene: mitsuba.Scene) -> None:
        """
        Inform the emitter about the properties of the scene
        
        Various emitters that surround the scene (e.g. environment emitters)
        must be informed about the scene dimensions to operate correctly. This
        function is invoked by the Scene constructor.
        """
        ...

    def set_shape(self: mitsuba.Endpoint, shape: mitsuba.Shape) -> None:
        """
        Set the shape associated with this endpoint.
        """
        ...

    def shape(self: mitsuba.Sensor) -> mitsuba.Shape:
        """
        Return the shape, to which the emitter is currently attached
        """
        ...

    def shutter_open(self: mitsuba.Sensor) -> float:
        """
        Return the time value of the shutter opening event
        """
        ...

    def shutter_open_time(self: mitsuba.Sensor) -> float:
        """
        Return the length, for which the shutter remains open
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def world_transform(self: mitsuba.Endpoint) -> mitsuba.Transform4f:
        """
        Return the local space to world space transformation
        """
        ...

    ...

class Shape(Object):
    """
    Forward declaration for `SilhouetteSample`
    """

    ptr = ...

    @overload
    def bbox(self: mitsuba.Shape) -> mitsuba.BoundingBox3f:
        """
        Return an axis aligned box that bounds all shape primitives (including
        any transformations that may have been applied to them)
        
        """
        ...

    @overload
    def bbox(self: mitsuba.Shape, index: int) -> mitsuba.BoundingBox3f:
        """
        Return an axis aligned box that bounds a single shape primitive
        (including any transformations that may have been applied to it)
        
        Remark:
            The default implementation simply calls bbox()
        
        """
        ...

    @overload
    def bbox(self: mitsuba.Shape, index: int, clip: mitsuba.BoundingBox3f) -> mitsuba.BoundingBox3f:
        """
        Return an axis aligned box that bounds a single shape primitive after
        it has been clipped to another bounding box.
        
        This is extremely important to construct high-quality kd-trees. The
        default implementation just takes the bounding box returned by
        bbox(ScalarIndex index) and clips it to *clip*.
        """
        ...

    def bsdf(self: mitsuba.Shape):
        """
        Return the shape's BSDF
        """
        ...

    def compute_surface_interaction(self: mitsuba.Shape, ray: mitsuba.Ray3f, pi, ray_flags: int = 14, active: bool = True):
        """
        Compute and return detailed information related to a surface
        interaction
        
        The implementation should at most compute the fields ``p``, ``uv``,
        ``n``, ``sh_frame``.n, ``dp_du``, ``dp_dv``, ``dn_du`` and ``dn_dv``.
        The ``flags`` parameter specifies which of those fields should be
        computed.
        
        The fields ``t``, ``time``, ``wavelengths``, ``shape``,
        ``prim_index``, ``instance``, will already have been initialized by
        the caller. The field ``wi`` is initialized by the caller following
        the call to compute_surface_interaction(), and ``duv_dx``, and
        ``duv_dy`` are left uninitialized.
        
        Parameter ``ray``:
            Ray associated with the ray intersection
        
        Parameter ``pi``:
            Data structure carrying information about the ray intersection
        
        Parameter ``ray_flags``:
            Flags specifying which information should be computed
        
        Parameter ``recursion_depth``:
            Integer specifying the recursion depth for nested virtual function
            call to this method (e.g. used for instancing).
        
        Returns:
            A data structure containing the detailed information
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def differential_motion(self: mitsuba.Shape, si, active: bool = True) -> mitsuba.Point3f:
        """
        Return the attached (AD) point on the shape's surface
        
        This method is only useful when using automatic differentiation. The
        immediate/primal return value of this method is exactly equal to
        \`si.p\`.
        
        The input `si` does not need to be explicitly detached, it is done by
        the method itself.
        
        If the shape cannot be differentiated, this method will return the
        detached input point.
        
        note:: The returned attached point is exactly the same as a point
        which is computed by calling compute_surface_interaction with the
        RayFlags::FollowShape flag.
        
        Parameter ``si``:
            The surface point for which the function will be evaluated.
        
        Not all fields of the object need to be filled. Only the `prim_index`,
        `p` and `uv` fields are required. Certain shapes will only use a
        subset of these.
        
        Returns:
            The same surface point as the input but attached (AD) to the
            shape's parameters.
        """
        ...

    def effective_primitive_count(self: mitsuba.Shape) -> int:
        """
        Return the number of primitives (triangles, hairs, ..) contributed to
        the scene by this shape
        
        Includes instanced geometry. The default implementation simply returns
        the same value as primitive_count().
        """
        ...

    def emitter(self: mitsuba.Shape):
        """
        Return the area emitter associated with this shape (if any)
        """
        ...

    def eval_attribute(self: mitsuba.Shape, name: str, si, active: bool = True) -> mitsuba.Color3f:
        """
        Evaluate a specific shape attribute at the given surface interaction.
        
        Shape attributes are user-provided fields that provide extra
        information at an intersection. An example of this would be a per-
        vertex or per-face color on a triangle mesh.
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An unpolarized spectral power distribution or reflectance value
        """
        ...

    def eval_attribute_1(self: mitsuba.Shape, name: str, si, active: bool = True) -> float:
        """
        Monochromatic evaluation of a shape attribute at the given surface
        interaction
        
        This function differs from eval_attribute() in that it provided raw
        access to scalar intensity/reflectance values without any color
        processing (e.g. spectral upsampling).
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An scalar intensity or reflectance value
        """
        ...

    def eval_attribute_3(self: mitsuba.Shape, name: str, si, active: bool = True) -> mitsuba.Color3f:
        """
        Trichromatic evaluation of a shape attribute at the given surface
        interaction
        
        This function differs from eval_attribute() in that it provided raw
        access to RGB intensity/reflectance values without any additional
        color processing (e.g. RGB-to-spectral upsampling).
        
        Parameter ``name``:
            Name of the attribute to evaluate
        
        Parameter ``si``:
            Surface interaction associated with the query
        
        Returns:
            An trichromatic intensity or reflectance value
        """
        ...

    def eval_parameterization(self: mitsuba.Shape, uv: mitsuba.Point2f, ray_flags: int = 14, active: bool = True):
        """
        Parameterize the mesh using UV values
        
        This function maps a 2D UV value to a surface interaction data
        structure. Its behavior is only well-defined in regions where this
        mapping is bijective. The default implementation throws.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def exterior_medium(self: mitsuba.Shape):
        """
        Return the medium that lies on the exterior of this shape
        """
        ...

    def has_attribute(self: mitsuba.Shape, name: str, active: bool = True) -> bool:
        """
        Returns whether this shape contains the specified attribute.
        
        Parameter ``name``:
            Name of the attribute
        """
        ...

    def id(self: mitsuba.Shape) -> str:
        """
        Return a string identifier
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def interior_medium(self: mitsuba.Shape):
        """
        Return the medium that lies on the interior of this shape
        """
        ...

    def invert_silhouette_sample(self: mitsuba.Shape, ss, active: bool = True) -> mitsuba.Point3f:
        """
        Map a silhouette segment to a point in boundary sample space
        
        This method is the inverse of sample_silhouette(). The mapping from/to
        boundary sample space to/from boundary segments is bijective.
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``ss``:
            The sampled boundary segment
        
        Returns:
            The corresponding boundary sample space point
        """
        ...

    def is_emitter(self: mitsuba.Shape) -> bool:
        """
        Is this shape also an area emitter?
        """
        ...

    def is_medium_transition(self: mitsuba.Shape) -> bool:
        """
        Does the surface of this shape mark a medium transition?
        """
        ...

    def is_mesh(self: mitsuba.Shape) -> bool:
        """
        Is this shape a triangle mesh?
        """
        ...

    def is_sensor(self: mitsuba.Shape) -> bool:
        """
        Is this shape also an area sensor?
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def parameters_grad_enabled(self: mitsuba.Shape) -> bool:
        """
        Return whether any shape's parameters that introduce visibility
        discontinuities require gradients (default return false)
        """
        ...

    def pdf_direction(self: mitsuba.Shape, it, ps, active: bool = True) -> float:
        """
        Query the probability density of sample_direction()
        
        Parameter ``it``:
            A reference position somewhere within the scene.
        
        Parameter ``ps``:
            A position record describing the sample in question
        
        Returns:
            The probability density per unit solid angle
        """
        ...

    def pdf_position(self: mitsuba.Shape, ps, active: bool = True) -> float:
        """
        Query the probability density of sample_position() for a particular
        point on the surface.
        
        Parameter ``ps``:
            A position record describing the sample in question
        
        Returns:
            The probability density per unit area
        """
        ...

    def precompute_silhouette(self: mitsuba.Shape, viewpoint: mitsuba.Point3f) -> Tuple[mitsuba.ArrayXu, mitsuba.ArrayXf]:
        """
        Precompute the visible silhouette of this shape for a given viewpoint.
        
        This method is meant to be used for silhouettes that are shared
        between all threads, as is the case for primarily visible derivatives.
        
        The return values are respectively a list of indices and their
        corresponding weights. The semantic meaning of these indices is
        different for each shape. For example, a triangle mesh will return the
        indices of all of its edges that constitute its silhouette. These
        indices are meant to be re-used as an argument when calling
        sample_precomputed_silhouette.
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``viewpoint``:
            The viewpoint which defines the silhouette of the shape
        
        Returns:
            A list of indices used by the shape internally to represent
            silhouettes, and a list of the same length containing the
            (unnormalized) weights associated to each index.
        """
        ...

    def primitive_count(self: mitsuba.Shape) -> int:
        """
        Returns the number of sub-primitives that make up this shape
        
        Remark:
            The default implementation simply returns ``1``
        """
        ...

    def primitive_silhouette_projection(self: mitsuba.Shape, viewpoint: mitsuba.Point3f, si, flags: int, sample: float, active: bool = True):
        """
        Projects a point on the surface of the shape to its silhouette as seen
        from a specified viewpoint.
        
        This method only projects the `si.p` point within its primitive.
        
        Not all of the fields of the SilhouetteSample3f might be filled by
        this method. Each shape will at the very least fill its return value
        with enough information for it to be used by invert_silhouette_sample.
        
        The projection operation might not find the closest silhouette point
        to the given surface point. For example, it can be guided by a random
        number ``sample``. Not all shapes types need this random number, each
        shape implementation is free to define its own algorithm and
        guarantees about the projection operation.
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``viewpoint``:
            The viewpoint which defines the silhouette to project the point
            to.
        
        Parameter ``si``:
            The surface point which will be projected.
        
        Parameter ``flags``:
            Flags to select the type of SilhouetteSample3f to generate from
            the projection. Only one type of discontinuity can be used per
            call.
        
        Parameter ``sample``:
            A random number that can be used to define the projection
            operation.
        
        Returns:
            A boundary segment on the silhouette of the shape as seen from
            ``viewpoint``.
        """
        ...

    def ray_intersect(self: mitsuba.Shape, ray: mitsuba.Ray3f, ray_flags: int = 14, active: bool = True):
        """
        Test for an intersection and return detailed information
        
        This operation combines the prior ray_intersect_preliminary() and
        compute_surface_interaction() operations.
        
        Parameter ``ray``:
            The ray to be tested for an intersection
        
        Parameter ``flags``:
            Describe how the detailed information should be computed
        """
        ...

    def ray_intersect_preliminary(self: mitsuba.Shape, ray: mitsuba.Ray3f, prim_index: int = 0, active: bool = True):
        """
        Fast ray intersection
        
        Efficiently test whether the shape is intersected by the given ray,
        and return preliminary information about the intersection if that is
        the case.
        
        If the intersection is deemed relevant (e.g. the closest to the ray
        origin), detailed intersection information can later be obtained via
        the create_surface_interaction() method.
        
        Parameter ``ray``:
            The ray to be tested for an intersection
        
        Parameter ``prim_index``:
            Index of the primitive to be intersected. This index is ignored by
            a shape that contains a single primitive. Otherwise, if no index
            is provided, the ray intersection will be performed on the shape's
            first primitive at index 0.
        """
        ...

    def ray_test(self: mitsuba.Shape, ray: mitsuba.Ray3f, active: bool = True) -> bool:
        """
        Fast ray shadow test
        
        Efficiently test whether the shape is intersected by the given ray.
        
        No details about the intersection are returned, hence the function is
        only useful for visibility queries. For most shapes, the
        implementation will simply forward the call to
        ray_intersect_preliminary(). When the shape actually contains a nested
        kd-tree, some optimizations are possible.
        
        Parameter ``ray``:
            The ray to be tested for an intersection
        
        Parameter ``prim_index``:
            Index of the primitive to be intersected
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def sample_direction(self: mitsuba.Shape, it, sample: mitsuba.Point2f, active: bool = True):
        """
        Sample a direction towards this shape with respect to solid angles
        measured at a reference position within the scene
        
        An ideal implementation of this interface would achieve a uniform
        solid angle density within the surface region that is visible from the
        reference position ``it.p`` (though such an ideal implementation is
        usually neither feasible nor advisable due to poor efficiency).
        
        The function returns the sampled position and the inverse probability
        per unit solid angle associated with the sample.
        
        When the Shape subclass does not supply a custom implementation of
        this function, the Shape class reverts to a fallback approach that
        piggybacks on sample_position(). This will generally lead to a
        suboptimal sample placement and higher variance in Monte Carlo
        estimators using the samples.
        
        Parameter ``it``:
            A reference position somewhere within the scene.
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``
        
        Returns:
            A DirectionSample instance describing the generated sample
        """
        ...

    def sample_position(self: mitsuba.Shape, time: float, sample: mitsuba.Point2f, active: bool = True):
        """
        Sample a point on the surface of this shape
        
        The sampling strategy is ideally uniform over the surface, though
        implementations are allowed to deviate from a perfectly uniform
        distribution as long as this is reflected in the returned probability
        density.
        
        Parameter ``time``:
            The scene time associated with the position sample
        
        Parameter ``sample``:
            A uniformly distributed 2D point on the domain ``[0,1]^2``
        
        Returns:
            A PositionSample instance describing the generated sample
        """
        ...

    def sample_precomputed_silhouette(self: mitsuba.Shape, viewpoint: mitsuba.Point3f, sample1: int, sample2: float, active: bool = True):
        """
        Samples a boundary segement on the shape's silhouette using
        precomputed information computed in precompute_silhouette.
        
        This method is meant to be used for silhouettes that are shared
        between all threads, as is the case for primarily visible derivatives.
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``viewpoint``:
            The viewpoint that was used for the precomputed silhouette
            information
        
        Parameter ``sample1``:
            A sampled index from the return values of precompute_silhouette
        
        Parameter ``sample2``:
            A uniformly distributed sample in ``[0,1]``
        
        Returns:
            A boundary segment on the silhouette of the shape as seen from
            ``viewpoint``.
        """
        ...

    def sample_silhouette(self: mitsuba.Shape, sample: mitsuba.Point3f, flags: int, active: bool = True):
        """
        Map a point sample in boundary sample space to a silhouette segment
        
        This method's behavior is undefined when used in non-JIT variants or
        when the shape is not being differentiated.
        
        Parameter ``sample``:
            The boundary space sample (a point in the unit cube).
        
        Parameter ``flags``:
            Flags to select the type of silhouettes to sample from (see
            DiscontinuityFlags). Only one type of discontinuity can be sampled
            per call.
        
        Returns:
            Silhouette sample record.
        """
        ...

    def sensor(self: mitsuba.Shape):
        """
        Return the area sensor associated with this shape (if any)
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def shape_type(self: mitsuba.Shape) -> int:
        """
        Returns the shape type ShapeType of this shape
        """
        ...

    def silhouette_discontinuity_types(self: mitsuba.Shape) -> int:
        """
        //! @{ \name Silhouette sampling routines and other utilities
        """
        ...

    def silhouette_sampling_weight(self: mitsuba.Shape) -> float:
        """
        Return this shape's sampling weight w.r.t. all shapes in the scene
        """
        ...

    def surface_area(self: mitsuba.Shape) -> float:
        """
        Return the shape's surface area.
        
        The function assumes that the object is not undergoing some kind of
        time-dependent scaling.
        
        The default implementation throws an exception.
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class ShapeType:
    """
    Enumeration of all shape types in Mitsuba
    
    Members:
    
      Mesh : Meshes (`ply`, `obj`, `serialized`)
    
      BSplineCurve : B-Spline curves (`bsplinecurve`)
    
      Cylinder : Cylinders (`cylinder`)
    
      Disk : Disks (`disk`)
    
      LinearCurve : Linear curves (`linearcurve`)
    
      Rectangle : Rectangles (`rectangle`)
    
      SDFGrid : SDF Grids (`sdfgrid`)
    
      Sphere : Spheres (`sphere`)
    
      Other : Other shapes
    """

    def __init__(self: mitsuba.ShapeType, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    BSplineCurve = 1
    """
      BSplineCurve : B-Spline curves (`bsplinecurve`)
    """
    Cylinder = 2
    """
      Cylinder : Cylinders (`cylinder`)
    """
    Disk = 3
    """
      Disk : Disks (`disk`)
    """
    LinearCurve = 4
    """
      LinearCurve : Linear curves (`linearcurve`)
    """
    Mesh = 0
    """
      Mesh : Meshes (`ply`, `obj`, `serialized`)
    """
    Other = 9
    """
      Other : Other shapes
    """
    Rectangle = 5
    """
      Rectangle : Rectangles (`rectangle`)
    """
    SDFGrid = 6
    """
      SDFGrid : SDF Grids (`sdfgrid`)
    """
    Sphere = 7
    """
      Sphere : Spheres (`sphere`)
    """

    ...

class SilhouetteSample3f(PositionSample3f):
    """
    Data structure holding the result of visibility silhouette sampling
    operations on geometry.
    """

    @overload
    def __init__(self: mitsuba.SilhouetteSample3f) -> None:
        """
        Construct an uninitialized silhouette sample
        
        """
        ...

    @overload
    def __init__(self: mitsuba.SilhouetteSample3f, other: mitsuba.SilhouetteSample3f) -> None:
        """
        Copy constructor
        """
        ...

    d = ...
    "Direction of the boundary segment sample"
    delta = ...
    """
    Set if the sample was drawn from a degenerate (Dirac delta)
    distribution
    """
    discontinuity_type = ...
    "Type of discontinuity (DiscontinuityFlags)"
    flags = ...
    """
    The set of ``DiscontinuityFlags`` that were used to generate this
    sample
    """
    foreshortening = ...
    """
    Local-form boundary foreshortening term.
    
    It stores `sin_phi_B` for perimeter silhouettes or the normal
    curvature for interior silhouettes.
    """
    n = ...
    "Sampled surface normal (if applicable)"
    offset = ...
    """
    Offset along the boundary segment direction (`d`) to avoid self-
    intersections.
    """
    p = ...
    "Sampled position"
    pdf = ...
    "Probability density at the sample"
    prim_index = ...
    "Primitive index, e.g. the triangle ID (if applicable)"
    projection_index = ...
    """
    Projection index indicator
    
    For primitives like triangle meshes, a boundary segment is defined not
    only by the triangle index but also the edge index of the selected
    triangle. A value larger than 3 indicates a failed projection. For
    other primitives, zero indicates a failed projection.
    
    For triangle meshes, index 0 stands for the directed edge p0->p1 (not
    the opposite edge p1->p2), index 1 stands for the edge p1->p2, and
    index 2 for p2->p0.
    """
    scene_index = ...
    "Index of the shape in the scene (if applicable)"
    shape = ...
    "Pointer to the associated shape"
    silhouette_d = ...
    "Direction of the silhouette curve at the boundary point"
    time = ...
    "Associated time value"
    uv = ...
    """
    Optional: 2D sample position associated with the record
    
    In some uses of this record, a sampled position may be associated with
    an important 2D quantity, such as the texture coordinates on a
    triangle mesh or a position on the aperture of a sensor. When
    applicable, such positions are stored in the ``uv`` attribute.
    """

    def assign(self: mitsuba.SilhouetteSample3f, arg0: mitsuba.SilhouetteSample3f) -> None: ...
    def is_valid(self: mitsuba.SilhouetteSample3f) -> bool:
        """
        Is the current boundary segment valid=
        """
        ...

    def spawn_ray(self: mitsuba.SilhouetteSample3f) -> mitsuba.Ray3f:
        """
        Spawn a ray on the silhouette point in the direction of d
        
        The ray origin is offset in the direction of the segment (d) aswell as
        in the in the direction of the silhouette normal (n). Without this
        offsetting, during a ray intersection, the ray could potentially find
        an intersection point at its origin due to numerical instabilities in
        the intersection routines.
        """
        ...

    ...

class Spiral(Object):
    """
    Generates a spiral of blocks to be rendered.
    
    Author:
        Adam Arbree Aug 25, 2005 RayTracer.java Used with permission.
        Copyright 2005 Program of Computer Graphics, Cornell University
    """

    def __init__(self: mitsuba.Spiral, size, offset, block_size: int = 32, passes: int = 1) -> None:
        """
        Create a new spiral generator for the given size, offset into a larger
        frame, and block size
        """
        ...

    ptr = ...

    def block_count(self: mitsuba.Spiral) -> int:
        """
        Return the total number of blocks
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def max_block_size(self: mitsuba.Spiral) -> int:
        """
        Return the maximum block size
        """
        ...

    def next_block(self: mitsuba.Spiral):
        """
        Return the offset, size, and unique identifier of the next block.
        
        A size of zero indicates that the spiral traversal is done.
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def reset(self: mitsuba.Spiral) -> None:
        """
        Reset the spiral to its initial state. Does not affect the number of
        passes.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Stream(Object):
    """
    Abstract seekable stream class
    
    Specifies all functions to be implemented by stream subclasses and
    provides various convenience functions layered on top of on them.
    
    All ``read*()`` and ``write*()`` methods support transparent
    conversion based on the endianness of the underlying system and the
    value passed to set_byte_order(). Whenever host_byte_order() and
    byte_order() disagree, the endianness is swapped.
    
    See also:
        FileStream, MemoryStream, DummyStream
    """

    class EByteOrder:
        """
        Defines the byte order (endianness) to use in this Stream
        
        Members:
        
          EBigEndian : 
        
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        
          ENetworkByteOrder : x86, x86_64
        """

        def __init__(self: mitsuba.Stream.EByteOrder, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        EBigEndian = 0
        """
          EBigEndian : 
        """
        ELittleEndian = 1
        """
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        """

        ...

    ptr = ...

    EBigEndian = 0
    """
      EBigEndian : 
    """
    ELittleEndian = 1
    """
      ELittleEndian : PowerPC, SPARC, Motorola 68K
    """

    def byte_order(self: mitsuba.Stream) -> mitsuba.Stream.EByteOrder:
        """
        Returns the byte order of this stream.
        """
        ...

    def can_read(self: mitsuba.Stream) -> bool:
        """
        Can we read from the stream?
        """
        ...

    def can_write(self: mitsuba.Stream) -> bool:
        """
        Can we write to the stream?
        """
        ...

    def close(self: mitsuba.Stream) -> None:
        """
        Closes the stream.
        
        No further read or write operations are permitted.
        
        This function is idempotent. It may be called automatically by the
        destructor.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def flush(self: mitsuba.Stream) -> None:
        """
        Flushes the stream's buffers, if any
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def read(self: mitsuba.Stream, arg0: int) -> bytes:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def read_bool(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_double(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_float(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_line(self: mitsuba.Stream) -> str:
        """
        Convenience function for reading a line of text from an ASCII file
        """
        ...

    def read_single(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_string(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def seek(self: mitsuba.Stream, arg0: int) -> None:
        """
        Seeks to a position inside the stream.
        
        Seeking beyond the size of the buffer will not modify the length of
        its contents. However, a subsequent write should start at the sought
        position and update the size appropriately.
        """
        ...

    def set_byte_order(self: mitsuba.Stream, arg0: mitsuba.Stream.EByteOrder) -> None:
        """
        Sets the byte order to use in this stream.
        
        Automatic conversion will be performed on read and write operations to
        match the system's native endianness.
        
        No consistency is guaranteed if this method is called after performing
        some read and write operations on the system using a different
        endianness.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def size(self: mitsuba.Stream) -> int:
        """
        Returns the size of the stream
        """
        ...

    def skip(self: mitsuba.Stream, arg0: int) -> None:
        """
        Skip ahead by a given number of bytes
        """
        ...

    def tell(self: mitsuba.Stream) -> int:
        """
        Gets the current position inside the stream
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def truncate(self: mitsuba.Stream, arg0: int) -> None:
        """
        Truncates the stream to a given size.
        
        The position is updated to ``min(old_position, size)``. Throws an
        exception if in read-only mode.
        """
        ...

    def write(self: mitsuba.Stream, arg0: bytes) -> None:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def write_bool(self: mitsuba.Stream, arg0: bool) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_double(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_float(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_line(self: mitsuba.Stream, arg0: str) -> None:
        """
        Convenience function for writing a line of text to an ASCII file
        """
        ...

    def write_single(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_string(self: mitsuba.Stream, arg0: str) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    ...

class StreamAppender(Appender):
    """
    %Appender implementation, which writes to an arbitrary C++ output
    stream
    """

    def __init__(self: mitsuba.StreamAppender, arg0: str) -> None:
        """
        Create a new stream appender
        
        Remark:
            This constructor is not exposed in the Python bindings
        """
        ...

    ptr = ...

    def append(self: mitsuba.Appender, level: mitsuba.LogLevel, text: str) -> None:
        """
        Append a line of text with the given log level
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def log_progress(self: mitsuba.Appender, progress: float, name: str, formatted: str, eta: str, ptr: capsule = None) -> None:
        """
        Process a progress message
        
        Parameter ``progress``:
            Percentage value in [0, 100]
        
        Parameter ``name``:
            Title of the progress message
        
        Parameter ``formatted``:
            Formatted string representation of the message
        
        Parameter ``eta``:
            Estimated time until 100% is reached.
        
        Parameter ``ptr``:
            Custom pointer payload. This is used to express the context of a
            progress message. When rendering a scene, it will usually contain
            a pointer to the associated ``RenderJob``.
        """
        ...

    def logs_to_file(self: mitsuba.StreamAppender) -> bool:
        """
        Does this appender log to a file
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def read_log(self: mitsuba.StreamAppender) -> str:
        """
        Return the contents of the log file as a string
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class Struct(Object):
    """
    Descriptor for specifying the contents and in-memory layout of a POD-
    style data record
    
    Remark:
        The python API provides an additional ``dtype()`` method, which
        returns the NumPy ``dtype`` equivalent of a given ``Struct``
        instance.
    """

    def __init__(self: mitsuba.Struct, pack: bool = False, byte_order: mitsuba.Struct.ByteOrder = ByteOrder.HostByteOrder) -> None:
        """
        Create a new ``Struct`` and indicate whether the contents are packed
        or aligned
        """
        ...

    class ByteOrder:
        """
        Members:
        
          LittleEndian : 
        
          BigEndian : 
        
          HostByteOrder : 
        """

        def __init__(self: mitsuba.Struct.ByteOrder, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        BigEndian = 1
        """
          BigEndian : 
        """
        HostByteOrder = 2
        """
          HostByteOrder : 
        """
        LittleEndian = 0
        """
          LittleEndian : 
        """

        ...

    class Field:
        """
        Field specifier with size and offset
        """

        blend = ...
        """
        For use with StructConverter::convert()
        
        Specifies a pair of weights and source field names that will be
        linearly blended to obtain the output field value. Note that this only
        works for floating point fields or integer fields with the
        Flags::Normalized flag. Gamma-corrected fields will be blended in
        linear space.
        """
        flags = ...
        "Additional flags"
        name = ...
        "Name of the field"
        offset = ...
        "Offset within the ``Struct`` (in bytes)"
        size = ...
        "Size in bytes"
        type = ...
        "Type identifier"

        def is_float(self: mitsuba.Struct.Field) -> bool: ...
        def is_integer(self: mitsuba.Struct.Field) -> bool: ...
        def is_signed(self: mitsuba.Struct.Field) -> bool: ...
        def is_unsigned(self: mitsuba.Struct.Field) -> bool: ...
        def range(self: mitsuba.Struct.Field) -> Tuple[float, float]: ...
        ...

    class Flags:
        """
        Members:
        
          Empty : No flags set (default value)
        
          Normalized : Specifies whether an integer field encodes a normalized value in the
        range [0, 1]. The flag is ignored if specified for floating point
        valued fields.
        
          Gamma : Specifies whether the field encodes a sRGB gamma-corrected value.
        Assumes ``Normalized`` is also specified.
        
          Weight : In FieldConverter::convert, when an input structure contains a weight
        field, the value of all entries are considered to be expressed
        relative to its value. Converting to an un-weighted structure entails
        a division by the weight.
        
          Assert : In FieldConverter::convert, check that the field value matches the
        specified default value. Otherwise, return a failure
        
          Alpha : Specifies whether the field encodes an alpha value
        
          PremultipliedAlpha : Specifies whether the field encodes an alpha premultiplied value
        
          Default : In FieldConverter::convert, when the field is missing in the source
        record, replace it by the specified default value
        """

        def __init__(self: mitsuba.Struct.Flags, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        Alpha = 64
        """
          Alpha : Specifies whether the field encodes an alpha value
        """
        Assert = 4
        """
          Assert : In FieldConverter::convert, check that the field value matches the
        """
        Default = 8
        """
          Default : In FieldConverter::convert, when the field is missing in the source
        """
        Empty = 0
        """
          Empty : No flags set (default value)
        """
        Gamma = 2
        """
          Gamma : Specifies whether the field encodes a sRGB gamma-corrected value.
        """
        Normalized = 1
        """
          Normalized : Specifies whether an integer field encodes a normalized value in the
        """
        PremultipliedAlpha = 32
        """
          PremultipliedAlpha : Specifies whether the field encodes an alpha premultiplied value
        """
        Weight = 16
        """
          Weight : In FieldConverter::convert, when an input structure contains a weight
        """

        ...

    class Type:
        """
        Members:
        
          Int8 : 
        
          UInt8 : 
        
          Int16 : 
        
          UInt16 : 
        
          Int32 : 
        
          UInt32 : 
        
          Int64 : 
        
          UInt64 : 
        
          Float16 : 
        
          Float32 : 
        
          Float64 : 
        
          Invalid : 
        """

        @overload
        def __init__(self: mitsuba.Struct.Type, value: int) -> None: ...
        @overload
        def __init__(self: mitsuba.Struct.Type, dtype: dtype) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        Float16 = 9
        """
          Float16 : 
        """
        Float32 = 10
        """
          Float32 : 
        """
        Float64 = 11
        """
          Float64 : 
        """
        Int16 = 4
        """
          Int16 : 
        """
        Int32 = 6
        """
          Int32 : 
        """
        Int64 = 8
        """
          Int64 : 
        """
        Int8 = 2
        """
          Int8 : 
        """
        Invalid = 0
        """
          Invalid : 
        """
        UInt16 = 3
        """
          UInt16 : 
        """
        UInt32 = 5
        """
          UInt32 : 
        """
        UInt64 = 7
        """
          UInt64 : 
        """
        UInt8 = 1
        """
          UInt8 : 
        """

        ...

    ptr = ...

    def alignment(self: mitsuba.Struct) -> int:
        """
        Return the alignment (in bytes) of the data structure
        """
        ...

    def append(self: mitsuba.Struct, name: str, type: mitsuba.Struct.Type, flags: int = Flags.Empty, default: float = 0.0) -> mitsuba.Struct:
        """
        Append a new field to the ``Struct``; determines size and offset
        automatically
        """
        ...

    def byte_order(self: mitsuba.Struct) -> mitsuba.Struct.ByteOrder:
        """
        Return the byte order of the ``Struct``
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def dtype(self: mitsuba.Struct) -> dtype:
        """
        Return a NumPy dtype corresponding to this data structure
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def field(self: mitsuba.Struct, arg0: str) -> mitsuba.Struct.Field:
        """
        Look up a field by name (throws an exception if not found)
        """
        ...

    def field_count(self: mitsuba.Struct) -> int:
        """
        Return the number of fields
        """
        ...

    def has_field(self: mitsuba.Struct, arg0: str) -> bool:
        """
        Check if the ``Struct`` has a field of the specified name
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def size(self: mitsuba.Struct) -> int:
        """
        Return the size (in bytes) of the data structure, including padding
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class StructConverter(Object):
    """
    This class solves the any-to-any problem: efficiently converting from
    one kind of structured data representation to another
    
    Graphics applications often need to convert from one kind of
    structured representation to another, for instance when loading/saving
    image or mesh data. Consider the following data records which both
    describe positions tagged with color data.
    
    ```
    struct Source { // <-- Big endian! :(
       uint8_t r, g, b; // in sRGB
       half x, y, z;
    };
    
    struct Target { // <-- Little endian!
       float x, y, z;
       float r, g, b, a; // in linear space
    };
    ```
    
    The record ``Source`` may represent what is stored in a file on disk,
    while ``Target`` represents the expected input of the implementation.
    Not only are the formats (e.g. float vs half or uint8_t, incompatible
    endianness) and encodings different (e.g. gamma correction vs linear
    space), but the second record even has a different order and extra
    fields that don't exist in the first one.
    
    This class provides a routine convert() which <ol>
    
    * reorders entries
    
    * converts between many different formats (u[int]8-64, float16-64)
    
    * performs endianness conversion
    
    * applies or removes gamma correction
    
    * optionally checks that certain entries have expected default values
    
    * substitutes missing values with specified defaults
    
    * performs linear transformations of groups of fields (e.g. between
    different RGB color spaces)
    
    * applies dithering to avoid banding artifacts when converting 2D
    images
    
    </ol>
    
    The above operations can be arranged in countless ways, which makes it
    hard to provide an efficient generic implementation of this
    functionality. For this reason, the implementation of this class
    relies on a JIT compiler that generates fast conversion code on demand
    for each specific conversion. The function is cached and reused in
    case the same conversion is needed later on. Note that JIT compilation
    only works on x86_64 processors; other platforms use a slow generic
    fallback implementation.
    """

    def __init__(self: mitsuba.StructConverter, source: mitsuba.Struct, target: mitsuba.Struct, dither: bool = False) -> None: ...
    ptr = ...

    def convert(self: mitsuba.StructConverter, arg0: bytes) -> bytes: ...
    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def source(self: mitsuba.StructConverter) -> mitsuba.Struct:
        """
        Return the source ``Struct`` descriptor
        """
        ...

    def target(self: mitsuba.StructConverter) -> mitsuba.Struct:
        """
        Return the target ``Struct`` descriptor
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class SurfaceInteraction3f(Interaction3f):
    """
    Stores information related to a surface scattering interaction
    """

    @overload
    def __init__(self: mitsuba.SurfaceInteraction3f) -> None:
        """
        Construct from a position sample. Unavailable fields such as `wi` and
        the partial derivatives are left uninitialized. The `shape` pointer is
        left uninitialized because we can't guarantee that the given
        PositionSample::object points to a Shape instance.
        
        """
        ...

    @overload
    def __init__(self: mitsuba.SurfaceInteraction3f, arg0: mitsuba.SurfaceInteraction3f) -> None:
        """
        Copy constructor
        
        """
        ...

    @overload
    def __init__(self: mitsuba.SurfaceInteraction3f, ps, wavelengths: mitsuba.Color0f) -> None:
        """
        Construct from a position sample. Unavailable fields such as `wi` and
        the partial derivatives are left uninitialized. The `shape` pointer is
        left uninitialized because we can't guarantee that the given
        PositionSample::object points to a Shape instance.
        """
        ...

    dn_du = ...
    "Normal partials wrt. the UV parameterization"
    dn_dv = ...
    "Normal partials wrt. the UV parameterization"
    dp_du = ...
    "Position partials wrt. the UV parameterization"
    dp_dv = ...
    "Position partials wrt. the UV parameterization"
    duv_dx = ...
    "UV partials wrt. changes in screen-space"
    duv_dy = ...
    "UV partials wrt. changes in screen-space"
    instance = ...
    "Stores a pointer to the parent instance (if applicable)"
    n = ...
    "Geometric normal (only valid for ``SurfaceInteraction``)"
    p = ...
    "Position of the interaction in world coordinates"
    prim_index = ...
    "Primitive index, e.g. the triangle ID (if applicable)"
    sh_frame = ...
    "Shading frame"
    shape = ...
    "Pointer to the associated shape"
    t = ...
    "Distance traveled along the ray"
    time = ...
    "Time value associated with the interaction"
    uv = ...
    "UV surface coordinates"
    wavelengths = ...
    "Wavelengths associated with the ray that produced this interaction"
    wi = ...
    "Incident direction in the local shading frame"

    def assign(self: mitsuba.SurfaceInteraction3f, arg0: mitsuba.SurfaceInteraction3f) -> None: ...
    @overload
    def bsdf(self: mitsuba.SurfaceInteraction3f, ray: mitsuba.RayDifferential3f):
        """
        Returns the BSDF of the intersected shape.
        
        The parameter ``ray`` must match the one used to create the
        interaction record. This function computes texture coordinate partials
        if this is required by the BSDF (e.g. for texture filtering).
        
        Implementation in 'bsdf.h'
        
        """
        ...

    @overload
    def bsdf(self: mitsuba.SurfaceInteraction3f): ...
    def compute_uv_partials(self: mitsuba.SurfaceInteraction3f, ray: mitsuba.RayDifferential3f) -> None:
        """
        Computes texture coordinate partials
        """
        ...

    def emitter(self: mitsuba.SurfaceInteraction3f, scene: mitsuba.Scene, active: bool = True) -> mitsuba.Emitter:
        """
        Return the emitter associated with the intersection (if any) \note
        Defined in scene.h
        """
        ...

    def has_n_partials(self: mitsuba.SurfaceInteraction3f) -> bool: ...
    def has_uv_partials(self: mitsuba.SurfaceInteraction3f) -> bool: ...
    def initialize_sh_frame(self: mitsuba.SurfaceInteraction3f) -> None:
        """
        Initialize local shading frame using Gram-schmidt orthogonalization
        """
        ...

    def is_medium_transition(self: mitsuba.SurfaceInteraction3f) -> bool:
        """
        Does the surface mark a transition between two media?
        """
        ...

    def is_sensor(self: mitsuba.SurfaceInteraction3f) -> bool:
        """
        Is the intersected shape also a sensor?
        """
        ...

    def is_valid(self: mitsuba.Interaction3f) -> bool:
        """
        Is the current interaction valid?
        """
        ...

    def spawn_ray(self: mitsuba.Interaction3f, d: mitsuba.Vector3f) -> mitsuba.Ray3f:
        """
        Spawn a semi-infinite ray towards the given direction
        """
        ...

    def spawn_ray_to(self: mitsuba.Interaction3f, t: mitsuba.Point3f) -> mitsuba.Ray3f:
        """
        Spawn a finite ray towards the given position
        """
        ...

    @overload
    def target_medium(self: mitsuba.SurfaceInteraction3f, d: mitsuba.Vector3f) -> mitsuba.Medium:
        """
        Determine the target medium
        
        When ``is_medium_transition()`` = ``True``, determine the medium that
        contains the ``ray(this->p, d)``
        
        """
        ...

    @overload
    def target_medium(self: mitsuba.SurfaceInteraction3f, cos_theta: float) -> mitsuba.Medium:
        """
        Determine the target medium based on the cosine of the angle between
        the geometric normal and a direction
        
        Returns the exterior medium when ``cos_theta > 0`` and the interior
        medium when ``cos_theta <= 0``.
        """
        ...

    def to_local(self: mitsuba.SurfaceInteraction3f, v: mitsuba.Vector3f) -> mitsuba.Vector3f:
        """
        Convert a world-space vector into local shading coordinates
        """
        ...

    def to_local_mueller(self: mitsuba.SurfaceInteraction3f, M_world: mitsuba.Color3f, wi_world: mitsuba.Vector3f, wo_world: mitsuba.Vector3f) -> mitsuba.Color3f:
        """
        Converts a Mueller matrix defined in world space to a local frame
        
        A Mueller matrix operates from the (implicitly) defined frame
        stokes_basis(in_forward) to the frame stokes_basis(out_forward). This
        method converts a Mueller matrix defined on directions in world-space
        to a Mueller matrix defined in the local frame.
        
        This expands to a no-op in non-polarized modes.
        
        Parameter ``in_forward_local``:
            Incident direction (along propagation direction of light), given
            in world-space coordinates.
        
        Parameter ``wo_local``:
            Outgoing direction (along propagation direction of light), given
            in world-space coordinates.
        
        Returns:
            Equivalent Mueller matrix that operates in local frame
            coordinates.
        """
        ...

    def to_world(self: mitsuba.SurfaceInteraction3f, v: mitsuba.Vector3f) -> mitsuba.Vector3f:
        """
        Convert a local shading-space vector into world space
        """
        ...

    def to_world_mueller(self: mitsuba.SurfaceInteraction3f, M_local: mitsuba.Color3f, wi_local: mitsuba.Vector3f, wo_local: mitsuba.Vector3f) -> mitsuba.Color3f:
        """
        Converts a Mueller matrix defined in a local frame to world space
        
        A Mueller matrix operates from the (implicitly) defined frame
        stokes_basis(in_forward) to the frame stokes_basis(out_forward). This
        method converts a Mueller matrix defined on directions in the local
        frame to a Mueller matrix defined on world-space directions.
        
        This expands to a no-op in non-polarized modes.
        
        Parameter ``M_local``:
            The Mueller matrix in local space, e.g. returned by a BSDF.
        
        Parameter ``in_forward_local``:
            Incident direction (along propagation direction of light), given
            in local frame coordinates.
        
        Parameter ``wo_local``:
            Outgoing direction (along propagation direction of light), given
            in local frame coordinates.
        
        Returns:
            Equivalent Mueller matrix that operates in world-space
            coordinates.
        """
        ...

    ...

class TensorXb:
    @overload
    def __init__(self: mitsuba.TensorXb) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXb, array: object) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXb, array: mitsuba.ArrayXb) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXb, array: mitsuba.ArrayXb, shape: List[int]) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXb, arg0: mitsuba.TensorXb) -> None: ...
    array = ...
    label = ...
    ndim = ...
    shape = ...

    def assign(self: mitsuba.TensorXb, arg0: mitsuba.TensorXb) -> None: ...
    ...

class TensorXf64:
    @overload
    def __init__(self: mitsuba.TensorXf64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, array: object) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, array: mitsuba.ArrayXf64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, array: mitsuba.ArrayXf64, shape: List[int]) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, arg0: mitsuba.TensorXi) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, arg0: mitsuba.TensorXu) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, arg0: mitsuba.TensorXi64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, arg0: mitsuba.TensorXu64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, arg0: mitsuba.TensorXf) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf64, arg0: mitsuba.TensorXf64) -> None: ...
    array = ...
    label = ...
    ndim = ...
    shape = ...

    def assign(self: mitsuba.TensorXf64, arg0: mitsuba.TensorXf64) -> None: ...
    ...

class TensorXf:
    @overload
    def __init__(self: mitsuba.TensorXf) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, array: object) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, array: mitsuba.ArrayXf) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, array: mitsuba.ArrayXf, shape: List[int]) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, arg0: mitsuba.TensorXi) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, arg0: mitsuba.TensorXu) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, arg0: mitsuba.TensorXi64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, arg0: mitsuba.TensorXu64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, arg0: mitsuba.TensorXf) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXf, arg0: mitsuba.TensorXf64) -> None: ...
    array = ...
    label = ...
    ndim = ...
    shape = ...

    def assign(self: mitsuba.TensorXf, arg0: mitsuba.TensorXf) -> None: ...
    ...

class TensorXi:
    @overload
    def __init__(self: mitsuba.TensorXi) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, array: object) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, array: mitsuba.ArrayXi) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, array: mitsuba.ArrayXi, shape: List[int]) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, arg0: mitsuba.TensorXi) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, arg0: mitsuba.TensorXu) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, arg0: mitsuba.TensorXi64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, arg0: mitsuba.TensorXu64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, arg0: mitsuba.TensorXf) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi, arg0: mitsuba.TensorXf64) -> None: ...
    array = ...
    label = ...
    ndim = ...
    shape = ...

    def assign(self: mitsuba.TensorXi, arg0: mitsuba.TensorXi) -> None: ...
    ...

class TensorXi64:
    @overload
    def __init__(self: mitsuba.TensorXi64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, array: object) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, array: mitsuba.ArrayXi64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, array: mitsuba.ArrayXi64, shape: List[int]) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, arg0: mitsuba.TensorXi) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, arg0: mitsuba.TensorXu) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, arg0: mitsuba.TensorXi64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, arg0: mitsuba.TensorXu64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, arg0: mitsuba.TensorXf) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXi64, arg0: mitsuba.TensorXf64) -> None: ...
    array = ...
    label = ...
    ndim = ...
    shape = ...

    def assign(self: mitsuba.TensorXi64, arg0: mitsuba.TensorXi64) -> None: ...
    ...

class TensorXu:
    @overload
    def __init__(self: mitsuba.TensorXu) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, array: object) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, array: mitsuba.ArrayXu) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, array: mitsuba.ArrayXu, shape: List[int]) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, arg0: mitsuba.TensorXi) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, arg0: mitsuba.TensorXu) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, arg0: mitsuba.TensorXi64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, arg0: mitsuba.TensorXu64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, arg0: mitsuba.TensorXf) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu, arg0: mitsuba.TensorXf64) -> None: ...
    array = ...
    label = ...
    ndim = ...
    shape = ...

    def assign(self: mitsuba.TensorXu, arg0: mitsuba.TensorXu) -> None: ...
    ...

class TensorXu64:
    @overload
    def __init__(self: mitsuba.TensorXu64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, array: object) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, array: mitsuba.ArrayXu64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, array: mitsuba.ArrayXu64, shape: List[int]) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, arg0: mitsuba.TensorXi) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, arg0: mitsuba.TensorXu) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, arg0: mitsuba.TensorXi64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, arg0: mitsuba.TensorXu64) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, arg0: mitsuba.TensorXf) -> None: ...
    @overload
    def __init__(self: mitsuba.TensorXu64, arg0: mitsuba.TensorXf64) -> None: ...
    array = ...
    label = ...
    ndim = ...
    shape = ...

    def assign(self: mitsuba.TensorXu64, arg0: mitsuba.TensorXu64) -> None: ...
    ...

class Texture(Object):
    """
    Base class of all surface texture implementations
    
    This class implements a generic texture map that supports evaluation
    at arbitrary surface positions and wavelengths (if compiled in
    spectral mode). It can be used to provide both intensities (e.g. for
    light sources) and unitless reflectance parameters (e.g. an albedo of
    a reflectance model).
    
    The spectrum can be evaluated at arbitrary (continuous) wavelengths,
    though the underlying function it is not required to be smooth or even
    continuous.
    """

    def __init__(self: mitsuba.Texture, props: mitsuba.Properties) -> None: ...
    ptr = ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.Texture, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Evaluate the texture at the given surface interaction
        
        Parameter ``si``:
            An interaction record describing the associated surface position
        
        Returns:
            An unpolarized spectral power distribution or reflectance value
        """
        ...

    def eval_1(self: mitsuba.Texture, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> float:
        """
        Monochromatic evaluation of the texture at the given surface
        interaction
        
        This function differs from eval() in that it provided raw access to
        scalar intensity/reflectance values without any color processing (e.g.
        spectral upsampling). This is useful in parts of the renderer that
        encode scalar quantities using textures, e.g. a height field.
        
        Parameter ``si``:
            An interaction record describing the associated surface position
        
        Returns:
            An scalar intensity or reflectance value
        """
        ...

    def eval_1_grad(self: mitsuba.Texture, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Vector2f:
        """
        Monochromatic evaluation of the texture gradient at the given surface
        interaction
        
        Parameter ``si``:
            An interaction record describing the associated surface position
        
        Returns:
            A (u,v) pair of intensity or reflectance value gradients
        """
        ...

    def eval_3(self: mitsuba.Texture, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Trichromatic evaluation of the texture at the given surface
        interaction
        
        This function differs from eval() in that it provided raw access to
        RGB intensity/reflectance values without any additional color
        processing (e.g. RGB-to-spectral upsampling). This is useful in parts
        of the renderer that encode 3D quantities using textures, e.g. a
        normal map.
        
        Parameter ``si``:
            An interaction record describing the associated surface position
        
        Returns:
            An trichromatic intensity or reflectance value
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def is_spatially_varying(self: mitsuba.Texture) -> bool:
        """
        Does this texture evaluation depend on the UV coordinates
        """
        ...

    def max(self: mitsuba.Texture) -> float:
        """
        Return the maximum value of the spectrum
        
        Not every implementation necessarily provides this function. The
        default implementation throws an exception.
        
        Even if the operation is provided, it may only return an
        approximation.
        """
        ...

    def mean(self: mitsuba.Texture) -> float:
        """
        Return the mean value of the spectrum over the support
        (MI_WAVELENGTH_MIN..MI_WAVELENGTH_MAX)
        
        Not every implementation necessarily provides this function. The
        default implementation throws an exception.
        
        Even if the operation is provided, it may only return an
        approximation.
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def pdf_position(self: mitsuba.Texture, p: mitsuba.Point2f, active: bool = True) -> float:
        """
        Returns the probability per unit area of sample_position()
        """
        ...

    def pdf_spectrum(self: mitsuba.Texture, si: mitsuba.SurfaceInteraction3f, active: bool = True) -> mitsuba.Color0f:
        """
        Evaluate the density function of the sample_spectrum() method as a
        probability per unit wavelength (in units of 1/nm).
        
        Not every implementation necessarily overrides this function. The
        default implementation throws an exception.
        
        Parameter ``si``:
            An interaction record describing the associated surface position
        
        Returns:
            A density value for each wavelength in ``si.wavelengths`` (hence
            the Wavelength type).
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def resolution(self: mitsuba.Texture) -> mitsuba.Vector2i:
        """
        Returns the resolution of the texture, assuming that it is based on a
        discrete representation.
        
        The default implementation returns ``(1, 1)``
        """
        ...

    def sample_position(self: mitsuba.Texture, sample: mitsuba.Point2f, active: bool = True) -> Tuple[mitsuba.Point2f, float]:
        """
        Importance sample a surface position proportional to the overall
        spectral reflectance or intensity of the texture
        
        This function assumes that the texture is implemented as a mapping
        from 2D UV positions to texture values, which is not necessarily true
        for all textures (e.g. 3D noise functions, mesh attributes, etc.). For
        this reason, not every will plugin provide a specialized
        implementation, and the default implementation simply return the input
        sample (i.e. uniform sampling is used).
        
        Parameter ``sample``:
            A 2D vector of uniform variates
        
        Returns:
            1. A texture-space position in the range :math:`[0, 1]^2`
        
        2. The associated probability per unit area in UV space
        """
        ...

    def sample_spectrum(self: mitsuba.Texture, si: mitsuba.SurfaceInteraction3f, sample: mitsuba.Color0f, active: bool = True) -> Tuple[mitsuba.Color0f, mitsuba.Color3f]:
        """
        Importance sample a set of wavelengths proportional to the spectrum
        defined at the given surface position
        
        Not every implementation necessarily provides this function, and it is
        a no-op when compiling non-spectral variants of Mitsuba. The default
        implementation throws an exception.
        
        Parameter ``si``:
            An interaction record describing the associated surface position
        
        Parameter ``sample``:
            A uniform variate for each desired wavelength.
        
        Returns:
            1. Set of sampled wavelengths specified in nanometers
        
        2. The Monte Carlo importance weight (Spectral power distribution
        value divided by the sampling density)
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def spectral_resolution(self: mitsuba.Texture) -> float:
        """
        Returns the resolution of the spectrum in nanometers (if discretized)
        
        Not every implementation necessarily provides this function. The
        default implementation throws an exception.
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def wavelength_range(self: mitsuba.Texture) -> mitsuba.Vector2f:
        """
        Returns the range of wavelengths covered by the spectrum
        
        The default implementation returns ``(MI_CIE_MIN, MI_CIE_MAX)``
        """
        ...

    ...

class Texture1f64:
    @overload
    def __init__(self: mitsuba.Texture1f64, shape: List[int[1]], channels: int, use_accel: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    @overload
    def __init__(self: mitsuba.Texture1f64, tensor, use_accel: bool = True, migrate: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    shape = ...

    def eval(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True) -> List[float]: ...
    def eval_cubic(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True, force_drjit: bool = False) -> List[float]: ...
    def eval_cubic_grad(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True) -> Tuple[List[float], List[mitsuba.Array1f64]]: ...
    def eval_cubic_hessian(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True): ...
    def eval_cuda(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True) -> List[float]: ...
    def eval_fetch(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True) -> List[List[float][2]]: ...
    def eval_fetch_cuda(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True) -> List[List[float][2]]: ...
    def eval_fetch_drjit(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True) -> List[List[float][2]]: ...
    def eval_nonaccel(self: mitsuba.Texture1f64, pos: mitsuba.Array1f64, active: bool = True) -> List[float]: ...
    def filter_mode(self: mitsuba.Texture1f64) -> drjit.FilterMode: ...
    def migrated(self: mitsuba.Texture1f64) -> bool: ...
    def set_tensor(self: mitsuba.Texture1f64, tensor, migrate: bool = False) -> None: ...
    def set_value(self: mitsuba.Texture1f64, value: mitsuba.ArrayXf64, migrate: bool = False) -> None: ...
    def tensor(self: mitsuba.Texture1f64): ...
    def use_accel(self: mitsuba.Texture1f64) -> bool: ...
    def value(self: mitsuba.Texture1f64) -> mitsuba.ArrayXf64: ...
    def wrap_mode(self: mitsuba.Texture1f64) -> drjit.WrapMode: ...
    ...

class Texture1f:
    @overload
    def __init__(self: mitsuba.Texture1f, shape: List[int[1]], channels: int, use_accel: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    @overload
    def __init__(self: mitsuba.Texture1f, tensor, use_accel: bool = True, migrate: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    shape = ...

    def eval(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True) -> List[float]: ...
    def eval_cubic(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True, force_drjit: bool = False) -> List[float]: ...
    def eval_cubic_grad(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True) -> Tuple[List[float], List[mitsuba.Array1f]]: ...
    def eval_cubic_hessian(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True): ...
    def eval_cuda(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True) -> List[float]: ...
    def eval_fetch(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True) -> List[List[float][2]]: ...
    def eval_fetch_cuda(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True) -> List[List[float][2]]: ...
    def eval_fetch_drjit(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True) -> List[List[float][2]]: ...
    def eval_nonaccel(self: mitsuba.Texture1f, pos: mitsuba.Array1f, active: bool = True) -> List[float]: ...
    def filter_mode(self: mitsuba.Texture1f) -> drjit.FilterMode: ...
    def migrated(self: mitsuba.Texture1f) -> bool: ...
    def set_tensor(self: mitsuba.Texture1f, tensor, migrate: bool = False) -> None: ...
    def set_value(self: mitsuba.Texture1f, value: mitsuba.ArrayXf, migrate: bool = False) -> None: ...
    def tensor(self: mitsuba.Texture1f): ...
    def use_accel(self: mitsuba.Texture1f) -> bool: ...
    def value(self: mitsuba.Texture1f) -> mitsuba.ArrayXf: ...
    def wrap_mode(self: mitsuba.Texture1f) -> drjit.WrapMode: ...
    ...

class Texture2f64:
    @overload
    def __init__(self: mitsuba.Texture2f64, shape: List[int[2]], channels: int, use_accel: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    @overload
    def __init__(self: mitsuba.Texture2f64, tensor, use_accel: bool = True, migrate: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    shape = ...

    def eval(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True) -> List[float]: ...
    def eval_cubic(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True, force_drjit: bool = False) -> List[float]: ...
    def eval_cubic_grad(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True) -> Tuple[List[float], List[mitsuba.Array2f64]]: ...
    def eval_cubic_hessian(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True) -> Tuple[List[float], List[mitsuba.Array2f64], List[mitsuba.Matrix2f64]]: ...
    def eval_cuda(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True) -> List[float]: ...
    def eval_fetch(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True) -> List[List[float][4]]: ...
    def eval_fetch_cuda(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True) -> List[List[float][4]]: ...
    def eval_fetch_drjit(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True) -> List[List[float][4]]: ...
    def eval_nonaccel(self: mitsuba.Texture2f64, pos: mitsuba.Array2f64, active: bool = True) -> List[float]: ...
    def filter_mode(self: mitsuba.Texture2f64) -> drjit.FilterMode: ...
    def migrated(self: mitsuba.Texture2f64) -> bool: ...
    def set_tensor(self: mitsuba.Texture2f64, tensor, migrate: bool = False) -> None: ...
    def set_value(self: mitsuba.Texture2f64, value: mitsuba.ArrayXf64, migrate: bool = False) -> None: ...
    def tensor(self: mitsuba.Texture2f64): ...
    def use_accel(self: mitsuba.Texture2f64) -> bool: ...
    def value(self: mitsuba.Texture2f64) -> mitsuba.ArrayXf64: ...
    def wrap_mode(self: mitsuba.Texture2f64) -> drjit.WrapMode: ...
    ...

class Texture2f:
    @overload
    def __init__(self: mitsuba.Texture2f, shape: List[int[2]], channels: int, use_accel: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    @overload
    def __init__(self: mitsuba.Texture2f, tensor, use_accel: bool = True, migrate: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    shape = ...

    def eval(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True) -> List[float]: ...
    def eval_cubic(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True, force_drjit: bool = False) -> List[float]: ...
    def eval_cubic_grad(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True) -> Tuple[List[float], List[mitsuba.Array2f]]: ...
    def eval_cubic_hessian(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True) -> Tuple[List[float], List[mitsuba.Array2f], List[mitsuba.Matrix2f]]: ...
    def eval_cuda(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True) -> List[float]: ...
    def eval_fetch(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True) -> List[List[float][4]]: ...
    def eval_fetch_cuda(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True) -> List[List[float][4]]: ...
    def eval_fetch_drjit(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True) -> List[List[float][4]]: ...
    def eval_nonaccel(self: mitsuba.Texture2f, pos: mitsuba.Array2f, active: bool = True) -> List[float]: ...
    def filter_mode(self: mitsuba.Texture2f) -> drjit.FilterMode: ...
    def migrated(self: mitsuba.Texture2f) -> bool: ...
    def set_tensor(self: mitsuba.Texture2f, tensor, migrate: bool = False) -> None: ...
    def set_value(self: mitsuba.Texture2f, value: mitsuba.ArrayXf, migrate: bool = False) -> None: ...
    def tensor(self: mitsuba.Texture2f): ...
    def use_accel(self: mitsuba.Texture2f) -> bool: ...
    def value(self: mitsuba.Texture2f) -> mitsuba.ArrayXf: ...
    def wrap_mode(self: mitsuba.Texture2f) -> drjit.WrapMode: ...
    ...

class Texture3f64:
    @overload
    def __init__(self: mitsuba.Texture3f64, shape: List[int[3]], channels: int, use_accel: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    @overload
    def __init__(self: mitsuba.Texture3f64, tensor, use_accel: bool = True, migrate: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    shape = ...

    def eval(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True) -> List[float]: ...
    def eval_cubic(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True, force_drjit: bool = False) -> List[float]: ...
    def eval_cubic_grad(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True) -> Tuple[List[float], List[mitsuba.Array3f64]]: ...
    def eval_cubic_hessian(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True) -> Tuple[List[float], List[mitsuba.Array3f64], List[mitsuba.Matrix3f64]]: ...
    def eval_cuda(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True) -> List[float]: ...
    def eval_fetch(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True) -> List[List[float][8]]: ...
    def eval_fetch_cuda(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True) -> List[List[float][8]]: ...
    def eval_fetch_drjit(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True) -> List[List[float][8]]: ...
    def eval_nonaccel(self: mitsuba.Texture3f64, pos: mitsuba.Array3f64, active: bool = True) -> List[float]: ...
    def filter_mode(self: mitsuba.Texture3f64) -> drjit.FilterMode: ...
    def migrated(self: mitsuba.Texture3f64) -> bool: ...
    def set_tensor(self: mitsuba.Texture3f64, tensor, migrate: bool = False) -> None: ...
    def set_value(self: mitsuba.Texture3f64, value: mitsuba.ArrayXf64, migrate: bool = False) -> None: ...
    def tensor(self: mitsuba.Texture3f64): ...
    def use_accel(self: mitsuba.Texture3f64) -> bool: ...
    def value(self: mitsuba.Texture3f64) -> mitsuba.ArrayXf64: ...
    def wrap_mode(self: mitsuba.Texture3f64) -> drjit.WrapMode: ...
    ...

class Texture3f:
    @overload
    def __init__(self: mitsuba.Texture3f, shape: List[int[3]], channels: int, use_accel: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    @overload
    def __init__(self: mitsuba.Texture3f, tensor, use_accel: bool = True, migrate: bool = True, filter_mode: drjit.FilterMode = FilterMode.Linear, wrap_mode: drjit.WrapMode = WrapMode.Clamp) -> None: ...
    shape = ...

    def eval(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True) -> List[float]: ...
    def eval_cubic(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True, force_drjit: bool = False) -> List[float]: ...
    def eval_cubic_grad(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True) -> Tuple[List[float], List[mitsuba.Array3f]]: ...
    def eval_cubic_hessian(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True) -> Tuple[List[float], List[mitsuba.Array3f], List[mitsuba.Matrix3f]]: ...
    def eval_cuda(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True) -> List[float]: ...
    def eval_fetch(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True) -> List[List[float][8]]: ...
    def eval_fetch_cuda(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True) -> List[List[float][8]]: ...
    def eval_fetch_drjit(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True) -> List[List[float][8]]: ...
    def eval_nonaccel(self: mitsuba.Texture3f, pos: mitsuba.Array3f, active: bool = True) -> List[float]: ...
    def filter_mode(self: mitsuba.Texture3f) -> drjit.FilterMode: ...
    def migrated(self: mitsuba.Texture3f) -> bool: ...
    def set_tensor(self: mitsuba.Texture3f, tensor, migrate: bool = False) -> None: ...
    def set_value(self: mitsuba.Texture3f, value: mitsuba.ArrayXf, migrate: bool = False) -> None: ...
    def tensor(self: mitsuba.Texture3f): ...
    def use_accel(self: mitsuba.Texture3f) -> bool: ...
    def value(self: mitsuba.Texture3f) -> mitsuba.ArrayXf: ...
    def wrap_mode(self: mitsuba.Texture3f) -> drjit.WrapMode: ...
    ...

class Thread(Object):
    """
    Cross-platform thread implementation
    
    Mitsuba threads are internally implemented via the ``std::thread``
    class defined in C++11. This wrapper class is needed to attach
    additional state (Loggers, Path resolvers, etc.) that is inherited
    when a thread launches another thread.
    """

    def __init__(self: mitsuba.Thread, name: str) -> None: ...
    class EPriority:
        """
        Possible priority values for Thread::set_priority()
        
        Members:
        
          EIdlePriority : 
        
          ELowestPriority : 
        
          ELowPriority : 
        
          ENormalPriority : 
        
          EHighPriority : 
        
          EHighestPriority : 
        
          ERealtimePriority : 
        """

        def __init__(self: mitsuba.Thread.EPriority, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        EHighPriority = 4
        """
          EHighPriority : 
        """
        EHighestPriority = 5
        """
          EHighestPriority : 
        """
        EIdlePriority = 0
        """
          EIdlePriority : 
        """
        ELowPriority = 2
        """
          ELowPriority : 
        """
        ELowestPriority = 1
        """
          ELowestPriority : 
        """
        ENormalPriority = 3
        """
          ENormalPriority : 
        """
        ERealtimePriority = 6
        """
          ERealtimePriority : 
        """

        ...

    ptr = ...

    EHighPriority = 4
    """
      EHighPriority : 
    """
    EHighestPriority = 5
    """
      EHighestPriority : 
    """
    EIdlePriority = 0
    """
      EIdlePriority : 
    """
    ELowPriority = 2
    """
      ELowPriority : 
    """
    ELowestPriority = 1
    """
      ELowestPriority : 
    """
    ENormalPriority = 3
    """
      ENormalPriority : 
    """
    ERealtimePriority = 6
    """
      ERealtimePriority : 
    """

    def core_affinity(self: mitsuba.Thread) -> int:
        """
        Return the core affinity
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def detach(self: mitsuba.Thread) -> None:
        """
        Detach the thread and release resources
        
        After a call to this function, join() cannot be used anymore. This
        releases resources, which would otherwise be held until a call to
        join().
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def file_resolver(self: mitsuba.Thread) -> mitsuba.FileResolver:
        """
        Return the file resolver associated with the current thread
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def is_critical(self: mitsuba.Thread) -> bool:
        """
        Return the value of the critical flag
        """
        ...

    def is_running(self: mitsuba.Thread) -> bool:
        """
        Is this thread still running?
        """
        ...

    def join(self: mitsuba.Thread) -> None:
        """
        Wait until the thread finishes
        """
        ...

    def logger(self: mitsuba.Thread) -> mitsuba.Logger:
        """
        Return the thread's logger instance
        """
        ...

    def name(self: mitsuba.Thread) -> str:
        """
        Return the name of this thread
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def parent(self: mitsuba.Thread) -> mitsuba.Thread:
        """
        Return the parent thread
        """
        ...

    def priority(self: mitsuba.Thread) -> mitsuba.Thread.EPriority:
        """
        Return the thread priority
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_core_affinity(self: mitsuba.Thread, arg0: int) -> None:
        """
        Set the core affinity
        
        This function provides a hint to the operating system scheduler that
        the thread should preferably run on the specified processor core. By
        default, the parameter is set to -1, which means that there is no
        affinity.
        """
        ...

    def set_critical(self: mitsuba.Thread, arg0: bool) -> None:
        """
        Specify whether or not this thread is critical
        
        When an thread marked critical crashes from an uncaught exception, the
        whole process is brought down. The default is ``False``.
        """
        ...

    def set_file_resolver(self: mitsuba.Thread, arg0: mitsuba.FileResolver) -> None:
        """
        Set the file resolver associated with the current thread
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_logger(self: mitsuba.Thread, arg0: mitsuba.Logger) -> None:
        """
        Set the logger instance used to process log messages from this thread
        """
        ...

    def set_name(self: mitsuba.Thread, arg0: str) -> None:
        """
        Set the name of this thread
        """
        ...

    def set_priority(self: mitsuba.Thread, arg0: mitsuba.Thread.EPriority) -> bool:
        """
        Set the thread priority
        
        This does not always work -- for instance, Linux requires root
        privileges for this operation.
        
        Returns:
            ``True`` upon success.
        """
        ...

    def start(self: mitsuba.Thread) -> None:
        """
        Start the thread
        """
        ...

    def thread_id() -> int:
        """
        Return a unique ID that is associated with this thread
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class ThreadEnvironment:
    """
    Captures a thread environment (logger and file resolver). Used with
    ScopedSetThreadEnvironment
    """

    def __init__(self: mitsuba.ThreadEnvironment) -> None: ...
    ...

class Timer:
    def __init__(self: mitsuba.Timer) -> None: ...
    def begin_stage(self: mitsuba.Timer, arg0: str) -> None: ...
    def end_stage(self: mitsuba.Timer, arg0: str) -> None: ...
    def reset(self: mitsuba.Timer) -> int: ...
    def value(self: mitsuba.Timer) -> int: ...
    ...

class TransportMode:
    """
    Specifies the transport mode when sampling or evaluating a scattering
    function
    
    Members:
    
      Radiance : Radiance transport
    
      Importance : Importance transport
    """

    def __init__(self: mitsuba.TransportMode, value: int) -> None: ...
    name = ...
    "name(self: handle) -> str"
    value = ...

    Importance = 1
    """
      Importance : Importance transport
    """
    Radiance = 0
    """
      Radiance : Radiance transport
    """

    ...

class TraversalCallback:
    """
    Abstract class providing an interface for traversing scene graphs
    
    This interface can be implemented either in C++ or in Python, to be
    used in conjunction with Object::traverse() to traverse a scene graph.
    Mitsuba currently uses this mechanism to determine a scene's
    differentiable parameters.
    """

    def __init__(self: mitsuba.TraversalCallback) -> None: ...
    def put_object(self: mitsuba.TraversalCallback, name: str, obj: mitsuba.Object, flags: int) -> None:
        """
        Inform the traversal callback that the instance references another
        Mitsuba object
        """
        ...

    def put_parameter(self: mitsuba.TraversalCallback, name: str, value: object, flags: int) -> None:
        """
        Inform the traversal callback about an attribute of an instance
        """
        ...

    ...

class UInt: ...

class UInt32: ...

class UInt64: ...

class Volume(Object):
    """
    Abstract base class for 3D volumes.
    """

    def __init__(self: mitsuba.Volume, props: mitsuba.Properties) -> None: ...
    ptr = ...

    def bbox(self: mitsuba.Volume) -> mitsuba.BoundingBox3f:
        """
        Returns the bounding box of the volume
        """
        ...

    def channel_count(self: mitsuba.Volume) -> int:
        """
        Returns the number of channels stored in the volume
        
        When the channel count is zero, it indicates that the volume does not
        support per-channel queries.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def eval(self: mitsuba.Volume, it: mitsuba.Interaction3f, active: bool = True) -> mitsuba.Color3f:
        """
        Evaluate the volume at the given surface interaction, with color
        processing.
        """
        ...

    def eval_1(self: mitsuba.Volume, it: mitsuba.Interaction3f, active: bool = True) -> float:
        """
        Evaluate this volume as a single-channel quantity.
        """
        ...

    def eval_3(self: mitsuba.Volume, it: mitsuba.Interaction3f, active: bool = True) -> mitsuba.Vector3f:
        """
        Evaluate this volume as a three-channel quantity with no color
        processing (e.g. velocity field).
        """
        ...

    def eval_6(self: mitsuba.Volume, it: mitsuba.Interaction3f, active: bool = True) -> List[float[6]]:
        """
        Evaluate this volume as a six-channel quantity with no color
        processing This interface is specifically intended to encode the
        parameters of an SGGX phase function.
        """
        ...

    def eval_gradient(self: mitsuba.Volume, it: mitsuba.Interaction3f, active: bool = True) -> Tuple[mitsuba.Color3f, mitsuba.Vector3f]:
        """
        Evaluate the volume at the given surface interaction, and compute the
        gradients of the linear interpolant as well.
        """
        ...

    def eval_n(self: mitsuba.Volume, it: mitsuba.Interaction3f, active: bool = True) -> List[float]:
        """
        Evaluate this volume as a n-channel float quantity
        
        This interface is specifically intended to encode a variable number of
        parameters. Pointer allocation/deallocation must be performed by the
        caller.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def max(self: mitsuba.Volume) -> float:
        """
        Returns the maximum value of the volume over all dimensions.
        """
        ...

    def max_per_channel(self: mitsuba.Volume) -> List[float]:
        """
        In the case of a multi-channel volume, this function returns the
        maximum value for each channel.
        
        Pointer allocation/deallocation must be performed by the caller.
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def resolution(self: mitsuba.Volume) -> mitsuba.Vector3i:
        """
        Returns the resolution of the volume, assuming that it is based on a
        discrete representation.
        
        The default implementation returns ``(1, 1, 1)``
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    ...

class VolumeGrid(Object):
    @overload
    def __init__(self: mitsuba.VolumeGrid, array: numpy.ndarray[numpy.float32], compute_max: bool = True) -> None:
        """
        Initialize a VolumeGrid from a NumPy array
        
        """
        ...

    @overload
    def __init__(self: mitsuba.VolumeGrid, path: mitsuba.filesystem.path) -> None: ...
    @overload
    def __init__(self: mitsuba.VolumeGrid, stream: mitsuba.Stream) -> None: ...
    ptr = ...

    def buffer_size(self: mitsuba.VolumeGrid) -> int:
        """
        Return the volume grid size in bytes (excluding metadata)
        """
        ...

    def bytes_per_voxel(self: mitsuba.VolumeGrid) -> int:
        """
        Return the number bytes of storage used per voxel
        """
        ...

    def channel_count(self: mitsuba.VolumeGrid) -> int:
        """
        Return the number of channels
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def max(self: mitsuba.VolumeGrid) -> float:
        """
        Return the precomputed maximum over the volume grid
        """
        ...

    def max_per_channel(self: mitsuba.VolumeGrid) -> List[float]:
        """
        Return the precomputed maximum over the volume grid per channel
        
        Pointer allocation/deallocation must be performed by the caller.
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def set_max(self: mitsuba.VolumeGrid, arg0: float) -> None:
        """
        Set the precomputed maximum over the volume grid
        """
        ...

    def set_max_per_channel(self: mitsuba.VolumeGrid, arg0: List[float]) -> None:
        """
        Set the precomputed maximum over the volume grid per channel
        
        Pointer allocation/deallocation must be performed by the caller.
        """
        ...

    def size(self: mitsuba.VolumeGrid) -> mitsuba.Vector3u:
        """
        Return the resolution of the voxel grid
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    @overload
    def write(self: mitsuba.VolumeGrid, stream: mitsuba.Stream) -> None:
        """
        Write an encoded form of the bitmap to a binary volume file
        
        Parameter ``path``:
            Target file name (expected to end in ".vol")
        
        """
        ...

    @overload
    def write(self: mitsuba.VolumeGrid, path: mitsuba.filesystem.path) -> None:
        """
        Write an encoded form of the volume grid to a stream
        
        Parameter ``stream``:
            Target stream that will receive the encoded output
        """
        ...

    ...

class ZStream(Stream):
    """
    Transparent compression/decompression stream based on ``zlib``.
    
    This class transparently decompresses and compresses reads and writes
    to a nested stream, respectively.
    """

    def __init__(self: mitsuba.ZStream, child_stream: mitsuba.Stream, stream_type: mitsuba.ZStream.EStreamType = EStreamType.EDeflateStream, level: int = -1) -> None:
        """
        Creates a new compression stream with the given underlying stream.
        This new instance takes ownership of the child stream. The child
        stream must outlive the ZStream.
        """
        ...

    class EByteOrder:
        """
        Defines the byte order (endianness) to use in this Stream
        
        Members:
        
          EBigEndian : 
        
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        
          ENetworkByteOrder : x86, x86_64
        """

        def __init__(self: mitsuba.Stream.EByteOrder, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        EBigEndian = 0
        """
          EBigEndian : 
        """
        ELittleEndian = 1
        """
          ELittleEndian : PowerPC, SPARC, Motorola 68K
        """

        ...

    class EStreamType:
        """
        
        Members:
        
          EDeflateStream : 
        
          EGZipStream : A raw deflate stream
        """

        def __init__(self: mitsuba.ZStream.EStreamType, value: int) -> None: ...
        name = ...
        "name(self: handle) -> str"
        value = ...

        EDeflateStream = 0
        """
          EDeflateStream : 
        """
        EGZipStream = 1
        """
          EGZipStream : A raw deflate stream
        """

        ...

    ptr = ...

    EBigEndian = 0
    """
      EBigEndian : 
    """
    EDeflateStream = 0
    """
      EDeflateStream : 
    """
    EGZipStream = 1
    """
      EGZipStream : A raw deflate stream
    """
    ELittleEndian = 1
    """
      ELittleEndian : PowerPC, SPARC, Motorola 68K
    """

    def byte_order(self: mitsuba.Stream) -> mitsuba.Stream.EByteOrder:
        """
        Returns the byte order of this stream.
        """
        ...

    def can_read(self: mitsuba.Stream) -> bool:
        """
        Can we read from the stream?
        """
        ...

    def can_write(self: mitsuba.Stream) -> bool:
        """
        Can we write to the stream?
        """
        ...

    def child_stream(self: mitsuba.ZStream) -> object:
        """
        Returns the child stream of this compression stream
        """
        ...

    def close(self: mitsuba.Stream) -> None:
        """
        Closes the stream.
        
        No further read or write operations are permitted.
        
        This function is idempotent. It may be called automatically by the
        destructor.
        """
        ...

    def dec_ref(self: mitsuba.Object, dealloc: bool = True) -> None:
        """
        Decrease the reference count of the object and possibly deallocate it.
        
        The object will automatically be deallocated once the reference count
        reaches zero.
        """
        ...

    def expand(self: mitsuba.Object) -> list:
        """
        Expand the object into a list of sub-objects and return them
        
        In some cases, an Object instance is merely a container for a number
        of sub-objects. In the context of Mitsuba, an example would be a
        combined sun & sky emitter instantiated via XML, which recursively
        expands into a separate sun & sky instance. This functionality is
        supported by any Mitsuba object, hence it is located this level.
        """
        ...

    def flush(self: mitsuba.Stream) -> None:
        """
        Flushes the stream's buffers, if any
        """
        ...

    def id(self: mitsuba.Object) -> str:
        """
        Return an identifier of the current instance (if available)
        """
        ...

    def inc_ref(self: mitsuba.Object) -> None:
        """
        Increase the object's reference count by one
        """
        ...

    def parameters_changed(self: mitsuba.Object, keys: List[str] = []) -> None:
        """
        Update internal state after applying changes to parameters
        
        This function should be invoked when attributes (obtained via
        traverse) are modified in some way. The object can then update its
        internal state so that derived quantities are consistent with the
        change.
        
        Parameter ``keys``:
            Optional list of names (obtained via traverse) corresponding to
            the attributes that have been modified. Can also be used to notify
            when this function is called from a parent object by adding a
            "parent" key to the list. When empty, the object should assume
            that any attribute might have changed.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def read(self: mitsuba.Stream, arg0: int) -> bytes:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def read_bool(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_double(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_float(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_int8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_line(self: mitsuba.Stream) -> str:
        """
        Convenience function for reading a line of text from an ASCII file
        """
        ...

    def read_single(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_string(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint16(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint32(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint64(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def read_uint8(self: mitsuba.Stream) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def ref_count(self: mitsuba.Object) -> int:
        """
        Return the current reference count
        """
        ...

    def seek(self: mitsuba.Stream, arg0: int) -> None:
        """
        Seeks to a position inside the stream.
        
        Seeking beyond the size of the buffer will not modify the length of
        its contents. However, a subsequent write should start at the sought
        position and update the size appropriately.
        """
        ...

    def set_byte_order(self: mitsuba.Stream, arg0: mitsuba.Stream.EByteOrder) -> None:
        """
        Sets the byte order to use in this stream.
        
        Automatic conversion will be performed on read and write operations to
        match the system's native endianness.
        
        No consistency is guaranteed if this method is called after performing
        some read and write operations on the system using a different
        endianness.
        """
        ...

    def set_id(self: mitsuba.Object, id: str) -> None:
        """
        Set an identifier to the current instance (if applicable)
        """
        ...

    def size(self: mitsuba.Stream) -> int:
        """
        Returns the size of the stream
        """
        ...

    def skip(self: mitsuba.Stream, arg0: int) -> None:
        """
        Skip ahead by a given number of bytes
        """
        ...

    def tell(self: mitsuba.Stream) -> int:
        """
        Gets the current position inside the stream
        """
        ...

    def traverse(self: mitsuba.Object, cb) -> None:
        """
        Traverse the attributes and object graph of this instance
        
        Implementing this function enables recursive traversal of C++ scene
        graphs. It is e.g. used to determine the set of differentiable
        parameters when using Mitsuba for optimization.
        
        Remark:
            The default implementation does nothing.
        
        See also:
            TraversalCallback
        """
        ...

    def truncate(self: mitsuba.Stream, arg0: int) -> None:
        """
        Truncates the stream to a given size.
        
        The position is updated to ``min(old_position, size)``. Throws an
        exception if in read-only mode.
        """
        ...

    def write(self: mitsuba.Stream, arg0: bytes) -> None:
        """
        Writes a specified amount of data into the stream. \note This does
        **not** handle endianness swapping.
        
        Throws an exception when not all data could be written.
        Implementations need to handle endianness swap when appropriate.
        """
        ...

    def write_bool(self: mitsuba.Stream, arg0: bool) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_double(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_float(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_int8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_line(self: mitsuba.Stream, arg0: str) -> None:
        """
        Convenience function for writing a line of text to an ASCII file
        """
        ...

    def write_single(self: mitsuba.Stream, arg0: float) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_string(self: mitsuba.Stream, arg0: str) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint16(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint32(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint64(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    def write_uint8(self: mitsuba.Stream, arg0: int) -> object:
        """
        Reads one object of type T from the stream at the current position by
        delegating to the appropriate ``serialization_helper``.
        
        Endianness swapping is handled automatically if needed.
        """
        ...

    ...


from .stubs import python_ad as ad


from .stubs import python_chi2 as chi2

def cie1931_xyz(wavelength: float) -> mitsuba.Color3f:
    """
    Evaluate the CIE 1931 XYZ color matching functions given a wavelength
    in nanometers
    """
    ...

def cie1931_y(wavelength: float) -> float:
    """
    Evaluate the CIE 1931 Y color matching function given a wavelength in
    nanometers
    """
    ...

def cie_d65(wavelength: float) -> float:
    """
    Evaluate the CIE D65 illuminant spectrum given a wavelength in
    nanometers, normalized to ensures that it integrates to a luminance of
    1.0.
    """
    ...

def coordinate_system(n: mitsuba.Vector3f) -> Tuple[mitsuba.Vector3f, mitsuba.Vector3f]:
    """
    Complete the set {a} to an orthonormal basis {a, b, c}
    """
    ...

def cornell_box():
    """
    
    Returns a dictionary containing a description of the Cornell Box scene.
    
    """
    ...


from .stubs import cuda_ad_spectral as cuda_ad_spectral


from .stubs import cuda_spectral as cuda_spectral

def depolarizer(arg0: mitsuba.Color3f) -> mitsuba.Color3f: ...
def eval_reflectance(type: mitsuba.MicrofacetType, alpha_u: float, alpha_v: float, wi, eta: float) -> mitsuba.ArrayXf: ...

from .stubs import scalar_rgb_filesystem as filesystem

float_dtype = ...
"""
str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.
"""
def fresnel(cos_theta_i: float, eta: float) -> Tuple[float, float, float, float]:
    """
    Calculates the unpolarized Fresnel reflection coefficient at a planar
    interface between two dielectrics
    
    Parameter ``cos_theta_i``:
        Cosine of the angle between the surface normal and the incident
        ray
    
    Parameter ``eta``:
        Relative refractive index of the interface. A value greater than
        1.0 means that the surface normal is pointing into the region of
        lower density.
    
    Returns:
        A tuple (F, cos_theta_t, eta_it, eta_ti) consisting of
    
    F Fresnel reflection coefficient.
    
    cos_theta_t Cosine of the angle between the surface normal and the
    transmitted ray
    
    eta_it Relative index of refraction in the direction of travel.
    
    eta_ti Reciprocal of the relative index of refraction in the direction
    of travel. This also happens to be equal to the scale factor that must
    be applied to the X and Y component of the refracted direction.
    """
    ...

def fresnel_conductor(cos_theta_i: float, eta: mitsuba.Complex2f) -> float:
    """
    Calculates the unpolarized Fresnel reflection coefficient at a planar
    interface of a conductor, i.e. a surface with a complex-valued
    relative index of refraction
    
    Remark:
        The implementation assumes that cos_theta_i > 0, i.e. light enters
        from *outside* of the conducting layer (generally a reasonable
        assumption unless very thin layers are being simulated)
    
    Parameter ``cos_theta_i``:
        Cosine of the angle between the surface normal and the incident
        ray
    
    Parameter ``eta``:
        Relative refractive index (complex-valued)
    
    Returns:
        The unpolarized Fresnel reflection coefficient.
    """
    ...

def fresnel_diffuse_reflectance(eta: float) -> float:
    """
    Computes the diffuse unpolarized Fresnel reflectance of a dielectric
    material (sometimes referred to as "Fdr").
    
    This value quantifies what fraction of diffuse incident illumination
    will, on average, be reflected at a dielectric material boundary
    
    Parameter ``eta``:
        Relative refraction coefficient
    
    Returns:
        F, the unpolarized Fresnel coefficient.
    """
    ...

def fresnel_polarized(cos_theta_i: float, eta: mitsuba.Complex2f) -> Tuple[mitsuba.Complex2f, mitsuba.Complex2f, float, mitsuba.Complex2f, mitsuba.Complex2f]:
    """
    Calculates the polarized Fresnel reflection coefficient at a planar
    interface between two dielectrics or conductors. Returns complex
    values encoding the amplitude and phase shift of the s- and
    p-polarized waves.
    
    This is the most general version, which subsumes all others (at the
    cost of transcendental function evaluations in the complex-valued
    arithmetic)
    
    Parameter ``cos_theta_i``:
        Cosine of the angle between the surface normal and the incident
        ray
    
    Parameter ``eta``:
        Complex-valued relative refractive index of the interface. In the
        real case, a value greater than 1.0 case means that the surface
        normal points into the region of lower density.
    
    Returns:
        A tuple (a_s, a_p, cos_theta_t, eta_it, eta_ti) consisting of
    
    a_s Perpendicularly polarized wave amplitude and phase shift.
    
    a_p Parallel polarized wave amplitude and phase shift.
    
    cos_theta_t Cosine of the angle between the surface normal and the
    transmitted ray. Zero in the case of total internal reflection.
    
    eta_it Relative index of refraction in the direction of travel
    
    eta_ti Reciprocal of the relative index of refraction in the direction
    of travel. In the real-valued case, this also happens to be equal to
    the scale factor that must be applied to the X and Y component of the
    refracted direction.
    """
    ...

def get_property(ptr: capsule, type: capsule, parent: handle) -> object: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.EmitterFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.EmitterFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.RayFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.RayFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.DiscontinuityFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.DiscontinuityFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.BSDFFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.BSDFFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.FilmFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.FilmFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.PhaseFunctionFlags) -> bool: ...
@overload
def has_flag(arg0: int, arg1: mitsuba.PhaseFunctionFlags) -> bool: ...
def linear_rgb_rec(wavelength: float) -> mitsuba.Color3f:
    """
    Evaluate the ITU-R Rec. BT.709 linear RGB color matching functions
    given a wavelength in nanometers
    """
    ...

def load_dict(dict: dict, parallel: bool = True) -> object:
    """
    Load a Mitsuba scene or object from an Python dictionary
    
    Parameter ``dict``:
        Python dictionary containing the object description
    
    Parameter ``parallel``:
        Whether the loading should be executed on multiple threads in parallel
    
    
    """
    ...

def load_file(path: str, update_scene: bool = False, parallel: bool = True, **kwargs) -> object:
    """
    Load a Mitsuba scene from an XML file
    
    Parameter ``path``:
        Filename of the scene XML file
    
    Parameter ``parameters``:
        Optional list of parameters that can be referenced as ``$varname``
        in the scene.
    
    Parameter ``variant``:
        Specifies the variant of plugins to instantiate (e.g.
        "scalar_rgb")
    
    Parameter ``update_scene``:
        When Mitsuba updates scene to a newer version, should the updated
        XML file be written back to disk?
    
    Parameter ``parallel``:
        Whether the loading should be executed on multiple threads in
        parallel
    """
    ...

def load_string(string: str, parallel: bool = True, **kwargs) -> object:
    """
    Load a Mitsuba scene from an XML string
    """
    ...

def log_level():
    """
    Returns the current log level.
    """
    ...

def lookup_ior(properties: mitsuba.Properties, name: str, default: object) -> float:
    """
    Lookup IOR value in table.
    """
    ...

@overload
def luminance(value: mitsuba.Color3f, wavelengths: mitsuba.Color0f, active: bool = True) -> float: ...
@overload
def luminance(c: mitsuba.Color3f) -> float: ...

from .stubs import scalar_rgb_math as math


from .stubs import scalar_rgb_mueller as mueller

def parse_fov(props, aspect: float) -> float:
    """
    Helper function to parse the field of view field of a camera
    """
    ...

@overload
def pdf_rgb_spectrum(wavelengths: float) -> float:
    """
    PDF for the sample_rgb_spectrum strategy. It is valid to call this
    function for a single wavelength (Float), a set of wavelengths
    (Spectrumf), a packet of wavelengths (SpectrumfP), etc. In all cases,
    the PDF is returned per wavelength.
    
    """
    ...

@overload
def pdf_rgb_spectrum(wavelengths: mitsuba.Color3f) -> mitsuba.Color3f:
    """
    PDF for the sample_rgb_spectrum strategy. It is valid to call this
    function for a single wavelength (Float), a set of wavelengths
    (Spectrumf), a packet of wavelengths (SpectrumfP), etc. In all cases,
    the PDF is returned per wavelength.
    """
    ...

def permute(value: int, size: int, seed: int, rounds: int = 4) -> int:
    """
    Generate pseudorandom permutation vector using a shuffling network
    
    This algorithm repeatedly invokes sample_tea_32() internally and has
    O(log2(sample_count)) complexity. It only supports permutation
    vectors, whose lengths are a power of 2.
    
    Parameter ``index``:
        Input index to be permuted
    
    Parameter ``size``:
        Length of the permutation vector
    
    Parameter ``seed``:
        Seed value used as second input to the Tiny Encryption Algorithm.
        Can be used to generate different permutation vectors.
    
    Parameter ``rounds``:
        How many rounds should be executed by the Tiny Encryption
        Algorithm? The default is 2.
    
    Returns:
        The index corresponding to the input index in the pseudorandom
        permutation vector.
    """
    ...

def permute_kensler(i: int, l: int, p: int, active: bool = True) -> int:
    """
    Generate pseudorandom permutation vector using the algorithm described
    in Pixar's technical memo "Correlated Multi-Jittered Sampling":
    
    https://graphics.pixar.com/library/MultiJitteredSampling/
    
    Unlike permute, this function supports permutation vectors of any
    length.
    
    Parameter ``index``:
        Input index to be mapped
    
    Parameter ``sample_count``:
        Length of the permutation vector
    
    Parameter ``seed``:
        Seed value used as second input to the Tiny Encryption Algorithm.
        Can be used to generate different permutation vectors.
    
    Returns:
        The index corresponding to the input index in the pseudorandom
        permutation vector.
    """
    ...

def perspective_projection(film_size: mitsuba.Vector2i, crop_size: mitsuba.Vector2i, crop_offset: mitsuba.Vector2i, fov_x: float, near_clip: float, far_clip: float) -> mitsuba.Transform4f:
    """
    Helper function to create a perspective projection transformation
    matrix
    """
    ...


from .stubs import scalar_rgb_quad as quad

def radical_inverse_2(index: int, scramble: int) -> float:
    """
    Van der Corput radical inverse in base 2
    """
    ...

@overload
def reflect(wi: mitsuba.Vector3f) -> mitsuba.Vector3f:
    """
    Reflection in local coordinates
    
    """
    ...

@overload
def reflect(wi: mitsuba.Vector3f, m: mitsuba.Normal3f) -> mitsuba.Vector3f:
    """
    Reflect ``wi`` with respect to a given surface normal
    """
    ...

@overload
def refract(wi: mitsuba.Vector3f, cos_theta_t: float, eta_ti: float) -> mitsuba.Vector3f:
    """
    Refraction in local coordinates
    
    The 'cos_theta_t' and 'eta_ti' parameters are given by the last two
    tuple entries returned by the fresnel and fresnel_polarized functions.
    
    """
    ...

@overload
def refract(wi: mitsuba.Vector3f, m: mitsuba.Normal3f, cos_theta_t: float, eta_ti: float) -> mitsuba.Vector3f:
    """
    Refract ``wi`` with respect to a given surface normal
    
    Parameter ``wi``:
        Direction to refract
    
    Parameter ``m``:
        Surface normal
    
    Parameter ``cos_theta_t``:
        Cosine of the angle between the normal the transmitted ray, as
        computed e.g. by fresnel.
    
    Parameter ``eta_ti``:
        Relative index of refraction (transmitted / incident)
    """
    ...

def register_bsdf(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_emitter(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_film(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_integrator(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_medium(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_mesh(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_phasefunction(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_sampler(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_sensor(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_texture(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def register_volume(arg0: str, arg1: Callable[[mitsuba.Properties], object]) -> None: ...
def render(scene: 'mitsuba.Scene', params: 'Any' = None, sensor: 'Union[int, mitsuba.Sensor]' = 0, integrator: 'mitsuba.Integrator' = None, seed: 'int' = 0, seed_grad: 'int' = 0, spp: 'int' = 0, spp_grad: 'int' = 0) -> 'mitsuba.TensorXf':
    """
    
    This function provides a convenient high-level interface to differentiable
    rendering algorithms in Mi. The function returns a rendered image that can
    be used in subsequent differentiable computation steps. At any later point,
    the entire computation graph can be differentiated end-to-end in either
    forward or reverse mode (i.e., using ``dr.forward()`` and
    ``dr.backward()``).
    
    Under the hood, the differentiation operation will be intercepted and routed
    to ``Integrator.render_forward()`` or ``Integrator.render_backward()``,
    which evaluate the derivative using either naive AD or a more specialized
    differential simulation.
    
    Note the default implementation of this functionality relies on naive
    automatic differentiation (AD), which records a computation graph of the
    primal rendering step that is subsequently traversed to propagate
    derivatives. This tends to be relatively inefficient due to the need to
    track intermediate program state. In particular, it means that
    differentiation of nontrivial scenes at high sample counts will often run
    out of memory. Integrators like ``rb`` (Radiative Backpropagation) and
    ``prb`` (Path Replay Backpropagation) that are specifically designed for
    differentiation can be significantly more efficient.
    
    Parameter ``scene`` (``mi.Scene``):
    Reference to the scene being rendered in a differentiable manner.
    
    Parameter ``params``:
    An optional container of scene parameters that should receive gradients.
    This argument isn't optional when computing forward mode derivatives. It
    should be an instance of type ``mi.SceneParameters`` obtained via
    ``mi.traverse()``. Gradient tracking must be explicitly enabled on these
    parameters using ``dr.enable_grad(params['parameter_name'])`` (i.e.
    ``render()`` will not do this for you). Furthermore, ``dr.set_grad(...)``
    must be used to associate specific gradient values with parameters if
    forward mode derivatives are desired. When the scene parameters are
    derived from other variables that have gradient tracking enabled,
    gradient values should be propagated to the scene parameters by calling
    ``dr.forward_to(params, dr.ADFlag.ClearEdges)`` before calling this
    function.
    
    Parameter ``sensor`` (``int``, ``mi.Sensor``):
    Specify a sensor or a (sensor index) to render the scene from a
    different viewpoint. By default, the first sensor within the scene
    description (index 0) will take precedence.
    
    Parameter ``integrator`` (``mi.Integrator``):
    Optional parameter to override the rendering technique to be used. By
    default, the integrator specified in the original scene description will
    be used.
    
    Parameter ``seed`` (``int``)
    This parameter controls the initialization of the random number
    generator during the primal rendering step. It is crucial that you
    specify different seeds (e.g., an increasing sequence) if subsequent
    calls should produce statistically independent images (e.g. to
    de-correlate gradient-based optimization steps).
    
    Parameter ``seed_grad`` (``int``)
    This parameter is analogous to the ``seed`` parameter but targets the
    differential simulation phase. If not specified, the implementation will
    automatically compute a suitable value from the primal ``seed``.
    
    Parameter ``spp`` (``int``):
    Optional parameter to override the number of samples per pixel for the
    primal rendering step. The value provided within the original scene
    specification takes precedence if ``spp=0``.
    
    Parameter ``spp_grad`` (``int``):
    This parameter is analogous to the ``seed`` parameter but targets the
    differential simulation phase. If not specified, the implementation will
    copy the value from ``spp``.
    
    """
    ...

@overload
def sample_rgb_spectrum(sample: float) -> Tuple[float, float]:
    """
    Importance sample a "importance spectrum" that concentrates the
    computation on wavelengths that are relevant for rendering of RGB data
    
    Based on "An Improved Technique for Full Spectral Rendering" by
    Radziszewski, Boryczko, and Alda
    
    Returns a tuple with the sampled wavelength and inverse PDF
    
    """
    ...

@overload
def sample_rgb_spectrum(sample: mitsuba.Color3f) -> Tuple[mitsuba.Color3f, mitsuba.Color3f]:
    """
    Importance sample a "importance spectrum" that concentrates the
    computation on wavelengths that are relevant for rendering of RGB data
    
    Based on "An Improved Technique for Full Spectral Rendering" by
    Radziszewski, Boryczko, and Alda
    
    Returns a tuple with the sampled wavelength and inverse PDF
    """
    ...

def sample_tea_32(v0: int, v1: int, rounds: int = 4) -> Tuple[int, int]:
    """
    Generate fast and reasonably good pseudorandom numbers using the Tiny
    Encryption Algorithm (TEA) by David Wheeler and Roger Needham.
    
    For details, refer to "GPU Random Numbers via the Tiny Encryption
    Algorithm" by Fahad Zafar, Marc Olano, and Aaron Curtis.
    
    Parameter ``v0``:
        First input value to be encrypted (could be the sample index)
    
    Parameter ``v1``:
        Second input value to be encrypted (e.g. the requested random
        number dimension)
    
    Parameter ``rounds``:
        How many rounds should be executed? The default for random number
        generation is 4.
    
    Returns:
        Two uniformly distributed 32-bit integers
    """
    ...

def sample_tea_64(v0: int, v1: int, rounds: int = 4) -> int:
    """
    Generate fast and reasonably good pseudorandom numbers using the Tiny
    Encryption Algorithm (TEA) by David Wheeler and Roger Needham.
    
    For details, refer to "GPU Random Numbers via the Tiny Encryption
    Algorithm" by Fahad Zafar, Marc Olano, and Aaron Curtis.
    
    Parameter ``v0``:
        First input value to be encrypted (could be the sample index)
    
    Parameter ``v1``:
        Second input value to be encrypted (e.g. the requested random
        number dimension)
    
    Parameter ``rounds``:
        How many rounds should be executed? The default for random number
        generation is 4.
    
    Returns:
        A uniformly distributed 64-bit integer
    """
    ...

def sample_tea_float32(v0: int, v1: int, rounds: int = 4) -> float:
    """
    Generate fast and reasonably good pseudorandom numbers using the Tiny
    Encryption Algorithm (TEA) by David Wheeler and Roger Needham.
    
    This function uses sample_tea to return single precision floating
    point numbers on the interval ``[0, 1)``
    
    Parameter ``v0``:
        First input value to be encrypted (could be the sample index)
    
    Parameter ``v1``:
        Second input value to be encrypted (e.g. the requested random
        number dimension)
    
    Parameter ``rounds``:
        How many rounds should be executed? The default for random number
        generation is 4.
    
    Returns:
        A uniformly distributed floating point number on the interval
        ``[0, 1)``
    """
    ...

def sample_tea_float64(v0: int, v1: int, rounds: int = 4) -> float:
    """
    Generate fast and reasonably good pseudorandom numbers using the Tiny
    Encryption Algorithm (TEA) by David Wheeler and Roger Needham.
    
    This function uses sample_tea to return double precision floating
    point numbers on the interval ``[0, 1)``
    
    Parameter ``v0``:
        First input value to be encrypted (could be the sample index)
    
    Parameter ``v1``:
        Second input value to be encrypted (e.g. the requested random
        number dimension)
    
    Parameter ``rounds``:
        How many rounds should be executed? The default for random number
        generation is 4.
    
    Returns:
        A uniformly distributed floating point number on the interval
        ``[0, 1)``
    """
    ...


from .stubs import scalar_rgb as scalar_rgb


from .stubs import scalar_spectral as scalar_spectral

def set_log_level(arg0) -> None:
    """
    Sets the log level.
    """
    ...

def set_property(ptr: capsule, type: capsule, value: handle) -> None: ...
def set_variant(*args) -> None:
    """
    
    Set the variant to be used by the `mitsuba` module. Multiple variant
    names can be passed to this function and the first one that is supported
    will be set as current variant.
    
    """
    ...

def sggx_pdf(wm: mitsuba.Vector3f, s) -> float:
    """
    Evaluates the probability of sampling a given normal using the SGGX
    microflake distribution
    
    Parameter ``wm``:
        The microflake normal
    
    Parameter ``s``:
        The parameters of the SGGX phase function stored as a 6D vector
        [S_xx, S_yy, S_zz, S_xy, S_xz, S_yz]. The parameters describe the
        entries of a symmetric positive definite 3x3 matrix. The user
        needs to ensure that the parameters indeed represent a positive
        definite matrix.
    
    Returns:
        The probability of sampling a certain normal
    """
    ...

def sggx_projected_area(wi: mitsuba.Vector3f, s) -> float:
    """
    Evaluates the projected area of the SGGX microflake distribution
    
    Parameter ``wi``:
        A 3D direction
    
    Parameter ``s``:
        The parameters of the SGGX phase function stored as a 6D vector
        [S_xx, S_yy, S_zz, S_xy, S_xz, S_yz]. The parameters describe the
        entries of a symmetric positive definite 3x3 matrix. The user
        needs to ensure that the parameters indeed represent a positive
        definite matrix.
    
    Returns:
        The projected area of the SGGX microflake distribution
    """
    ...

@overload
def sggx_sample(sh_frame: mitsuba.Frame3f, sample: mitsuba.Point2f, s) -> mitsuba.Normal3f:
    """
    Samples the visible normal distribution of the SGGX microflake
    distribution
    
    This function is based on the paper
    
    "The SGGX microflake distribution", Siggraph 2015 by Eric Heitz,
    Jonathan Dupuy, Cyril Crassin and Carsten Dachsbacher
    
    Parameter ``sh_frame``:
        Shading frame aligned with the incident direction, e.g.
        constructed as Frame3f(wi)
    
    Parameter ``sample``:
        A uniformly distributed 2D sample
    
    Parameter ``s``:
        The parameters of the SGGX phase function stored as a 6D vector
        [S_xx, S_yy, S_zz, S_xy, S_xz, S_yz]. The parameters describe the
        entries of a symmetric positive definite 3x3 matrix. The user
        needs to ensure that the parameters indeed represent a positive
        definite matrix.
    
    Returns:
        A normal (in world space) sampled from the distribution of visible
        normals
    
    """
    ...

@overload
def sggx_sample(sh_frame: mitsuba.Vector3f, sample: mitsuba.Point2f, s) -> mitsuba.Normal3f:
    """
    Samples the visible normal distribution of the SGGX microflake
    distribution
    
    This function is based on the paper
    
    "The SGGX microflake distribution", Siggraph 2015 by Eric Heitz,
    Jonathan Dupuy, Cyril Crassin and Carsten Dachsbacher
    
    Parameter ``sh_frame``:
        Shading frame aligned with the incident direction, e.g.
        constructed as Frame3f(wi)
    
    Parameter ``sample``:
        A uniformly distributed 2D sample
    
    Parameter ``s``:
        The parameters of the SGGX phase function stored as a 6D vector
        [S_xx, S_yy, S_zz, S_xy, S_xz, S_yz]. The parameters describe the
        entries of a symmetric positive definite 3x3 matrix. The user
        needs to ensure that the parameters indeed represent a positive
        definite matrix.
    
    Returns:
        A normal (in world space) sampled from the distribution of visible
        normals
    """
    ...

def sobol_2(index: int, scramble: int) -> float:
    """
    Sobol' radical inverse in base 2
    """
    ...

def spectrum_from_file(filename: mitsuba.filesystem.path) -> Tuple[List[float], List[float]]:
    """
    Read a spectral power distribution from an ASCII file.
    
    The data should be arranged as follows: The file should contain a
    single measurement per line, with the corresponding wavelength in
    nanometers and the measured value separated by a space. Comments are
    allowed.
    
    Parameter ``path``:
        Path of the file to be read
    
    Parameter ``wavelengths``:
        Array that will be loaded with the wavelengths stored in the file
    
    Parameter ``values``:
        Array that will be loaded with the values stored in the file
    """
    ...

def spectrum_list_to_srgb(wavelengths: List[float], values: List[float], bounded: bool = True, d65: bool = False) -> mitsuba.Color3f: ...
def spectrum_to_file(filename: mitsuba.filesystem.path, wavelengths: List[float], values: List[float]) -> None:
    """
    Write a spectral power distribution to an ASCII file.
    
    The format is identical to that parsed by spectrum_from_file().
    
    Parameter ``path``:
        Path to the file to be written to
    
    Parameter ``wavelengths``:
        Array with the wavelengths to be stored in the file
    
    Parameter ``values``:
        Array with the values to be stored in the file
    """
    ...


from .stubs import scalar_rgb_spline as spline

def srgb_model_eval(arg0: mitsuba.Array3f, arg1: mitsuba.Color0f) -> mitsuba.Color3f: ...
def srgb_model_fetch(arg0: mitsuba.Color3f) -> mitsuba.Array3f:
    """
    Look up the model coefficients for a sRGB color value
    
    Parameter ``c``:
        An sRGB color value where all components are in [0, 1].
    
    Returns:
        Coefficients for use with srgb_model_eval
    """
    ...

def srgb_model_mean(arg0: mitsuba.Array3f) -> float: ...
def srgb_to_xyz(rgb: mitsuba.Color3f, active: bool = True) -> mitsuba.Color3f:
    """
    Convert ITU-R Rec. BT.709 linear RGB to XYZ tristimulus values
    """
    ...

def traverse(node: 'mitsuba.Object') -> 'SceneParameters':
    """
    
    Traverse a node of Mitsuba's scene graph and return a dictionary-like
    object that can be used to read and write associated scene parameters.
    
    See also :py:class:`mitsuba.SceneParameters`.
    
    """
    ...

def unpolarized_spectrum(arg0: mitsuba.Color3f) -> mitsuba.Color3f: ...

from .stubs import scalar_rgb_util as util

def variant() -> str:
    """
    Return currently enabled variant
    """
    ...

def variant_context(*args) -> 'None':
    """
    
    Temporarily override the active variant. Arguments are interpreted as
    they are in :func:`mitsuba.set_variant`.
    
    """
    ...

def variants() -> List[str]:
    """
    Return a list of all variants that have been compiled
    """
    ...


from .stubs import scalar_rgb_warp as warp


from .stubs import python_xml as xml

def xml_to_props(path: str) -> List[Tuple[str, mitsuba.Properties]]:
    """
    Get the names and properties of the objects described in a Mitsuba XML file
    """
    ...

def xyz_to_srgb(rgb: mitsuba.Color3f, active: bool = True) -> mitsuba.Color3f:
    """
    Convert XYZ tristimulus values to ITU-R Rec. BT.709 linear RGB
    """
    ...

