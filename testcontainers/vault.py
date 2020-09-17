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
import urllib

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class VaultContainer(DockerContainer):
    """
    Vault container.

    Example
    -------
    ::

        with VaultContainer().with_vault_token('my token') as vault:
            client = hvac.Client(url=vault.get_url(), token='my token')
    """

    def __init__(self, image='vault:latest', **kwargs):
        super(VaultContainer, self).__init__(image, **kwargs)
        self.port_to_expose = 8200
        self.with_exposed_ports(self.port_to_expose)

    def _configure(self):
        self.with_kwargs(cap_add=['IPC_LOCK'])
        self.with_env('VAULT_ADDR', 'http://0.0.0.0:' + str(self.port_to_expose))

    @wait_container_is_ready()
    def _connect(self):
        res = urllib.request.urlopen(self.get_url() + "/v1/sys/health")
        if res.status != 200:
            raise Exception()

    def start(self):
        self._configure()
        super().start()
        self._connect()
        return self

    def get_url(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port_to_expose)
        return 'http://{}:{}'.format(host, port)

    def with_vault_token(self, token):
        self.with_env('VAULT_DEV_ROOT_TOKEN_ID', token)
        self.with_env('VAULT_TOKEN', token)
        return self
