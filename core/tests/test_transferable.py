from pathlib import Path

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.transferable import Transferable, TransferSpec, build_transfer_tar

import io
import tarfile
from typing import Any


def test_build_transfer_tar_from_bytes():
    data = b"hello world"
    tar_bytes = build_transfer_tar(data, "/tmp/my_file")

    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
        members = tar.getmembers()
        assert len(members) == 1
        assert members[0].name == "/tmp/my_file"
        assert members[0].size == len(data)
        assert members[0].mode == 0o644
        extracted = tar.extractfile(members[0])
        assert extracted is not None
        assert extracted.read() == data


def test_build_transfer_tar_from_file(tmp_path: Path):
    my_file = tmp_path / "my_file"
    my_file.write_bytes(b"file content")

    tar_bytes = build_transfer_tar(my_file, "/dest/my_file", mode=0o755)

    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
        members = tar.getmembers()
        assert len(members) == 1
        assert members[0].name == "/dest/my_file"
        assert members[0].mode == 0o755
        extracted = tar.extractfile(members[0])
        assert extracted is not None
        assert extracted.read() == b"file content"


def test_build_transfer_tar_from_directory(tmp_path: Path):
    source_dir = tmp_path / "my_dir"
    source_dir.mkdir()
    (source_dir / "a.txt").write_bytes(b"aaa")

    tar_bytes = build_transfer_tar(source_dir, "/dest")

    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
        names = tar.getnames()
        assert any("my_dir" in n for n in names)
        assert any("a.txt" in n for n in names)


def test_build_transfer_tar_rejects_invalid_type():
    with pytest.raises(TypeError, match="source must be bytes or Path"):
        invalid: Any = 123
        build_transfer_tar(invalid, "/tmp/bad")


def test_build_transfer_tar_rejects_nonexistent_path(tmp_path: Path):
    bad_path = tmp_path / "does_not_exist"
    with pytest.raises(TypeError, match="neither a file nor directory"):
        build_transfer_tar(bad_path, "/tmp/bad")


@pytest.fixture(name="transferable", params=(bytes, Path))
def copy_sources_fixture(request, tmp_path: Path):
    """
    Provide source argument for tests of copy_into_container
    """
    raw_data = b"hello world"
    if request.param is bytes:
        return raw_data
    elif request.param is Path:
        my_file = tmp_path / "my_file"
        my_file.write_bytes(raw_data)
        return my_file
    pytest.fail("Invalid type")


def test_copy_into_container_at_runtime(transferable: Transferable):
    destination_in_container = "/tmp/my_file"

    with DockerContainer("bash", command="sleep infinity") as container:
        container.copy_into_container(transferable, destination_in_container)
        result = container.exec(f"cat {destination_in_container}")

    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_into_container_at_startup(transferable: Transferable):
    destination_in_container = "/tmp/my_file"

    container = DockerContainer("bash", command="sleep infinity")
    container.with_copy_into_container(transferable, destination_in_container)

    with container:
        result = container.exec(f"cat {destination_in_container}")

    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_into_startup_file(transferable: Transferable):
    destination_in_container = "/tmp/my_file"

    container = DockerContainer("bash", command=f"cat {destination_in_container}")
    container.with_copy_into_container(transferable, destination_in_container)

    with container:
        exit_code = container.wait()
        stdout, _ = container.get_logs()
        assert exit_code == 0
        assert stdout.decode() == "hello world"


def test_copy_into_container_via_initializer(transferable: Transferable):
    destination_in_container = "/tmp/my_file"
    transferables: list[TransferSpec] = [(transferable, destination_in_container, 0o644)]

    with DockerContainer("bash", command="sleep infinity", transferables=transferables) as container:
        result = container.exec(f"cat {destination_in_container}")

    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_file_from_container(tmp_path: Path):
    file_in_container = "/tmp/foo.txt"
    destination_on_host = tmp_path / "foo.txt"
    assert not destination_on_host.is_file()

    with DockerContainer("bash", command="sleep infinity") as container:
        result = container.exec(f'bash -c "echo -n hello world > {file_in_container}"')
        assert result.exit_code == 0
        container.copy_from_container(file_in_container, destination_on_host)

    assert destination_on_host.is_file()
    assert destination_on_host.read_text() == "hello world"


def test_copy_directory_into_container(tmp_path: Path):
    source_dir = tmp_path / "my_directory"
    source_dir.mkdir()
    my_file = source_dir / "my_file"
    my_file.write_bytes(b"hello world")

    destination_in_container = "/tmp/my_destination_directory"

    with DockerContainer("bash", command="sleep infinity") as container:
        container.copy_into_container(source_dir, destination_in_container)
        result = container.exec(f"ls {destination_in_container}")

        assert result.exit_code == 0
        assert result.output == b"my_directory\n"

        result = container.exec(f"ls {destination_in_container}/my_directory")
        assert result.exit_code == 0
        assert result.output == b"my_file\n"

        result = container.exec(f"cat {destination_in_container}/my_directory/my_file")
        assert result.exit_code == 0
        assert result.output == b"hello world"
