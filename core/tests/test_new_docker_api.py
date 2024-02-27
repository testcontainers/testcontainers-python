from pathlib import Path

from testcontainers.core.container import DockerContainer


def test_docker_custom_image():
    container = DockerContainer("mysql:5.7.17")
    container.with_exposed_ports(3306)
    container.with_env("MYSQL_ROOT_PASSWORD", "root")

    with container:
        port = container.get_exposed_port(3306)
        assert int(port) > 0


def test_docker_kwargs():
    code_dir = Path(__file__).parent
    container_first = DockerContainer("nginx:latest")
    container_first.with_volume_mapping(code_dir, "/code")

    container_second = DockerContainer("nginx:latest")

    with container_first:
        container_second.with_kwargs(volumes_from=[container_first._container.short_id])
        with container_second:
            files_first = container_first.exec("ls /code").output.decode("utf-8").strip()
            files_second = container_second.exec("ls /code").output.decode("utf-8").strip()
            assert files_first == files_second
