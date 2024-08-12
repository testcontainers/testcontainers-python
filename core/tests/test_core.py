import pytest
import tempfile
import random
import os

from pathlib import Path
from typing import Optional

from testcontainers.core.container import DockerContainer, docker
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


def test_docker_start_with_copy_file_to_container(tmp_path: Path) -> None:
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text('FROM alpine:latest\nCMD ["cat", "/hello_world.txt"]\n')
    helloworld_filepath = tmp_path / "hello_world.txt"
    helloworld_filepath.write_text("Hello, World!\n")
    with DockerImage(path=tmp_path) as image:
        with DockerContainer(image=str(image)).with_copy_file_to_container(
            helloworld_filepath.absolute(), "/hello_world.txt"
        ) as container:
            stdout, stderr = container.get_logs()
            assert stdout.decode() == "Hello, World!\n"


def test_docker_start_with_copy_file_to_container_several_times(tmp_path: Path) -> None:
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text('FROM alpine:latest\nCMD ["cat", "/one.txt", "/two.txt", "/three.txt"]\n')
    one_filepath = tmp_path / "one.txt"
    one_filepath.write_text("1")
    two_filepath = tmp_path / "two.txt"
    two_filepath.write_text("2")
    three_filepath = tmp_path / "three.txt"
    three_filepath.write_text("3")
    with DockerImage(path=tmp_path) as image:
        with (
            DockerContainer(image=str(image))
            .with_copy_file_to_container(one_filepath.absolute(), "/one.txt")
            .with_copy_file_to_container(two_filepath.absolute(), "/two.txt")
            .with_copy_file_to_container(three_filepath.absolute(), "/three.txt") as container
        ):
            stdout, stderr = container.get_logs()
            assert stdout.decode() == "123"


def test_docker_start_with_copy_file_to_container_from_directory(tmp_path: Path) -> None:
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text(
        'FROM alpine:latest\nCMD ["cat", "/numbers/one.txt", "/numbers/two.txt", "/numbers/three.txt"]\n'
    )
    numbers_dirpath = tmp_path / "numbers"
    numbers_dirpath.mkdir()
    one_filepath = numbers_dirpath / "one.txt"
    one_filepath.write_text("1")
    two_filepath = numbers_dirpath / "two.txt"
    two_filepath.write_text("2")
    three_filepath = numbers_dirpath / "three.txt"
    three_filepath.write_text("3")
    with DockerImage(path=tmp_path) as image:
        with DockerContainer(image=str(image)).with_copy_file_to_container(
            numbers_dirpath.absolute(), "/numbers"
        ) as container:
            stdout, stderr = container.get_logs()
            assert stdout.decode() == "123"


def test_docker_start_with_copy_file_to_container_not_readonly(tmp_path: Path) -> None:
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text(
        'FROM alpine:latest\nCMD ["/bin/sh", "-c", "echo \'Hello, World!\' > /hello_world.txt"]\n'
    )
    helloworld_filepath = tmp_path / "hello_world.txt"
    helloworld_filepath.write_text("sentinel")
    with DockerImage(path=tmp_path) as image:
        with DockerContainer(image=str(image)).with_copy_file_to_container(
            helloworld_filepath.absolute(),
            "/hello_world.txt",
            read_only=False,
        ) as container:
            stdout, stderr = container.get_logs()
            assert stdout.decode() == ""
    assert helloworld_filepath.read_text() == "Hello, World!\n"


def test_docker_start_with_copy_file_to_container_src_does_not_exists(tmp_path: Path) -> None:
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM alpine:latest\n")
    not_exisiting_path = tmp_path / "not_existing"
    assert not_exisiting_path.exists() is False
    with DockerImage(path=tmp_path) as image:
        with pytest.raises(
            docker.errors.APIError, match='invalid mount config for type "bind": bind source path does not exist'
        ):
            with DockerContainer(image=str(image)).with_copy_file_to_container(
                not_exisiting_path,
                "/hello_world.txt",
            ) as container:
                pass


def test_docker_start_with_copy_file_to_container_replace_existing_container_file(tmp_path: Path) -> None:
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text(
        'FROM alpine:latest\nRUN echo \'Hello, World!\' > /hello_world.txt\nCMD ["cat", "/hello_world.txt"]\n'
    )
    helloworld_filepath = tmp_path / "hello_world.txt"
    helloworld_filepath.write_text("Hej Verden!\n")
    with DockerImage(path=tmp_path) as image:
        with DockerContainer(image=str(image)).with_copy_file_to_container(
            helloworld_filepath.absolute(), "/hello_world.txt"
        ) as container:
            stdout, stderr = container.get_logs()
            assert stdout.decode() == "Hej Verden!\n"


def test_docker_start_with_copy_file_to_container_with_volume(tmp_path: Path) -> None:
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text('FROM alpine:latest\nCMD ["cat", "/first/one.txt", "/second/two.txt"]\n')
    first_dirpath = tmp_path / "first"
    first_dirpath.mkdir()
    one_filepath = first_dirpath / "one.txt"
    one_filepath.write_text("1")
    second_dirpath = tmp_path / "second"
    second_dirpath.mkdir()
    two_filepath = second_dirpath / "two.txt"
    two_filepath.write_text("2")
    with DockerImage(path=tmp_path) as image:
        with (
            DockerContainer(image=str(image))
            .with_copy_file_to_container(first_dirpath.absolute(), "/first")
            .with_volume_mapping(
                host=str(second_dirpath),
                container="/second",
            ) as container
        ):
            stdout, stderr = container.get_logs()
            assert stdout.decode() == "12"
