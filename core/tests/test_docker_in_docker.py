# import contextlib
# import json
# import os
# import time
# import socket
# from pathlib import Path
# from typing import Final, Any, Generator
#
# import pytest
# from docker.models.containers import Container
#
# from testcontainers.core import utils
# from testcontainers.core.config import testcontainers_config as tcc
# from testcontainers.core.labels import SESSION_ID
# from testcontainers.core.network import Network
# from testcontainers.core.container import DockerContainer
# from testcontainers.core.docker_client import DockerClient, LOGGER
# from testcontainers.core.utils import inside_container
# from testcontainers.core.utils import is_mac
# from testcontainers.core.waiting_utils import wait_for_logs
#
#
# def _wait_for_dind_return_ip(client: DockerClient, dind: Container):
#     # get ip address for DOCKER_HOST
#     # avoiding DockerContainer class here to prevent code changes affecting the test
#     docker_host_ip = client.bridge_ip(dind.id)
#     # Wait for startup
#     timeout = 10
#     start_wait = time.perf_counter()
#     while True:
#         try:
#             with socket.create_connection((docker_host_ip, 2375), timeout=timeout):
#                 break
#         except ConnectionRefusedError:
#             if time.perf_counter() - start_wait > timeout:
#                 raise RuntimeError("Docker in docker took longer than 10 seconds to start")
#             time.sleep(0.01)
#     return docker_host_ip
#
#
# @pytest.mark.skipif(is_mac(), reason="Docker socket forwarding (socat) is unsupported on Docker Desktop for macOS")
# def test_wait_for_logs_docker_in_docker():
#     # real dind isn't possible (AFAIK) in CI
#     # forwarding the socket to a container port is at least somewhat the same
#     client = DockerClient()
#     not_really_dind = client.run(
#         image="alpine/socat",
#         command="tcp-listen:2375,fork,reuseaddr unix-connect:/var/run/docker.sock",
#         volumes={"/var/run/docker.sock": {"bind": "/var/run/docker.sock"}},
#         detach=True,
#     )
#
#     not_really_dind.start()
#     docker_host_ip = _wait_for_dind_return_ip(client, not_really_dind)
#     docker_host = f"tcp://{docker_host_ip}:2375"
#
#     with DockerContainer(
#         image="hello-world",
#         docker_client_kw={"environment": {"DOCKER_HOST": docker_host, "DOCKER_CERT_PATH": "", "DOCKER_TLS_VERIFY": ""}},
#     ) as container:
#         assert container.get_container_host_ip() == docker_host_ip
#         wait_for_logs(container, "Hello from Docker!")
#         stdout, stderr = container.get_logs()
#         assert stdout, "There should be something on stdout"
#
#     not_really_dind.stop()
#     not_really_dind.remove()
#
#
# @pytest.mark.skipif(
#     is_mac(), reason="Bridge networking and Docker socket forwarding are not supported on Docker Desktop for macOS"
# )
# def test_dind_inherits_network():
#     client = DockerClient()
#     try:
#         custom_network = client.client.networks.create("custom_network", driver="bridge", check_duplicate=True)
#     except Exception:
#         custom_network = client.client.networks.list(names=["custom_network"])[0]
#     not_really_dind = client.run(
#         image="alpine/socat",
#         command="tcp-listen:2375,fork,reuseaddr unix-connect:/var/run/docker.sock",
#         volumes={"/var/run/docker.sock": {"bind": "/var/run/docker.sock"}},
#         detach=True,
#     )
#
#     not_really_dind.start()
#
#     docker_host_ip = _wait_for_dind_return_ip(client, not_really_dind)
#     docker_host = f"tcp://{docker_host_ip}:2375"
#
#     with DockerContainer(
#         image="hello-world",
#         docker_client_kw={"environment": {"DOCKER_HOST": docker_host, "DOCKER_CERT_PATH": "", "DOCKER_TLS_VERIFY": ""}},
#     ) as container:
#         assert container.get_container_host_ip() == docker_host_ip
#         # Check the gateways are the same, so they can talk to each other
#         assert container.get_docker_client().gateway_ip(container.get_wrapped_container().id) == client.gateway_ip(
#             not_really_dind.id
#         )
#         wait_for_logs(container, "Hello from Docker!")
#         stdout, stderr = container.get_logs()
#         assert stdout, "There should be something on stdout"
#
#     not_really_dind.stop()
#     not_really_dind.remove()
#     custom_network.remove()
#
#
# @contextlib.contextmanager
# def print_surround_header(what: str, header_len: int = 80) -> Generator[None, None, None]:
#     """
#     Helper to visually mark a block with headers
#     """
#     start = f"#   Beginning of {what}"
#     end = f"#   End of {what}"
#
#     print("\n")
#     print("#" * header_len)
#     print(start + " " * (header_len - len(start) - 1) + "#")
#     print("#" * header_len)
#     print("\n")
#
#     yield
#
#     print("\n")
#     print("#" * header_len)
#     print(end + " " * (header_len - len(end) - 1) + "#")
#     print("#" * header_len)
#     print("\n")
#
#
# EXPECTED_NETWORK_VAR: Final[str] = "TCC_EXPECTED_NETWORK"
#
#
# def get_docker_info() -> dict[str, Any]:
#     client = DockerClient().client
#
#     # Get Docker version info
#     version_info = client.version()
#
#     # Get Docker system info
#     system_info = client.info()
#
#     # Get container inspections
#     containers = client.containers.list(all=True)  # List all containers (running or not)
#     container_inspections = {container.name: container.attrs for container in containers}
#
#     # Return as a dictionary
#     return {"version_info": version_info, "system_info": system_info, "container_inspections": container_inspections}
#
#
# # see https://forums.docker.com/t/get-a-containers-full-id-from-inside-of-itself
# @pytest.mark.xfail(reason="Does not work in rootles docker i.e. github actions")
# @pytest.mark.inside_docker_check
# @pytest.mark.skipif(not os.environ.get(EXPECTED_NETWORK_VAR), reason="No expected network given")
# def test_find_host_network_in_dood() -> None:
#     """
#     Check that the correct host network is found for DooD
#     """
#     LOGGER.info(f"Running container id={utils.get_running_in_container_id()}")
#     # Get some debug information in the hope this helps to find
#     LOGGER.info(f"hostname: {socket.gethostname()}")
#     LOGGER.info(f"docker info: {json.dumps(get_docker_info(), indent=2)}")
#     assert DockerClient().find_host_network() == os.environ[EXPECTED_NETWORK_VAR]
#
#
# @pytest.mark.skipif(
#     is_mac(), reason="Docker socket mounting and container networking do not work reliably on Docker Desktop for macOS"
# )
# @pytest.mark.skipif(not Path(tcc.ryuk_docker_socket).exists(), reason="No docker socket available")
# def test_dood(python_testcontainer_image: str) -> None:
#     """
#     Run tests marked as inside_docker_check inside docker out of docker
#     """
#
#     docker_sock = tcc.ryuk_docker_socket
#     with Network() as network:
#         with (
#             DockerContainer(
#                 image=python_testcontainer_image,
#             )
#             .with_command("poetry run pytest -m inside_docker_check")
#             .with_volume_mapping(docker_sock, docker_sock, "rw")
#             # test also that the correct network was found
#             # but only do this if not already inside a container
#             # as there for some reason this doesn't work
#             .with_env(EXPECTED_NETWORK_VAR, "" if inside_container() else network.name)
#             .with_env("RYUK_RECONNECTION_TIMEOUT", "1s")
#             .with_network(network)
#         ) as container:
#             status = container.get_wrapped_container().wait()
#             stdout, stderr = container.get_logs()
#             # ensure ryuk removed the containers created inside container
#             # because they are bound our network the deletion of the network
#             # would fail otherwise
#             time.sleep(1.1)
#
#     # Show what was done inside test
#     with print_surround_header("test_dood results"):
#         print(stdout.decode("utf-8", errors="replace"))
#         print(stderr.decode("utf-8", errors="replace"))
#     assert status["StatusCode"] == 0
#
#
# def test_dind(python_testcontainer_image: str, tmp_path: Path) -> None:
#     """
#     Run selected tests in Docker in Docker
#     """
#     cert_dir = tmp_path / "certs"
#     dind_name = f"docker_{SESSION_ID}"
#     with Network() as network:
#         with (
#             DockerContainer(image="docker:dind", privileged=True)
#             .with_name(dind_name)
#             .with_volume_mapping(str(cert_dir), "/certs", "rw")
#             .with_env("DOCKER_TLS_CERTDIR", "/certs/docker")
#             .with_env("DOCKER_TLS_VERIFY", "1")
#             .with_network(network)
#             .with_network_aliases("docker")
#         ) as dind_container:
#             wait_for_logs(dind_container, "API listen on")
#             client_dir = cert_dir / "docker" / "client"
#             ca_file = client_dir / "ca.pem"
#             assert ca_file.is_file()
#             try:
#                 with (
#                     DockerContainer(image=python_testcontainer_image)
#                     .with_command("poetry run pytest -m inside_docker_check")
#                     .with_volume_mapping(str(cert_dir), "/certs")
#                     # for some reason the docker client does not respect
#                     # DOCKER_TLS_CERTDIR and looks in /root/.docker instead
#                     .with_volume_mapping(str(client_dir), "/root/.docker")
#                     .with_env("DOCKER_TLS_CERTDIR", "/certs/docker/client")
#                     .with_env("DOCKER_TLS_VERIFY", "1")
#                     # docker port is 2376 for https, 2375 for http
#                     .with_env("DOCKER_HOST", "tcp://docker:2376")
#                     .with_network(network)
#                 ) as test_container:
#                     status = test_container.get_wrapped_container().wait()
#                     stdout, stderr = test_container.get_logs()
#             finally:
#                 # ensure the certs are deleted from inside the container
#                 # as they might be owned by root it otherwise could lead to problems
#                 # with pytest cleanup
#                 dind_container.exec("rm -rf /certs/docker")
#                 dind_container.exec("chmod -R a+rwX /certs")
#
#     # Show what was done inside test
#     with print_surround_header("test_dood results"):
#         print(stdout.decode("utf-8", errors="replace"))
#         print(stderr.decode("utf-8", errors="replace"))
#     assert status["StatusCode"] == 0
