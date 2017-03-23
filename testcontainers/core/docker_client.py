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
import docker
from docker.models.containers import Container


class DockerClient(object):
    def __init__(self):
        self.client = docker.from_env()

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
        return self.client.api.port(container_id, port)[0]["HostPort"]
