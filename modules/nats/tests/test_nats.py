from testcontainers.nats import NatsContainer
import anyio
from nats.aio.client import Client as NATSClient
import uuid

import pytest

pytest.mark.usefixtures("anyio_backend")


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_basic_publishing(anyio_backend):
    with NatsContainer() as container:
        nc: NATSClient = await container.get_client()

        topic = str(uuid.uuid4())

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
async def test_more_complex_example(anyio_backend):
    with NatsContainer() as container:
        nc: NATSClient = await container.get_client()

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
