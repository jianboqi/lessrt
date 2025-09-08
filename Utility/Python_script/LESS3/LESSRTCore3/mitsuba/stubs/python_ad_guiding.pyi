from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

class BaseGuidingDistr:
    def sample(self, sampler):
        """
        
        Return a sample in U^3 from the stored guiding distribution and its
        reciprocal density.
        
        """
        ...

    ...

class GridDistr(BaseGuidingDistr):
    """
        Regular grid guiding distribution.
        
    """

    def get_cell_array(self, index_array_):
        """
        
        Returns the 3D cell index corresponding to the 1D input index.
        
        With `index_array`=dr.arange(mi.UInt32, self.num_cells), the output
        array of this function is [[0, 0, 0], [0, 0, 1], ..., [Nx-1, Ny-1, Nz-1]].
        
        """
        ...

    def random_cell_sample(self, sampler): ...
    def sample(self, sampler): ...
    def sample_to_cell_idx(self, sample, active=True): ...
    def set_mass(self, mass):
        """
        
        Sets the grid's density with the flat-1D input mass
        
        """
        ...

    ...

class OcSpaceDistr(BaseGuidingDistr):
    """
        Octree space partitioned distribution.
        
    """

    def construct_octree(self, points, log=False):
        """
        
        Octree construction/partitioning for the given `input` points.
        
        """
        ...

    def estimate_mass_in_leaves(self, aabb_min, aabb_max, seed, log: 'bool' = False):
        """
        
        Evaluates `extra_spc` random samples in each leaf to compute an average
        mass per leaf.
        
        """
        ...

    def sample(self, sampler): ...
    def set_points(self, points, mass, seed=0, log=False):
        """
        
        Builds an octree from a set of points and their corresponding mass
        
        """
        ...

    ...

class UniformDistr(BaseGuidingDistr):
    def sample(self, sampler): ...
    ...

