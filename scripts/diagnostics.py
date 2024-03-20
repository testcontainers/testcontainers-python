import json

from testcontainers.core import utils
from testcontainers.core.container import DockerContainer

result = {
    "is_linux": utils.is_linux(),
    "is_mac": utils.is_mac(),
    "is_windows": utils.is_windows(),
    "inside_container": utils.inside_container(),
    "default_gateway_ip": utils.default_gateway_ip(),
}

with DockerContainer("alpine:latest") as container:
    client = container.get_docker_client()
    result.update(
        {
            "container_host_ip": container.get_container_host_ip(),
            "docker_client_gateway_ip": client.gateway_ip(container._container.id),
            "docker_client_bridge_ip": client.bridge_ip(container._container.id),
            "docker_client_host": client.host(),
        }
    )

print(json.dumps(result, indent=2))  # noqa: T201
