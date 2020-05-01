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
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
import urllib


class ElasticSearchContainer(DockerContainer):
    """
    ElasticSearch container.

    Example
    -------
    ::

        with ElasticSearchContainer() as es:
            connection_url = es.get_url()
    """
    def __init__(self, image="elasticsearch:7.5.0", port_to_expose=9200):
        super(ElasticSearchContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        self.with_env('transport.host', '127.0.0.1')
        self.with_env('http.host', '0.0.0.0')
        self.with_env('discovery.zen.minimum_master_nodes', '1')

    @wait_container_is_ready()
    def _connect(self):
        res = urllib.request.urlopen(self.get_url())
        if res.status != 200:
            raise Exception()

    def get_url(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port_to_expose)
        return 'http://{}:{}'.format(host, port)

    def start(self):
        super().start()
        self._connect()
        return self


ElasticsearchContainer = ElasticSearchContainer
