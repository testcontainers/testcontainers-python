import os
from typing import Optional

import pika

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class RabbitMqContainer(DockerContainer):
    """
    Test container for RabbitMQ. The example below spins up a RabbitMQ broker and uses the
    `pika client library <(https://pypi.org/project/pika/)>`__ to establish a connection to the
    broker.

    Example:

        .. doctest::

            >>> import pika
            >>> from testcontainers.rabbitmq import RabbitMqContainer

            >>> with RabbitMqContainer("rabbitmq:3.9.10") as rabbitmq:
            ...    connection = pika.BlockingConnection(rabbitmq.get_connection_params())
            ...    channel = connection.channel()
    """

    def __init__(
        self,
        image: str = "rabbitmq:latest",
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        vhost: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize the RabbitMQ test container.

        Args:
            image: Docker image from docker hub. Defaults to "rabbitmq:latest".
            port: Port to reach the AMQP API. Defaults to 5672.
            username: RabbitMQ username.
            password: RabbitMQ password.
        """
        super().__init__(image=image, **kwargs)
        self.port = port or int(os.environ.get("RABBITMQ_NODE_PORT", 5672))
        self.username = username or os.environ.get("RABBITMQ_DEFAULT_USER", "guest")
        self.password = password or os.environ.get("RABBITMQ_DEFAULT_PASS", "guest")
        self.vhost = vhost or os.environ.get("RABBITMQ_DEFAULT_VHOST", "/")

        self.with_exposed_ports(self.port)
        self.with_env("RABBITMQ_NODE_PORT", self.port)
        self.with_env("RABBITMQ_DEFAULT_USER", self.username)
        self.with_env("RABBITMQ_DEFAULT_PASS", self.password)
        self.with_env("RABBITMQ_DEFAULT_VHOST", self.vhost)

    @wait_container_is_ready(pika.exceptions.IncompatibleProtocolError, pika.exceptions.AMQPConnectionError)
    def readiness_probe(self) -> bool:
        """Test if the RabbitMQ broker is ready."""
        connection = pika.BlockingConnection(self.get_connection_params())
        if connection.is_open:
            connection.close()
            return self
        raise RuntimeError("Could not open connection to RabbitMQ broker.")

    def get_connection_params(self) -> pika.ConnectionParameters:
        """
        Get connection params as a pika.ConnectionParameters object.
        For more details see:
        https://pika.readthedocs.io/en/latest/modules/parameters.html
        """
        credentials = pika.PlainCredentials(username=self.username, password=self.password)

        return pika.ConnectionParameters(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.port),
            virtual_host=self.vhost,
            credentials=credentials,
        )

    def start(self) -> "RabbitMqContainer":
        """Start the test container."""
        super().start()
        self.readiness_probe()
        return self
