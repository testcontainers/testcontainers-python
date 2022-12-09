import os
from typing import Optional

import pika
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class RabbitMqContainer(DockerContainer):
    """
    Test container for RabbitMQ. The example below spins up a RabbitMQ broker and uses the
    `pika` client library (https://pypi.org/project/pika/) to establish a connection to the broker.

    Example
    -------
    .. doctest::

        >>> import pika
        >>> from testcontainers.rabbitmq import RabbitMqContainer

        >>> with RabbitMqContainer("rabbitmq:3.9.10") as rabbitmq:
        ...    connection = pika.BlockingConnection(rabbitmq.get_connection_params())
        ...    channel = connection.channel()
    """

    RABBITMQ_NODE_PORT = os.environ.get("RABBITMQ_NODE_PORT", 5672)
    RABBITMQ_DEFAULT_USER = os.environ.get("RABBITMQ_DEFAULT_USER", "guest")
    RABBITMQ_DEFAULT_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS", "guest")

    def __init__(
        self,
        image: str = "rabbitmq:latest",
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize the RabbitMQ test container.

        Args:
            image (str, optional):
                The docker image from docker hub. Defaults to "rabbitmq:latest".
            port (int, optional):
                The port to reach the AMQP API. Defaults to 5672.
            username (str, optional):
                Overwrite the default username which is "guest".
            password (str, optional):
                Overwrite the default username which is "guest".
        """
        super(RabbitMqContainer, self).__init__(image=image, **kwargs)
        self.RABBITMQ_NODE_PORT = port or int(self.RABBITMQ_NODE_PORT)
        self.RABBITMQ_DEFAULT_USER = username or self.RABBITMQ_DEFAULT_USER
        self.RABBITMQ_DEFAULT_PASS = password or self.RABBITMQ_DEFAULT_PASS

        self.with_exposed_ports(self.RABBITMQ_NODE_PORT)
        self.with_env("RABBITMQ_NODE_PORT", self.RABBITMQ_NODE_PORT)
        self.with_env("RABBITMQ_DEFAULT_USER", self.RABBITMQ_DEFAULT_USER)
        self.with_env("RABBITMQ_DEFAULT_PASS", self.RABBITMQ_DEFAULT_PASS)

    @wait_container_is_ready(pika.exceptions.IncompatibleProtocolError)
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
        credentials = pika.PlainCredentials(username=self.RABBITMQ_DEFAULT_USER,
                                            password=self.RABBITMQ_DEFAULT_PASS)

        return pika.ConnectionParameters(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.RABBITMQ_NODE_PORT),
            credentials=credentials,
        )

    def start(self):
        """Start the test container."""
        super().start()
        self.readiness_probe()
        return self
