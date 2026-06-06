import io
import pathlib
import tarfile
from typing import Union

Transferable = Union[bytes, pathlib.Path]

TransferSpec = Union[tuple[Transferable, str], tuple[Transferable, str, int]]


def build_transfer_tar(transferable: Transferable, destination: str, mode: int = 0o644) -> bytes:
    """Build a tar archive containing the transferable, ready for put_archive(path="/")."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        if isinstance(transferable, bytes):
            info = tarfile.TarInfo(name=destination)
            info.size = len(transferable)
            info.mode = mode
            tar.addfile(info, io.BytesIO(transferable))
        elif isinstance(transferable, pathlib.Path):
            if transferable.is_file():
                info = tarfile.TarInfo(name=destination)
                info.size = transferable.stat().st_size
                info.mode = mode
                with transferable.open("rb") as f:
                    tar.addfile(info, f)
            elif transferable.is_dir():
                tar.add(str(transferable), arcname=f"{destination.rstrip('/')}/{transferable.name}")
            else:
                raise TypeError(f"Path {transferable} is neither a file nor directory")
        else:
            raise TypeError("source must be bytes or Path")
    return buf.getvalue()
