import tempfile
from io import BytesIO
from pathlib import Path
from tarfile import TarFile
from tarfile import open as tarfile_open

from testcontainers.core.transferable import (
    BytesTransferable,
    FileTransferable,
    # IoObject,
    StringTransferable,
    Transferable,
)


def handle_transferable(transferable: Transferable) -> bytes:
    location_to_use = "/hello"

    # lifted from kafka module
    with BytesIO() as archive, TarFile(fileobj=archive, mode="w") as tar:
        transferable.transfer_to(tar, location_to_use)

        archive.seek(0)

        with tarfile_open(fileobj=archive, mode="r") as tar_read:
            extracted_file = tar_read.extractfile(tar_read.getmember(location_to_use))
            if extracted_file is None:
                raise FileNotFoundError(f"no location {location_to_use}")
            return extracted_file.read()


def test_file_transferable_size():
    with tempfile.NamedTemporaryFile(prefix="tc-python-core-file-trx-test-size") as f:
        some_bytes = b"hello, world!"
        Path(f.file.name).write_bytes(some_bytes)
        f = FileTransferable(f.name)
        assert len(some_bytes) == f.get_size()


def test_file_transferable_content():
    with tempfile.NamedTemporaryFile(prefix="tc-python-core-file-trx-test-content") as f:
        some_bytes = b"hello, world!"
        Path(f.file.name).write_bytes(some_bytes)
        f = FileTransferable(f.name)

        contents_of_transferable = handle_transferable(f)
        assert some_bytes == contents_of_transferable


def test_string_transferable_size():
    assert StringTransferable("").get_size() == 0
    assert StringTransferable("abc").get_size() == 3
    assert StringTransferable("abc-").get_size() == 4
    assert StringTransferable("abc-ஹ").get_size() == 7


def test_bytes_transferable_size():
    assert BytesTransferable(b"").get_size() == 0
    assert BytesTransferable(b"abc").get_size() == 3
