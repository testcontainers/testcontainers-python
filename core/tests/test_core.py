import pytest
import tempfile

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


def test_from_image():
    test_image_tag = "test-image:latest"
    with tempfile.TemporaryDirectory() as temp_directory:
        with open(f"{temp_directory}/Dockerfile", "w") as f:
            f.write(
                """
                FROM alpine:latest
                CMD echo "Hello from Docker Image!"
                """
            )
            f.close()
            with DockerImage(tag=test_image_tag, path=temp_directory) as image:
                assert image.tag == test_image_tag
                logs = image.get_logs()
                assert isinstance(logs, list)
                assert logs[0] == {"stream": "Step 1/2 : FROM alpine:latest"}
                assert logs[3] == {"stream": 'Step 2/2 : CMD echo "Hello from Docker Image!"'}
                with DockerContainer(image.tag) as container:
                    wait_for_logs(container, "Hello from Docker Image!")
