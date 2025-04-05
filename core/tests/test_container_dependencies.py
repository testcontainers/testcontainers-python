import pytest
from docker.errors import APIError, ImageNotFound
from testcontainers.core.container import DockerContainer
from testcontainers.core.exceptions import ContainerStartException


def test_single_dependency_starts() -> None:
    """
    Test that a container with a single dependency starts correctly.
    """
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    dependency_container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container.depends_on(dependency_container)

    container.start()

    assert dependency_container.wait_until_running(), "Dependency did not reach running state"
    assert container.wait_until_running(), "Container did not reach running state"

    container.stop()
    dependency_container.stop()


def test_multiple_dependencies_start() -> None:
    """
    Test that a container with multiple dependencies starts correctly.
    """
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    dependency1 = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    dependency2 = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container.depends_on([dependency1, dependency2])

    container.start()

    assert dependency1.wait_until_running(), "Dependency 1 did not reach running state"
    assert dependency2.wait_until_running(), "Dependency 2 did not reach running state"
    assert container.wait_until_running(), "Container did not reach running state"

    container.stop()
    dependency1.stop()
    dependency2.stop()


def test_dependency_failure() -> None:
    """
    Test that the container fails to start if a dependency fails to start.
    """
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    failing_dependency = DockerContainer("nonexistent-image")
    container.depends_on(failing_dependency)

    with pytest.raises((APIError, ImageNotFound)):
        container.start()

    assert container._container is None, "Container should not start if dependency fails"


def test_all_dependencies_fail() -> None:
    """
    Test that the container fails to start if all dependencies fail.
    """
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
    """
    Test that all started dependencies are stopped if one of them fails.
    """
    container = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    dependency1 = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    failing_dependency = DockerContainer("nonexistent-image3")

    container.depends_on([dependency1, failing_dependency])

    with pytest.raises(Exception):
        container.start()

    assert dependency1._container is None, "dependency1 was not cleaned up properly"
    assert failing_dependency._container is None, "failing_dependency was not cleaned up properly"
    assert container._container is None, "container was not cleaned up properly"


def test_circular_dependency_detection() -> None:
    """
    Test that adding a circular dependency raises a ContainerStartException.
    """
    container_a = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container_b = DockerContainer("alpine:latest").with_command("tail -f /dev/null")

    # Add dependency from A to B
    container_a.depends_on(container_b)

    with pytest.raises(ContainerStartException, match="Circular dependency detected"):
        container_b.depends_on(container_a)


def test_multi_level_circular_dependency_detection() -> None:
    """
    Test that a multi-level circular dependency raises a ContainerStartException.
    """
    container_a = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container_b = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container_c = DockerContainer("alpine:latest").with_command("tail -f /dev/null")

    # Step 1: A depends on B
    container_a.depends_on(container_b)

    # Step 2: B depends on C
    container_b.depends_on(container_c)

    # Step 3: Adding the circular dependency: C depends on A
    with pytest.raises(ContainerStartException, match="Circular dependency detected"):
        container_c.depends_on(container_a)


def test_complex_dependency_graph() -> None:
    container_a = DockerContainer("alpine:latest").with_name("container_a").with_command("tail -f /dev/null")
    container_b = DockerContainer("alpine:latest").with_name("container_b").with_command("tail -f /dev/null")
    container_c = DockerContainer("alpine:latest").with_name("container_c").with_command("tail -f /dev/null")
    container_d = DockerContainer("alpine:latest").with_name("container_d").with_command("tail -f /dev/null")
    container_e = DockerContainer("alpine:latest").with_name("container_e").with_command("tail -f /dev/null")

    # Dependency graph:
    # A -> [B, C]
    # B -> D
    # C -> E
    container_a.depends_on([container_b, container_c])
    container_b.depends_on(container_d)
    container_c.depends_on(container_e)

    try:
        container_a.start()
    except Exception as e:
        raise e

    assert container_a.wait_until_running(), "Container A did not reach running state"
    assert container_b.wait_until_running(), "Container B did not reach running state"
    assert container_c.wait_until_running(), "Container C did not reach running state"
    assert container_d.wait_until_running(), "Container D did not reach running state"
    assert container_e.wait_until_running(), "Container E did not reach running state"

    # Cleanup
    container_a.stop()
    container_b.stop()
    container_c.stop()
    container_d.stop()
    container_e.stop()


def test_dependency_cleanup_on_complex_failure() -> None:
    """
    Test that all dependencies are cleaned up in a complex graph if one fails.
    """
    container_a = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container_b = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    container_c = DockerContainer("alpine:latest").with_command("tail -f /dev/null")
    failing_container = DockerContainer("nonexistent-image")

    # Dependency graph:
    # A -> [B, C]
    # C -> Failing
    container_a.depends_on([container_b, container_c])
    container_c.depends_on(failing_container)

    with pytest.raises(Exception):
        container_a.start()

    assert container_b._container is None, "Container B was not cleaned up properly"
    assert container_c._container is None, "Container C was not cleaned up properly"
    assert failing_container._container is None, "Failing container was not cleaned up properly"
    assert container_a._container is None, "Container A was not cleaned up properly"
