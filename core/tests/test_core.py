import pytest
import tempfile
import random
import os

from pathlib import Path
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.transferable import Transferable
from testcontainers.core.waiting_utils import wait_for_logs


def test_timeout_is_raised_when_waiting_for_logs():
    with pytest.raises(TimeoutError), DockerContainer("alpine").with_command("sleep 2") as container:
        wait_for_logs(container, "Hello from Docker!", timeout=1e-3)


def test_garbage_collection_is_defensive():
    # For more info, see https://github.com/testcontainers/testcontainers-python/issues/399
    # we simulate garbage collection: start, stop, then call `del`
    container = DockerContainer("postgres:latest")
    container.start()
    container.stop(force=True, delete_volume=True)
    delattr(container, "_container")
    del container


def test_wait_for_hello():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")


def test_can_get_logs():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        stdout, stderr = container.get_logs()
        assert isinstance(stdout, bytes)
        assert isinstance(stderr, bytes)
        assert stdout, "There should be something on stdout"


@pytest.mark.parametrize("test_cleanup", [True, False])
@pytest.mark.parametrize("test_image_tag", [None, "test-image:latest"])
def test_docker_image(test_image_tag: Optional[str], test_cleanup: bool, check_for_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        # It's important to use a random string to avoid image caching
        random_string = "Hello from Docker Image! " + str(random.randint(0, 1000))
        with open(f"{temp_directory}/Dockerfile", "w") as f:
            f.write(
                f"""
                FROM alpine:latest
                CMD echo "{random_string}"
                """
            )
        with DockerImage(path=temp_directory, tag=test_image_tag, clean_up=test_cleanup) as image:
            image_short_id = image.short_id
            assert image.tag is test_image_tag, f"Expected {test_image_tag}, got {image.tag}"
            assert image.short_id is not None, "Short ID should not be None"
            logs = image.get_logs()
            assert isinstance(logs, list), "Logs should be a list"
            assert logs[0] == {"stream": "Step 1/2 : FROM alpine:latest"}
            assert logs[3] == {"stream": f'Step 2/2 : CMD echo "{random_string}"'}
            with DockerContainer(str(image)) as container:
                assert container._container.image.short_id.endswith(image_short_id), "Image ID mismatch"
                assert container.get_logs() == ((random_string + "\n").encode(), b""), "Container logs mismatch"

        check_for_image(image_short_id, test_cleanup)


@pytest.mark.parametrize("dockerfile_path", [None, Path("subdir/my.Dockerfile")])
def test_docker_image_with_custom_dockerfile_path(dockerfile_path: Optional[Path]):
    with tempfile.TemporaryDirectory() as temp_directory:
        temp_dir_path = Path(temp_directory)
        if dockerfile_path:
            os.makedirs(temp_dir_path / dockerfile_path.parent, exist_ok=True)
            dockerfile_rel_path = dockerfile_path
            dockerfile_kwargs = {"dockerfile_path": dockerfile_path}
        else:
            dockerfile_rel_path = Path("Dockerfile")  # default
            dockerfile_kwargs = {}

        with open(temp_dir_path / dockerfile_rel_path, "x") as f:
            f.write(
                f"""
                FROM alpine:latest
                CMD echo "Hello world!"
                """
            )
        with DockerImage(path=temp_directory, tag="test", clean_up=True, no_cache=True, **dockerfile_kwargs) as image:
            image_short_id = image.short_id
            with DockerContainer(str(image)) as container:
                assert container._container.image.short_id.endswith(image_short_id), "Image ID mismatch"
                assert container.get_logs() == (("Hello world!\n").encode(), b""), "Container logs mismatch"


def test_docker_start_with_copy_file_to_container_from_binary_transferable() -> None:
    container = DockerContainer("nginx")
    data = "test_docker_start_with_copy_file_to_container_from_binary_transferable"

    input_data = data.encode("utf-8")
    output_file = Path("/tmp/test_docker_start_with_copy_file_to_container_from_binary_transferable.txt")

    container.with_copy_file_to_container(Transferable.of(input_data), output_file).start()

    _, stdout = container.exec(f"cat {output_file}")
    assert stdout.decode() == data


def test_docker_start_with_copy_file_to_container_from_file_transferable() -> None:
    container = DockerContainer("nginx")
    data = "test_docker_start_with_copy_file_to_container_from_file_transferable"

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(data.encode("utf-8"))
        f.seek(0)

        input_file = Path(f.name)
        output_file = Path("/tmp/test_docker_start_with_copy_file_to_container_from_file_transferable.txt")

        container.with_copy_file_to_container(Transferable.of(input_file), output_file).start()

        _, stdout = container.exec(f"cat {output_file}")
        assert stdout.decode() == data
