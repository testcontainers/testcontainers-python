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


from testcontainers.docker_client import DockerClient


class DockerContainer(object):
    def __init__(self):
        self._docker = DockerClient()
        self._env = {}
        self._exposed_port = None
        self._host = "0.0.0.0"

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def _add_env(self, key, value):
        self._env[key] = value

    def _expose_port(self, port):
        self._exposed_port = port

    def _configure(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        self._docker.remove_all_spawned()


class GenericDockerContainer(DockerContainer):
    def __init__(self, config):
        super(GenericDockerContainer, self).__init__()
        self.container = None
        self.config = config

    def start(self):
        """
        Start container without wait
        :return:
        """
        self.container = self._docker.run(**self.config)
        return self

    @property
    def id(self):
        return self.container["Id"]
