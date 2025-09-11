import pathlib
from typing import Union

Transferable = Union[bytes, pathlib.Path]

TransferSpec = Union[tuple[Transferable, str], tuple[Transferable, str, int]]
