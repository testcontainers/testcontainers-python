from testcontainers.core.container import DockerContainer


def test_docker():
    container = DockerContainer("spirogov/video_service", "latest").expose_port(8086, 8086)
