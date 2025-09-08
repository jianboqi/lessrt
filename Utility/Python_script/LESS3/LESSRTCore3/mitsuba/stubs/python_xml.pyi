from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

class Files:
    """
        Enum for different files or dicts containing specific info
        
    """

    ...

class WriteXML:
    """
        File Writing API
        Populates a dictionary with scene data, then writes it to XML.
        
    """

    def add_comment(self, comment, file=0):
        """
        
        Add a comment to the scene dict
        
        Parameter ``comment``:
        text of the comment
        Parameter ``file``:
        the subdict to which to add the comment
        
        """
        ...

    def add_include(self, file):
        """
        
        Add an include tag to the main file.
        This is used when splitting the XML scene file in multiple fragments.
        
        Parameters:
        
        Parameter ``file``:
        the file to include
        
        """
        ...

    def close_element(self, file=None):
        """
        
        Close the last tag we opened in a given file.
        
        Parameter ``file``:
        The file to write to
        
        """
        ...

    def configure_defaults(self, scene_dict):
        """
        
        Traverse the scene graph and look for properties in the defaults dict.
        For such properties, store their value in a default tag and replace the value by $name in the prop.
        
        Parameter ``scene_dict``:
        The dictionary containing the scene info
        
        """
        ...

    def current_tag(self):
        """
        
        Get the tag in which we are currently writing
        
        """
        ...

    def data_add(self, key, value, file=0):
        """
        
        Add an entry to a given subdict.
        
        Parameter ``key``:
        dict key
        Parameter ``value``:
        entry
        Parameter ``file``:
        the subdict to which to add the data
        
        """
        ...

    def decompose_transform(self, transform, export_scale=False):
        """
        
        Export a transform as a combination of rotation, scale and translation.
        This helps manually modifying the transform after export (for cameras for instance)
        
        Parameter ``transform``:
        The ScalarTransform4f transform matrix to decompose
        Parameter ``export_scale``:
        Whether to add a scale property or not. (e.g. don't do it for cameras to avoid clutter)
        
        """
        ...

    def element(self, name, attributes={}, file=None):
        """
        
        Write a single-line XML element.
        
        Parameter ``name``:
        Name of the element (e.g. integer, string, rotate...)
        Parameter ``attributes``:
        Additional fields to add to the element (e.g. name, value...)
        Parameter ``file``:
        The file to write to
        
        """
        ...

    def exit(self): ...
    def format_path(self, filepath, tag):
        """
        
        Given a filepath, either copy it in the scene folder (in the corresponding directory)
        or convert it to a relative path.
        
        Parameter ``filepath``:
        the path to the given file
        Parameter ``tag``:
        the tag this path property belongs to in (shape, texture, spectrum)
        
        """
        ...

    def format_spectrum(self, entry, entry_type):
        """
        
        Format rgb or spectrum tags to the proper XML output.
        The entry should contain the name and value of the spectrum entry.
        The type is passed separately, since it is popped from the dict in write_dict
        
        Parameter ``entry``:
        The dict containing the spectrum
        Parameter ``entry_type``:
        Either 'spectrum' or 'rgb'
        
        """
        ...

    def get_plugin_tag(self, plugin_type):
        """
        
        Get the corresponding tag of a given plugin (e.g. 'bsdf' for 'diffuse')
        If the given type (e.g. 'transform') is not a plugin, returns None.
        
        Parameter ``plugin_type``:
        Name of the type (e.g. 'diffuse', 'ply'...)
        
        """
        ...

    def open_element(self, name, attributes={}, file=None):
        """
        
        Open an XML tag (e.g. emitter, bsdf...)
        
        Parameter ``name``:
        Name of the tag (emitter, bsdf, shape...)
        Parameter ``attributes``:
        Additional fields to add to the opening tag (e.g. name, type...)
        Parameter ``file``:
        File to write to
        
        """
        ...

    def preprocess_scene(self, scene_dict):
        """
        
        Preprocess the scene dictionary before writing it to file:
        - Add default properties.
        - Reorder the scene dict before writing it to file.
        - Separate the dict into different category-specific subdicts.
        - If not splitting files, merge them in the end.
        
        Parameter ``scene_dict``:
        The dictionary containing the scene data
        
        """
        ...

    def process(self, scene_dict):
        """
        
        Preprocess then write the input dict to XML file format
        
        Parameter ``scene_dict``:
        The dictionary containing all the scene info.
        
        """
        ...

    def set_filename(self, name):
        """
        
        Open the files for output,
        using filenames based on the given base name.
        Create the necessary folders to create the file at the specified path.
        
        Parameter ``name``:
        path to the scene.xml file to write.
        
        """
        ...

    def set_output_file(self, file):
        """
        
        Switch next output to the given file index
        
        Parameter ``file``:
        index of the file to start writing to
        
        """
        ...

    def transform_matrix(self, transform):
        """
        
        Converts a mitsuba ScalarTransform4f into a dict entry.
        This dict entry won't have a 'type' because it's handled in a specific case.
        
        Parameter ``transform``:
        The given transform matrix
        
        """
        ...

    def wf(self, ind, st, tabs=0):
        """
        
        Write a string to file index ind.
        Optionally indent the string by a number of tabs
        
        Parameter ``ind``:
        index of the file to write to
        Parameter ``st``:
        text to write
        Parameter ``tabs``:
        optional number of tabs to add
        
        """
        ...

    def write_comment(self, comment, file=None):
        """
        
        Write an XML comment to file.
        
        Parameter ``comment``:
        The text of the comment to write
        Parameter ``file``:
        Index of the file to write to
        
        """
        ...

    def write_dict(self, data):
        """
        
        Main XML writing routine.
        Given a dictionary, iterate over its entries and write them to file.
        Calls itself for nested dictionaries.
        
        Parameter ``data``:
        The dictionary to write to file.
        
        """
        ...

    def write_header(self, file, comment=None):
        """
        
        Write an XML header to a specified file.
        Optionally add a comment to describe the file.
        
        Parameter ``file``:
        The file to write to
        Parameter ``comment``:
        Optional comment to add (e.g. "# Geometry file")
        
        """
        ...

    ...

def copy2(src, dst, *, follow_symlinks=True):
    """
    Copy data and metadata. Return the file's destination.
    
    Metadata is copied with copystat(). Please see the copystat function
    for more information.
    
    The destination may be a directory.
    
    If follow_symlinks is false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".
    
    """
    ...

def dict_to_xml(scene_dict, filename, split_files=False):
    """
    
    Converts a Mitsuba dictionary into its XML representation.
    
    Parameter ``scene_dict``:
    Mitsuba dictionary
    Parameter ``filename``:
    Output filename
    Parameter ``split_files``:
    Whether to split the scene into multiple files (default: False)
    
    """
    ...

