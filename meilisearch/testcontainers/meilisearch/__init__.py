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

from typing import Optional
import urllib
from urllib.error import URLError

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class MeilisearchContainer(DockerContainer):
    """
    Meilisearch container.

    Example:
# >>> from testcontainers.meilicsearch import MeilisearchContainer
        .. doctest::

            >>> import json
            >>> import urllib.request


            >>> with MeilisearchContainer(f'getmeili/meilisearch:latest') as meilisearch_container:
            ...     with urllib.request.urlopen(meilisearch_container.get_url() + '/health') as response:
            ...         json.loads(response.read().decode())['status']
            'available'
    """

    def __init__(self, image: str = "getmeili/meilisearch:latest", port: int = 7700,
                 master_key: Optional[str] = None, **kwargs) -> None:
        # raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super(MeilisearchContainer, self).__init__(image, **kwargs)
        self.port = port
        self.master_key = master_key
        self.with_exposed_ports(self.port)
        self.with_env('MEILI_MASTER_KEY', master_key)

    @wait_container_is_ready(URLError)
    def _connect(self) -> None:
        res = urllib.request.urlopen(self.get_url())
        if res.status != 200:
            raise Exception()

    def get_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f'http://{host}:{port}'

    def get_master_key(self) -> str:
        return self.master_key

    def start(self) -> "MeilisearchContainer":
        super().start()
        self._connect()
        return self
