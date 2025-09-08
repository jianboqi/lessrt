from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

class ProjectiveDetail:
    """
        Class holding implementation details of various operations needed by
        projective-sampling/path-space style integrators.
        
    """

    class ProjectOperation:
        """
                Projection operation takes a seed ray as input and outputs a
                
        ef SilhouetteSample3f object.
                
        """

        def eval(self, scene, ray_guide, si_guide, sampler, active):
            """
            
            Dispatches the seed surface interaction object to the appropriate
            shape's projection algorithm.
            
            """
            ...

        def hybrid_mesh_projection(self, scene: 'mitsuba.Scene', si: 'mitsuba.SurfaceInteraction3f', viewpoint: 'mitsuba.Point3f', state: 'mitsuba.UInt64', active: 'mitsuba.Bool', max_move: 'int'): ...
        def mesh_jump(self, scene: 'mitsuba.Scene', si_: 'mitsuba.SurfaceInteraction3f', viewpoint: 'mitsuba.Point3f', state: 'mitsuba.UInt64', active: 'mitsuba.Bool', max_jump: 'int'): ...
        def mesh_walk(self, si_: 'mitsuba.SurfaceInteraction3f', viewpoint: 'mitsuba.Point3f', state: 'mitsuba.UInt64', active: 'mitsuba.Bool', max_move: 'int'): ...
        def project_curve(self, scene, ray_guide, si, state, active): ...
        def project_cylinder(self, scene, ray_guide, si, state, active): ...
        def project_disk(self, scene, ray_guide, si, state, active): ...
        def project_mesh(self, scene, ray_guide, si_guide, state, active): ...
        def project_rectangle(self, scene, ray_guide, si, state, active): ...
        def project_sdf(self, scene, ray_guide, si_guide, state, active): ...
        def project_sphere(self, scene, ray_guide, si, state, active): ...
        ...

    def eval_indirect_integrand(self, scene: 'mitsuba.Scene', sensor: 'mitsuba.Sensor', sample: 'mitsuba.Vector3f', sampler: 'mitsuba.Sampler', preprocess: 'bool', active: 'mitsuba.Mask' = True):
        """
        
        Evaluate the indirect discontinuous derivatives integral for a given
        sample point in boundary sample space.
        
        Parameters ``sample`` (``mi.Point3f``):
        The sample point in boundary sample space.
        
        This function returns a tuple ``(result, sensor_uv)`` where
        
        Output ``result`` (``mi.Spectrum``):
        The integrand of the indirect discontinuous derivatives.
        
        Output ``sensor_uv`` (``mi.Point2f``):
        The UV coordinates on the sensor film to splat the result to. If
        ``preprocess`` is false, this coordinate is not used.
        
        """
        ...

    def eval_primary_silhouette_radiance_difference(self, scene, sampler, ss, viewpoint, active=True) -> 'mitsuba.Float':
        """
        
        Compute the difference in radiance between two rays that hit and miss a
        silhouette point ``ss.p`` viewed from ``viewpoint``.
        
        """
        ...

    def get_projected_points(self, scene: 'mitsuba.Scene', sensor: 'mitsuba.Sensor', sampler: 'mitsuba.Sampler'):
        """
        
        Helper function to project seed rays to obtain silhouette segments and
        map them to boundary sample space.
        
        """
        ...

    def init_indirect_silhouette(self, scene: 'mitsuba.Scene', sensor: 'mitsuba.Sensor', seed: 'int'):
        """
        
        Initialize the guiding structure for indirect discontinuous derivatives
        based on the guiding mode. The result is stored in this python class.
        
        """
        ...

    def init_indirect_silhouette_grid_proj(self, scene, sensor, seed):
        """
        
        Guiding structure initialization for projective grid sampling.
        
        """
        ...

    def init_indirect_silhouette_grid_unif(self, scene, sensor, seed):
        """
        
        Guiding structure initialization for uniform grid sampling.
        
        """
        ...

    def init_indirect_silhouette_octree(self, scene, sensor, seed):
        """
        
        Guiding structure initialization for octree-based guiding.
        
        """
        ...

    def init_primarily_visible_silhouette(self, scene: 'mitsuba.Scene', sensor: 'mitsuba.Sensor'):
        """
        
        Precompute the silhouette of the scene as seen from the sensor and store
        the result in this python class.
        
        """
        ...

    def perspective_sensor_jacobian(self, sensor: 'mitsuba.Sensor', ss: 'mitsuba.SilhouetteSample3f'):
        """
        
        The silhouette sample `ss` stores (1) the sampling density in the scene
        space, and (2) the motion of the silhouette point in the scene space.
        This Jacobian corrects both quantities to the camera sample space.
        
        """
        ...

    def sample_primarily_visible_silhouette(self, scene: 'mitsuba.Scene', viewpoint: 'mitsuba.Point3f', sample2: 'mitsuba.Point2f', active: 'mitsuba.Mask') -> 'mitsuba.SilhouetteSample3f':
        """
        
        Sample a primarily visible silhouette point as seen from the sensor.
        Returns a silhouette sample struct.
        
        """
        ...

    ...

