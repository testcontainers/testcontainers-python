from testcontainers.nats import NatsContainer
from uuid import uuid4
import pytest

from nats import connect as nats_connect
from nats.aio.client import Client as NATSClient


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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_more_complex_example(anyio_backend):
    with NatsContainer() as container:
        nc: NATSClient = await get_client(container)

        sub = await nc.subscribe("greet.*")
        await nc.publish("greet.joe", b"hello")

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


@pytest.mark.asyncio
async def test_doctest_usage():
    """simpler to run test to mirror what is in the doctest"""
    with NatsContainer() as nats_container:
        client = await nats_connect(nats_container.nats_uri())
        sub_tc = await client.subscribe("tc")
        await client.publish("tc", b"Test-Containers")
        next_message = await sub_tc.next_msg(timeout=5.0)
        await client.close()
    assert next_message.data == b"Test-Containers"
