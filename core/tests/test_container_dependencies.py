import pytest
from docker.errors import APIError, ImageNotFound
from testcontainers.core.container import DockerContainer


def test_single_dependency_starts() -> None:
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    dependency_container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container.depends_on(dependency_container)

    container.start()

    assert dependency_container.wait_until_running(), "Dependency did not reach running state"
    assert container.wait_until_running(), "Container did not reach running state"

    container.stop()
    dependency_container.stop()


def test_multiple_dependencies_start() -> None:
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    dependency1 = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    dependency2 = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container.depends_on([dependency1, dependency2])

    dependency1.start()
    dependency2.start()
    assert dependency1.wait_until_running(), "Dependency 1 did not reach running state"
    assert dependency2.wait_until_running(), "Dependency 2 did not reach running state"

    container.start()
    assert container.wait_until_running(), "Container did not reach running state"

    container.stop()
    dependency1.stop()
    dependency2.stop()


def test_dependency_failure() -> None:
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    failing_dependency = DockerContainer("nonexistent-image")
    container.depends_on(failing_dependency)

    with pytest.raises((APIError, ImageNotFound)):
        container.start()

    assert container._container is None


def test_all_dependencies_fail() -> None:
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    failing_dependency1 = DockerContainer("nonexistent-image1")
    failing_dependency2 = DockerContainer("nonexistent-image2")
    container.depends_on([failing_dependency1, failing_dependency2])

    with pytest.raises((APIError, ImageNotFound)):
        container.start()

    assert container._container is None
    assert failing_dependency1._container is None
    assert failing_dependency2._container is None


def test_dependency_cleanup_on_partial_failure() -> None:
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    dependency1 = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    failing_dependency = DockerContainer("nonexistent-image3")

    container.depends_on([dependency1, failing_dependency])

    with pytest.raises(Exception):
        container.start()

    assert dependency1._container is None, "dependency1 was not cleaned up properly"
    assert failing_dependency._container is None, "failing_dependency was not cleaned up properly"
    assert container._container is None, "container was not cleaned up properly"
