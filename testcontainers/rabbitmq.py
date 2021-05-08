import os

import pika

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class RabbitmqContainer(DockerContainer):

    SERVICE_STARTED = "Server startup complete;"

    RABBITMQ_PORT = 5672
    RABBITMQ_DEFAULT_USER = os.environ.get("RABBITMQ_DEFAULT_USER", "guest")
    RABBITMQ_DEFAULT_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS", "guest")

    def __init__(self, image="rabbitmq:latest", user=None, password=None):
        super(RabbitmqContainer, self).__init__(image=image)
        self.user = user or self.RABBITMQ_DEFAULT_USER
        self.password = password or self.RABBITMQ_DEFAULT_PASS

    def start(self):
        self._configure()
        super().start()
        self._connect()
        return self

    def get_connection(self):
        import pika
        return pika.BlockingConnection(
            parameters=self.get_connection_parameters(),
        )

    def get_connection_parameters(self):
        import pika
        return pika.ConnectionParameters(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.RABBITMQ_PORT),
            credentials=pika.PlainCredentials(
                self.user,
                self.password,
            )
        )

    def _configure(self):
        self.with_env("RABBITMQ_DEFAULT_USER", self.user)
        self.with_env("RABBITMQ_DEFAULT_PASS", self.password)
        self.with_exposed_ports(self.RABBITMQ_PORT)

    @wait_container_is_ready()
    def _connect(self):
        self.get_connection()
