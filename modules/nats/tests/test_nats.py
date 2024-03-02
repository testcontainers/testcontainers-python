from testcontainers.nats import NatsContainer
import anyio
from nats.aio.client import Client as NATSClient
import uuid

import pytest
pytest.mark.usefixtures("anyio_backend")


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_basic_publishing(anyio_backend):
    with NatsContainer() as container:
        nc: NATSClient =  await container.get_client()
         
        topic= str(uuid.uuid4())
    
        sub = await nc.subscribe(topic)
        sent_message = b'Test-Containers'
        await nc.publish(topic, b'Test-Containers')
        received_msg = await sub.next_msg()
        print("Received:", received_msg)
        assert sent_message == received_msg.data
        await nc.flush()
        await nc.close()