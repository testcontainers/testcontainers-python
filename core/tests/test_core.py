import tempfile
from pathlib import Path

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.transferable import Transferable, TransferSpec


def test_garbage_collection_is_defensive():
    # For more info, see https://github.com/testcontainers/testcontainers-python/issues/399
    # we simulate garbage collection: start, stop, then call `del`
    container = DockerContainer("postgres:latest")
    container.start()
    container.stop(force=True, delete_volume=True)
    delattr(container, "_container")
    del container


def test_get_logs():
    with DockerContainer("hello-world") as container:
        stdout, stderr = container.get_logs()
        assert isinstance(stdout, bytes)
        assert isinstance(stderr, bytes)
        assert "Hello from Docker".encode() in stdout, "There should be something on stdout"


def test_docker_container_with_env_file():
    """Test that environment variables can be loaded from a file"""
    with tempfile.TemporaryDirectory() as temp_directory:
        env_file_path = Path(temp_directory) / "env_file"
        with open(env_file_path, "w") as f:
            f.write(
                """
                TEST_ENV_VAR=hello
                NUMBER=123
                DOMAIN=example.org
                ADMIN_EMAIL=admin@${DOMAIN}
                ROOT_URL=${DOMAIN}/app
                """
            )
        container = DockerContainer("alpine").with_command("tail -f /dev/null")  # Keep the container running
        container.with_env_file(env_file_path)  # Load the environment variables from the file
        with container:
            output = container.exec("env").output.decode("utf-8").strip()
            assert "TEST_ENV_VAR=hello" in output
            assert "NUMBER=123" in output
            assert "DOMAIN=example.org" in output
            assert "ADMIN_EMAIL=admin@example.org" in output
            assert "ROOT_URL=example.org/app" in output
            print(output)


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
    # Given
    destination_in_container = "/tmp/my_file"

    with DockerContainer("bash", command="sleep infinity") as container:
        # When
        container.copy_into_container(transferable, destination_in_container)
        result = container.exec(f"cat {destination_in_container}")

    # Then
    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_into_container_at_startup(transferable: Transferable):
    # Given
    destination_in_container = "/tmp/my_file"

    container = DockerContainer("bash", command="sleep infinity")
    container.with_copy_into_container(transferable, destination_in_container)

    with container:
        # When
        result = container.exec(f"cat {destination_in_container}")

    # Then
    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_into_container_via_initializer(transferable: Transferable):
    # Given
    destination_in_container = "/tmp/my_file"
    transferables: list[TransferSpec] = [(transferable, destination_in_container, 0o644)]

    with DockerContainer("bash", command="sleep infinity", transferables=transferables) as container:
        # When
        result = container.exec(f"cat {destination_in_container}")

    # Then
    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_file_from_container(tmp_path: Path):
    # Given
    file_in_container = "/tmp/foo.txt"
    destination_on_host = tmp_path / "foo.txt"
    assert not destination_on_host.is_file()

    with DockerContainer("bash", command="sleep infinity") as container:
        result = container.exec(f'bash -c "echo -n hello world > {file_in_container}"')
        assert result.exit_code == 0

        # When
        container.copy_from_container(file_in_container, destination_on_host)

    # Then
    assert destination_on_host.is_file()
    assert destination_on_host.read_text() == "hello world"


def test_copy_directory_into_container(tmp_path: Path):
    # Given
    source_dir = tmp_path / "my_directory"
    source_dir.mkdir()
    my_file = source_dir / "my_file"
    my_file.write_bytes(b"hello world")

    destination_in_container = "/tmp/my_destination_directory"

    with DockerContainer("bash", command="sleep infinity") as container:
        # When
        container.copy_into_container(source_dir, destination_in_container)
        result = container.exec(f"ls {destination_in_container}")

        # Then - my_directory exists
        assert result.exit_code == 0
        assert result.output == b"my_directory\n"

        # Then - my_file is in directory
        result = container.exec(f"ls {destination_in_container}/my_directory")
        assert result.exit_code == 0
        assert result.output == b"my_file\n"

        # Then - my_file contents are correct
        result = container.exec(f"cat {destination_in_container}/my_directory/my_file")
        assert result.exit_code == 0
        assert result.output == b"hello world"
