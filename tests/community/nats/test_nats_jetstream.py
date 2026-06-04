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


@pytest.mark.asyncio
async def test_jetstream_add_stream(anyio_backend):
    with NatsContainer(jetstream=True) as container:
        nc: NATSClient = await get_client(container)

        topic = str(uuid4())

        js = nc.jetstream()

        await js.add_stream(name="test-stream", subjects=[topic])

        await nc.close()
