import os
import tarfile
from abc import ABC, abstractmethod
from contextlib import closing
from dataclasses import dataclass
from io import BufferedIOBase, BytesIO
from os import PathLike
from typing import BinaryIO, Union

__all__ = [
    "IoObject",
    "Transferable",
    "StringTransferable",
    "BytesTransferable",
    "FileTransferable",
]

# hack, because the functions we use here all return items having isinstance(x, BufferedIOBase)
# python best
IoObject = Union[BufferedIOBase, BytesIO, BinaryIO]


class Transferable(ABC):
    DEFAULT_FILE_MODE = 0o644
    DEFAULT_DIR_MODE = 0o755

    @staticmethod
    def of(content: Union[str, bytes, PathLike], file_mode: int = DEFAULT_FILE_MODE):
        if isinstance(content, PathLike):
            return FileTransferable(file=content, file_mode=file_mode)
        elif isinstance(content, bytes):
            return BytesTransferable(content=content, file_mode=file_mode)
        elif isinstance(content, str):
            return StringTransferable(content=content, file_mode=file_mode)
        raise TypeError(f"need to implement a custom Transferable for {type(content)}")

    def transfer_to(self, tar_archive: tarfile.TarFile, destination):
        tar_entry = tarfile.TarInfo(name=destination)
        tar_entry.size = self.get_size()
        tar_entry.mode = self.get_mode()
        with closing(self.get_content()) as content:
            tar_archive.addfile(tar_entry, content)

    @abstractmethod
    def get_content(self) -> IoObject:
        ...

    # noinspection PyMethodMayBeStatic
    def get_mode(self):
        return Transferable.DEFAULT_FILE_MODE

    @abstractmethod
    def get_size(self) -> int:
        ...


@dataclass
class StringTransferable(Transferable):
    content: str
    encoding: str = "utf-8"
    file_mode: int = Transferable.DEFAULT_FILE_MODE
    _content_bytes: bytes = None

    def __post_init__(self):
        self._content_bytes = self.content.encode(self.encoding)

    def get_content(self) -> IoObject:
        return BytesIO(self._content_bytes)

    def get_mode(self):
        return self.file_mode

    def get_size(self) -> int:
        return len(self._content_bytes)


@dataclass
class BytesTransferable(Transferable):
    content: bytes
    file_mode: int = Transferable.DEFAULT_FILE_MODE

    def get_content(self) -> BytesIO:
        return BytesIO(self.content)

    def get_mode(self):
        return self.file_mode

    def get_size(self) -> int:
        return len(self.content)


@dataclass
class FileTransferable(Transferable):
    file: str | PathLike
    file_mode: int = Transferable.DEFAULT_FILE_MODE

    def get_content(self) -> IoObject:
        return open(self.file, 'rb')

    def get_mode(self):
        return self.file_mode

    def get_size(self) -> int:
        return os.stat(self.file).st_size
