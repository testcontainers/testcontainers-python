import tempfile
from pathlib import Path

from testcontainers.core.container import DockerContainer, Transferrable


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


def test_copy_file_into_container_at_runtime(tmp_path: Path):
    # Given
    my_file = tmp_path / "my_file"
    my_file.write_text("hello world")
    destination_in_container = "/tmp/my_file"

    with DockerContainer("bash", command="sleep infinity") as container:
        # When
        container.copy_into_container(my_file, destination_in_container)
        result = container.exec(f"cat {destination_in_container}")

    # Then
    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_file_into_container_at_startup(tmp_path: Path):
    # Given
    my_file = tmp_path / "my_file"
    my_file.write_text("hello world")
    destination_in_container = "/tmp/my_file"

    container = DockerContainer("bash", command="sleep infinity")
    container.with_copy_into_container(my_file, destination_in_container)

    with container:
        # When
        result = container.exec(f"cat {destination_in_container}")

    # Then
    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_file_into_container_via_initializer(tmp_path: Path):
    # Given
    my_file = tmp_path / "my_file"
    my_file.write_text("hello world")
    destination_in_container = "/tmp/my_file"

    with DockerContainer(
        "bash", command="sleep infinity", transferrables=(Transferrable(my_file, destination_in_container),)
    ) as container:
        # When
        result = container.exec(f"cat {destination_in_container}")

    # Then
    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_bytes_to_container_at_runtime():
    # Given
    file_content = b"hello world"
    destination_in_container = "/tmp/my_file"

    with DockerContainer("bash", command="sleep infinity") as container:
        # When
        container.copy_into_container(file_content, destination_in_container)

        # Then
        result = container.exec(f"cat {destination_in_container}")

    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_bytes_to_container_at_startup():
    # Given
    file_content = b"hello world"
    destination_in_container = "/tmp/my_file"

    container = DockerContainer("bash", command="sleep infinity")
    container.with_copy_into_container(file_content, destination_in_container)

    with container:
        # When
        result = container.exec(f"cat {destination_in_container}")

    # Then
    assert result.exit_code == 0
    assert result.output == b"hello world"


def test_copy_bytes_to_container_via_initializer():
    # Given
    file_content = b"hello world"
    destination_in_container = "/tmp/my_file"

    with DockerContainer(
        "bash", command="sleep infinity", transferrables=(Transferrable(file_content, destination_in_container),)
    ) as container:
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
