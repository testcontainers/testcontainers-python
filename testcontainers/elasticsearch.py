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


class ElasticsearchContainer(DockerContainer):
    def __init__(self, image="elasticsearch:latest", port_to_expose=9200):
        super(ElasticsearchContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        cmd_dict = {
            'transport.host': '127.0.0.1',
            'http.host': '0.0.0.0',
            'discovery.zen.minimum_master_nodes': '1'
        }
        command = ' '.join(['-E{0}={1}'.format(k, v) for k, v in cmd_dict.items()])
        self.with_command(command)

    @wait_container_is_ready()
    def _connect(self):
        port = self.get_exposed_port(self.port_to_expose)
        res = urllib.request.urlopen('http://127.0.0.1:{}'.format(port))
        if res.status != 200:
            raise Exception()

    def start(self):
        super().start()
        self._connect()
        return self
