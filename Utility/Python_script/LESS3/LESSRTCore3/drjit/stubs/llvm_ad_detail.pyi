from typing import Any, Callable, Iterable, Iterator, Tuple, List, TypeVar, Union, overload
import drjit
import drjit as dr

def ad_add_edge(src_index: int, dst_index: int, cb: handle = None) -> None: ...
