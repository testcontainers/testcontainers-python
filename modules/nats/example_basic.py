import asyncio
import json

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg

from testcontainers.nats import NatsContainer


async def message_handler(msg: Msg):
    subject = msg.subject
    data = msg.data.decode()
    print(f"Received message on {subject}: {data}")


async def basic_example():
    with NatsContainer() as nats_container:
        # Get connection parameters
        host = nats_container.get_container_host_ip()
        port = nats_container.get_exposed_port(nats_container.port)

        # Create NATS client
        nc = NATS()
        await nc.connect(f"nats://{host}:{port}")
        print("Connected to NATS")

        # Create JetStream context
        js = nc.jetstream()

        # Create stream
        stream = await js.add_stream(name="test-stream", subjects=["test.>"])
        print(f"\nCreated stream: {stream.config.name}")

        # Create consumer
        consumer = await js.add_consumer(stream_name="test-stream", durable_name="test-consumer")
        print(f"Created consumer: {consumer.name}")

        # Subscribe to subjects
        subjects = ["test.1", "test.2", "test.3"]
        for subject in subjects:
            await nc.subscribe(subject, cb=message_handler)
            print(f"Subscribed to {subject}")

        # Publish messages
        messages = {"test.1": "Hello from test.1", "test.2": "Hello from test.2", "test.3": "Hello from test.3"}

        for subject, message in messages.items():
            await nc.publish(subject, message.encode())
            print(f"Published to {subject}")

        # Publish with headers
        headers = {"header1": "value1", "header2": "value2"}
        await nc.publish("test.headers", b"Message with headers", headers=headers)
        print("\nPublished message with headers")

        # Publish with reply
        reply_subject = "test.reply"
        await nc.subscribe(reply_subject, cb=message_handler)
        print(f"Subscribed to {reply_subject}")

        response = await nc.request("test.request", b"Request message", timeout=1)
        print(f"Received reply: {response.data.decode()}")

        # Publish to JetStream
        for subject, message in messages.items():
            ack = await js.publish(subject, message.encode())
            print(f"Published to JetStream {subject}: {ack.stream}")

        # Get stream info
        stream_info = await js.stream_info("test-stream")
        print("\nStream info:")
        print(
            json.dumps(
                {
                    "name": stream_info.config.name,
                    "subjects": stream_info.config.subjects,
                    "messages": stream_info.state.messages,
                    "bytes": stream_info.state.bytes,
                },
                indent=2,
            )
        )

        # Get consumer info
        consumer_info = await js.consumer_info("test-stream", "test-consumer")
        print("\nConsumer info:")
        print(
            json.dumps(
                {
                    "name": consumer_info.name,
                    "stream_name": consumer_info.stream_name,
                    "delivered": consumer_info.delivered.stream_seq,
                    "ack_floor": consumer_info.ack_floor.stream_seq,
                },
                indent=2,
            )
        )

        # Create key-value store
        kv = await js.create_key_value(bucket="test-kv", history=5, ttl=3600)
        print("\nCreated key-value store")

        # Put values
        await kv.put("key1", b"value1")
        await kv.put("key2", b"value2")
        print("Put values in key-value store")

        # Get values
        entry = await kv.get("key1")
        print(f"Got value: {entry.value.decode()}")

        # List keys
        keys = await kv.keys()
        print("\nKeys in store:")
        for key in keys:
            print(f"- {key}")

        # Delete key
        await kv.delete("key1")
        print("Deleted key1")

        # Create object store
        os = await js.create_object_store(bucket="test-os", ttl=3600)
        print("\nCreated object store")

        # Put object
        await os.put("test.txt", b"Hello from object store")
        print("Put object in store")

        # Get object
        obj = await os.get("test.txt")
        print(f"Got object: {obj.data.decode()}")

        # List objects
        objects = await os.list()
        print("\nObjects in store:")
        for obj in objects:
            print(f"- {obj.name}")

        # Delete object
        await os.delete("test.txt")
        print("Deleted object")

        # Clean up
        await js.delete_stream("test-stream")
        print("\nDeleted stream")

        await nc.close()


if __name__ == "__main__":
    asyncio.run(basic_example())
