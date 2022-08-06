#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
import urllib
import docker
from docker.models.containers import Container
from testcontainers.core.utils import inside_container
from testcontainers.core.utils import default_gateway_ip


class DockerClient(object):
    def __init__(self, **kwargs):
        self.client = docker.from_env(**kwargs)

    def run(self, image: str,
            command: str = None,
            environment: dict = None,
            ports: dict = None,
            detach: bool = False,
            stdout: bool = True,
            stderr: bool = False,
            remove: bool = False, **kwargs) -> Container:
        return self.client.containers.run(image,
                                          command=command,
                                          stdout=stdout,
                                          stderr=stderr,
                                          remove=remove,
                                          detach=detach,
                                          environment=environment,
                                          ports=ports,
                                          **kwargs)

    def port(self, container_id, port):
        port_mappings = self.client.api.port(container_id, port)
        if not port_mappings:
            raise ConnectionError(f'port mapping for container {container_id} and port {port} is '
                                  'not available')
        return port_mappings[0]["HostPort"]

    def get_container(self, container_id):
        containers = self.client.api.containers(filters={'id': container_id})
        if not containers:
            raise RuntimeError(f'could not get container with id {container_id}')
        return containers[0]

    def bridge_ip(self, container_id):
        container = self.get_container(container_id)
        return container['NetworkSettings']['Networks']['bridge']['IPAddress']

    def gateway_ip(self, container_id):
        container = self.get_container(container_id)
        return container['NetworkSettings']['Networks']['bridge']['Gateway']

    def host(self):
        # https://github.com/testcontainers/testcontainers-go/blob/dd76d1e39c654433a3d80429690d07abcec04424/docker.go#L644
        # if os env TC_HOST is set, use it
        host = os.environ.get('TC_HOST')
        if host:
            return host
        try:
            url = urllib.parse.urlparse(self.client.api.base_url)

        except ValueError:
            return None
        if 'http' in url.scheme or 'tcp' in url.scheme:
            return url.hostname
        if 'unix' in url.scheme or 'npipe' in url.scheme:
            if inside_container():
                ip_address = default_gateway_ip()
                if ip_address:
                    return ip_address
        return "localhost"
