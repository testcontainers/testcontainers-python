from testcontainers.nats import NatsContainer
from uuid import uuid4
import pytest


"""
If you are developing this and you want to test more advanced scenarios using a client
Activate your poetry shell.
pip install nats-py
This will get nats-py into your environment but keep it out of the project


"""


NO_NATS_CLIENT = True
try:
    from nats import connect as nats_connect
    from nats.aio.client import Client as NATSClient

    NO_NATS_CLIENT = False
except ImportError:
    pass


async def get_client(container: NatsContainer) -> "NATSClient":
    """
    Get a nats client.

    Returns:
        client: Nats client to connect to the container.
    """
    conn_string = container.nats_uri()
    client = await nats_connect(conn_string)
    return client


def test_basic_container_ops():
    with NatsContainer() as container:
        # Not sure how to get type information without doing this
        container: NatsContainer = container
        h, p = container.nats_host_and_port()
        assert h == "localhost"
        uri = container.nats_uri()
        management_uri = container.nats_management_uri()

        assert uri != management_uri


pytest.mark.usefixtures("anyio_backend")


@pytest.mark.skipif(NO_NATS_CLIENT, reason="No NATS Client Available")
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_pubsub(anyio_backend):
    with NatsContainer() as container:
        nc: NATSClient = await get_client(container)

        topic = str(uuid4())

        sub = await nc.subscribe(topic)
        sent_message = b"Test-Containers"
        await nc.publish(topic, b"Test-Containers")
        received_msg = await sub.next_msg()
        print("Received:", received_msg)
        assert sent_message == received_msg.data
        await nc.flush()
        await nc.close()


pytest.mark.usefixtures("anyio_backend")


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
@pytest.mark.skipif(NO_NATS_CLIENT, reason="No NATS Client Available")
async def test_more_complex_example(anyio_backend):
    with NatsContainer() as container:
        nc: NATSClient = await get_client(container)

        await nc.publish("greet.joe", b"hello")

        sub = await nc.subscribe("greet.*")

        try:
            await sub.next_msg(timeout=0.1)
        except TimeoutError:
            pass

        await nc.publish("greet.joe", b"hello.joe")
        await nc.publish("greet.pam", b"hello.pam")

        first = await sub.next_msg(timeout=0.1)
        assert b"hello.joe" == first.data

        second = await sub.next_msg(timeout=0.1)
        assert b"hello.pam" == second.data

        await nc.publish("greet.bob", b"hello")

        await sub.unsubscribe()
        await nc.drain()
