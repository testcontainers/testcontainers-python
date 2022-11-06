import pytest
import pprint

from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting_utils import wait_for_logs, wait_container_is_ready


def test_wait_for_logs_docker_in_docker():
    # real dind isn't possible in CI, forwarding the socket to a container port is at least somewhat the same
    client = DockerClient()
    dind = client.run(
        image="alpine/socat",
        command="tcp-listen:2375,fork,reuseaddr unix-connect:/var/run/docker.sock",
        volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}},
        detach=True,
    )

    dind.start()

    specs = client.get_container(dind.id)
    docker_host_ip = specs['NetworkSettings']['Networks']['bridge']['IPAddress']
    docker_host = f"tcp://{docker_host_ip}:2375"

    with DockerContainer(
            image="hello-world",
            docker_client_kw={
                "environment": {
                    "DOCKER_HOST": docker_host,
                    "DOCKER_TLS_CERTDIR": ""
                }
            }) as container:
        assert container.get_container_host_ip() == docker_host_ip
        wait_for_logs(container, "Hello from Docker!")
        stdout, stderr = container.get_logs()
        assert stdout, 'There should be something on stdout'

    dind.stop()
    dind.remove()
