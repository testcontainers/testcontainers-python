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

from testcontainers.core.config import MAX_TRIES
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class K3SContainer(DockerContainer):
    """
    K3S container.

    Example:

        .. doctest::

            >>> import json
            >>> import urllib
            >>> from testcontainers.k3s import K3SContainer

            >>> with K3SContainer() as k3s:
            ...     config_yaml = k3s.config_yaml()
    """

    KUBE_SECURE_PORT = 6443
    RANCHER_WEBHOOK_PORT = 8443

    def __init__(self, image="rancher/k3s:latest", **kwargs) -> None:
        super(K3SContainer, self).__init__(image, **kwargs)
        self.with_exposed_ports(self.KUBE_SECURE_PORT, self.RANCHER_WEBHOOK_PORT)
        self.with_env("K3S_URL",
                      'https://localhost:{}'.format(self.KUBE_SECURE_PORT))
        self.with_command("server --disable traefik --tls-san=" + self.get_container_host_ip())
        self.with_kwargs(privileged=True, tmpfs={"/run": "", "/var/run": ""})
        self.with_volume_mapping("/sys/fs/cgroup", "/sys/fs/cgroup", "rw")

    def _connect(self) -> None:
        wait_for_logs(self, predicate="Node controller sync successful", timeout=MAX_TRIES)

    def start(self) -> "K3SContainer":
        super().start()
        self._connect()
        return self

    def config_yaml(self) -> str:
        output = self.get_wrapped_container().exec_run(['cat', '/etc/rancher/k3s/k3s.yaml'])
        config_yaml = output.output.decode('utf-8') \
            .replace('https://127.0.0.1:{}'.format(self.KUBE_SECURE_PORT), 'https://localhost:{}'
                     .format(self.get_exposed_port(self.KUBE_SECURE_PORT)))
        return config_yaml
