import time
import socket
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting_utils import wait_for_logs


def _wait_for_dind_return_ip(client, dind):
    # get ip address for DOCKER_HOST
    # avoiding DockerContainer class here to prevent code changes affecting the test
    docker_host_ip = client.bridge_ip(dind.id)
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
    return docker_host_ip

def test_wait_for_logs_docker_in_docker():
    # real dind isn't possible (AFAIK) in CI
    # forwarding the socket to a container port is at least somewhat the same
    client = DockerClient()
    not_really_dind = client.run(
        image="alpine/socat",
        command="tcp-listen:2375,fork,reuseaddr unix-connect:/var/run/docker.sock",
        volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}},
        detach=True,
    )

    not_really_dind.start()
    docker_host_ip = _wait_for_dind_return_ip(client, not_really_dind)
    docker_host = f"tcp://{docker_host_ip}:2375"

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

    not_really_dind.stop()
    not_really_dind.remove()

def test_dind_inherits_network():
    client = DockerClient()
    try:
        custom_network = client.client.networks.create("custom_network", driver="bridge", check_duplicate=True)
    except:
        custom_network = client.client.networks.list(names=["custom_network"])[0]
    not_really_dind = client.run(
        image="alpine/socat",
        command="tcp-listen:2375,fork,reuseaddr unix-connect:/var/run/docker.sock",
        volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}},
        detach=True,
    )

    not_really_dind.start()

    docker_host_ip = _wait_for_dind_return_ip(client, not_really_dind)
    docker_host = f"tcp://{docker_host_ip}:2375"

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
        # Check the gateways are the same, so they can talk to each other
        assert container.get_docker_client().gateway_ip(container.get_wrapped_container().id) == client.gateway_ip(not_really_dind.id)
        wait_for_logs(container, "Hello from Docker!")
        stdout, stderr = container.get_logs()
        assert stdout, 'There should be something on stdout'

    not_really_dind.stop()
    not_really_dind.remove()
    custom_network.remove()

