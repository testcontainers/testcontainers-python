import pytest
import time
import socket
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting_utils import wait_for_logs


def test_wait_for_logs_docker_in_docker():
    # real dind
    client = DockerClient()
    dind = client.run(
        image="docker:dind",
        command="dockerd -H tcp://0.0.0.0:2375 --tls=false",
        detach=True,
        privileged=True
    )

    dind.start()

    # get ip address for DOCKER_HOST
    # avoiding DockerContainer class here to prevent code changes affecting the test
    specs = client.get_container(dind.id)
    docker_host_ip = specs['NetworkSettings']['Networks']['bridge']['IPAddress']
    docker_host = f"tcp://{docker_host_ip}:2375"
    # Wait for startup
    timeout = 10
    start_wait = time.perf_counter()
    while True:
        try:
            with socket.create_connection((docker_host_ip, 2375), timeout=timeout):
                break
        except ConnectionRefusedError:
            if time.perf_counter() - start_wait > timeout:
                raise RuntimeError('Docker in docker took longer than 10 seconds to start')
            time.sleep(0.01)

    with DockerContainer(
            image="hello-world",
            docker_client_kw={
                "environment": {
                    "DOCKER_HOST": docker_host,
                    "DOCKER_CERT_PATH": "",
                    "DOCKER_TLS_VERIFY": ""
                }
            }) as container:
        assert container.get_container_host_ip() == docker_host_ip
        wait_for_logs(container, "Hello from Docker!")
        stdout, stderr = container.get_logs()
        assert stdout, 'There should be something on stdout'

    dind.stop()
    dind.remove()

