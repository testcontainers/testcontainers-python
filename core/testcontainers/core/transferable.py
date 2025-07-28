import dataclasses
import pathlib
from typing import Union


@dataclasses.dataclass
class Transferable:
    """
    Wrapper class enabling copying files into a container
    """

    source: Union[bytes, pathlib.Path]
    destination_in_container: str
    mode: int = 0o644
