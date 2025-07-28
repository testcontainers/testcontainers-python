import dataclasses
import os
from typing import Union


@dataclasses.dataclass
class Transferable:
    source: Union[bytes, os.PathLike]
    destination_in_container: str
    mode: int = 0o644
