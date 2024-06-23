import pytest
import tempfile
import random

from typing import Optional, Tuple

from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
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
@pytest.mark.parametrize("test_build_arg", [None, ("buildargkey", "buildargval")])
def test_docker_image(test_image_tag: Optional[str], test_cleanup: bool, test_build_arg: Optional[Tuple[str, str]], check_for_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        # It's important to use a random string to avoid image caching
        random_string = "Hello from Docker Image! " + str(random.randint(0, 1000))
        build_arg_name = test_build_arg[0] if test_build_arg else "MISSING"
        build_arg_value = test_build_arg[1] if test_build_arg else "MISSING"
        with open(f"{temp_directory}/Dockerfile", "w") as f:
            f.write(
                f"""
                FROM alpine:latest
                ARG {build_arg_name}
                ENV {build_arg_name}=${build_arg_name}
                CMD echo "{random_string} ${build_arg_name}"
                """
            )
        with DockerImage(
            path=temp_directory, tag=test_image_tag, clean_up=test_cleanup, build_args={build_arg_name: build_arg_value}
        ) as image:
            image_short_id = image.short_id
            assert image.tag is test_image_tag, f"Expected {test_image_tag}, got {image.tag}"
            assert image.short_id is not None, "Short ID should not be None"
            logs = image.get_logs()
            assert isinstance(logs, list), "Logs should be a list"
            assert any("Step 1" in log.get("stream", "") for log in logs)
            assert any("FROM alpine:latest" in log.get("stream", "") for log in logs)
            assert any("Step 2" in log.get("stream", "") for log in logs)
            # assert any(f'CMD echo "{random_string} {build_arg_value}"' in log.get("stream", "") for log in logs)
            with DockerContainer(str(image)) as container:
                assert container._container.image.short_id.endswith(image_short_id), "Image ID mismatch"
                assert container.get_logs() == ((f"{random_string} {build_arg_value}\n").encode(), b""), "Container logs mismatch"

        check_for_image(image_short_id, test_cleanup)
