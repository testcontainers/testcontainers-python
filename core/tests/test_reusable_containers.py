from testcontainers.core.container import DockerContainer


def test_docker_container_reuse_default():
    with DockerContainer("hello-world") as container:
        container._reuse == False


def test_docker_container_with_reuse():
    with DockerContainer("hello-world").with_reuse() as container:
        container._reuse == True
