import json
from typing import Optional

import pika
import pytest

from testcontainers.rabbitmq import RabbitMqContainer

QUEUE = "test-q"
EXCHANGE = "test-exchange"
ROUTING_KEY = "test-route-key"
MESSAGE = {"hello": "world"}


@pytest.mark.parametrize(
    argnames=["port", "username", "password", "vhost"],
    argvalues=[
        [None, None, None, None],  # use the defaults
        [5673, None, None, None],  # test with custom port
        [None, "my_test_user", "my_secret_password", None],  # test with custom credentials
        [None, None, None, "vhost"],  # test with custom vhost
    ],
)
def test_docker_run_rabbitmq(
    port: Optional[int], username: Optional[str], password: Optional[str], vhost: Optional[str]
):
    """Run rabbitmq test container and use it to deliver a simple message."""
    kwargs = {}
    if port is not None:
        kwargs["port"] = port
    if username is not None:
        kwargs["username"] = username
    if password is not None:
        kwargs["password"] = password
    if vhost is not None:
        kwargs["vhost"] = vhost

    rabbitmq_container = RabbitMqContainer("rabbitmq:latest", **kwargs)
    with rabbitmq_container as rabbitmq:
        # connect to rabbitmq:
        connection_params = rabbitmq.get_connection_params()
        connection = pika.BlockingConnection(connection_params)

        # create exchange and queue:
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
        channel.queue_declare(QUEUE, arguments={})
        channel.queue_bind(QUEUE, EXCHANGE, ROUTING_KEY)

        # publish message:
        encoded_message = json.dumps(MESSAGE)
        channel.basic_publish(EXCHANGE, ROUTING_KEY, body=encoded_message)

        _, _, body = channel.basic_get(queue=QUEUE)
        received_message = json.loads(body.decode())
        assert received_message == MESSAGE
