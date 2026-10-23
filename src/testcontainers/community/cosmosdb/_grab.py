import tarfile
import tempfile
from contextlib import contextmanager
from os import path
from pathlib import Path

from docker.models.containers import Container


@contextmanager
def file(container: Container, target: str):
    target_path = Path(target)
    assert target_path.is_absolute(), "target must be an absolute path"

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "grabbed.tar"

        # download from container as tar archive
        with open(archive, "wb") as f:
            tar_bits, _ = container.get_archive(target)
            for chunk in tar_bits:
                f.write(chunk)

        # extract target file from tar archive
        with tarfile.TarFile(archive) as tar:
            yield tar.extractfile(path.basename(target))
