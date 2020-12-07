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
import os
import pika


class RabbitmqContainer(DockerContainer):
    RABBITMQ_DEFAULT_USER = os.environ.get("RABBITMQ_DEFAULT_USER", "guest")
    RABBITMQ_DEFAULT_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS", "guest")
    SERVICE_STARTED = r"Server startup complete;"

    def __init__(self, image="rabbitmq:latest"):
        super(RabbitmqContainer, self).__init__(image=image)
        self.port_to_expose = 5672
        self.with_exposed_ports(self.port_to_expose)
        self.queues = list()

    def _configure(self):
        self.with_env('RABBITMQ_DEFAULT_USER', 'guest')
        self.with_env('RABBITMQ_DEFAULT_PASS', 'guest')

    @wait_container_is_ready()
    def get_connection_parameters(self):
        credentials = pika.PlainCredentials(self.RABBITMQ_DEFAULT_USER, self.RABBITMQ_DEFAULT_PASS)
        parameters = pika.ConnectionParameters(self.get_container_host_ip(), self.port_to_expose,
                                               '/', credentials)
        return parameters

    @wait_container_is_ready()
    def get_connection(self):
        return self.get_container_host_ip(), self.port_to_expose

    @wait_container_is_ready()
    def declare_queue(self, queue):
        a = list()
        for q in queue:
            a.append(self.declare_queue(q))
        return a

    @wait_container_is_ready()
    def declare_queue(self, queue):
        cmd = "rabbitmqadmin declare queue name={}".format(queue)
        return self.exec(cmd)

    @wait_container_is_ready()
    def declare_binding(self, src, dest):
        cmd = "rabbitmqadmin declare binding source={} destination= {}".format(src, dest)
        self.exec(cmd)

    @wait_container_is_ready()
    def declare_exchange(self, name, type):
        cmd = "rabbitmqadmin declare exchange name={} type={}".format(name, type)
        self.exec(cmd)

    @wait_container_is_ready()
    def declare_vhost(self, vhost):
        cmd = "rabbitmqadmin declare exchange vhost={} type={}".format(vhost)
        self.exec(cmd)

    @wait_container_is_ready()
    def declare_parameter(self, component, name, value):
        cmd = "rabbitmqadmin declare parameter component={} name={} value={}".format(component, name, value)
        self.exec(cmd)

