from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import mitsuba
import mitsuba as mi
import drjit as dr

def absolute(arg0: mitsuba.filesystem.path) -> mitsuba.filesystem.path:
    """
    Returns an absolute path to the same location pointed by ``p``,
    relative to ``base``.
    
    See also:
        http ://en.cppreference.com/w/cpp/experimental/fs/absolute)
    """
    ...

def create_directory(arg0: mitsuba.filesystem.path) -> bool:
    """
    Creates a directory at ``p`` as if ``mkdir`` was used. Returns true if
    directory creation was successful, false otherwise. If ``p`` already
    exists and is already a directory, the function does nothing (this
    condition is not treated as an error).
    """
    ...

def current_path() -> mitsuba.filesystem.path:
    """
    Returns the current working directory (equivalent to getcwd)
    """
    ...

def equivalent(arg0: mitsuba.filesystem.path, arg1: mitsuba.filesystem.path) -> bool:
    """
    Checks whether two paths refer to the same file system object. Both
    must refer to an existing file or directory. Symlinks are followed to
    determine equivalence.
    """
    ...

def exists(arg0: mitsuba.filesystem.path) -> bool:
    """
    Checks if ``p`` points to an existing filesystem object.
    """
    ...

def file_size(arg0: mitsuba.filesystem.path) -> int:
    """
    Returns the size (in bytes) of a regular file at ``p``. Attempting to
    determine the size of a directory (as well as any other file that is
    not a regular file or a symlink) is treated as an error.
    """
    ...

def is_directory(arg0: mitsuba.filesystem.path) -> bool:
    """
    Checks if ``p`` points to a directory.
    """
    ...

def is_regular_file(arg0: mitsuba.filesystem.path) -> bool:
    """
    Checks if ``p`` points to a regular file, as opposed to a directory or
    symlink.
    """
    ...

class path:
    """
    Represents a path to a filesystem resource. On construction, the path
    is parsed and stored in a system-agnostic representation. The path can
    be converted back to the system-specific string using ``native()`` or
    ``string()``.
    """

    @overload
    def __init__(self: mitsuba.filesystem.path) -> None:
        """
        Default constructor. Constructs an empty path. An empty path is
        considered relative.
        
        """
        ...

    @overload
    def __init__(self: mitsuba.filesystem.path, arg0: mitsuba.filesystem.path) -> None:
        """
        Copy constructor.
        
        """
        ...

    @overload
    def __init__(self: mitsuba.filesystem.path, arg0: str) -> None:
        """
        Construct a path from a string with native type. On Windows, the path
        can use both '/' or '\\' as a delimiter.
        """
        ...

    def clear(self: mitsuba.filesystem.path) -> None:
        """
        Makes the path an empty path. An empty path is considered relative.
        """
        ...

    def empty(self: mitsuba.filesystem.path) -> bool:
        """
        Checks if the path is empty
        """
        ...

    def extension(self: mitsuba.filesystem.path) -> mitsuba.filesystem.path:
        """
        Returns the extension of the filename component of the path (the
        substring starting at the rightmost period, including the period).
        Special paths '.' and '..' have an empty extension.
        """
        ...

    def filename(self: mitsuba.filesystem.path) -> mitsuba.filesystem.path:
        """
        Returns the filename component of the path, including the extension.
        """
        ...

    def is_absolute(self: mitsuba.filesystem.path) -> bool:
        """
        Checks if the path is absolute.
        """
        ...

    def is_relative(self: mitsuba.filesystem.path) -> bool:
        """
        Checks if the path is relative.
        """
        ...

    def native(self: mitsuba.filesystem.path) -> str:
        """
        Returns the path in the form of a native string, so that it can be
        passed directly to system APIs. The path is constructed using the
        system's preferred separator and the native string type.
        """
        ...

    def parent_path(self: mitsuba.filesystem.path) -> mitsuba.filesystem.path:
        """
        Returns the path to the parent directory. Returns an empty path if it
        is already empty or if it has only one element.
        """
        ...

    def replace_extension(self: mitsuba.filesystem.path, arg0: mitsuba.filesystem.path) -> mitsuba.filesystem.path:
        """
        Replaces the substring starting at the rightmost '.' symbol by the
        provided string.
        
        A '.' symbol is automatically inserted if the replacement does not
        start with a dot. Removes the extension altogether if the empty path
        is passed. If there is no extension, appends a '.' followed by the
        replacement. If the path is empty, '.' or '..', the method does
        nothing.
        
        Returns *this.
        """
        ...

    ...

preferred_separator = ...
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
def remove(arg0: mitsuba.filesystem.path) -> bool:
    """
    Removes a file or empty directory. Returns true if removal was
    successful, false if there was an error (e.g. the file did not exist).
    """
    ...

def resize_file(arg0: mitsuba.filesystem.path, arg1: int) -> bool:
    """
    Changes the size of the regular file named by ``p`` as if ``truncate``
    was called. If the file was larger than ``target_length``, the
    remainder is discarded. The file must exist.
    """
    ...

