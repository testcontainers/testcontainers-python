import json
import time
from datetime import datetime
from threading import Thread

from kafka import KafkaConsumer, KafkaProducer

from testcontainers.kafka import KafkaContainer


def basic_example():
    with KafkaContainer() as kafka:
        # Get connection parameters
        bootstrap_servers = kafka.get_bootstrap_server()

        # Create Kafka producer
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers, value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("Created Kafka producer")

        # Create Kafka consumer
        consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            group_id="test_group",
        )
        print("Created Kafka consumer")

        # Define topics
        topics = ["test_topic1", "test_topic2"]

        # Subscribe to topics
        consumer.subscribe(topics)
        print(f"Subscribed to topics: {topics}")

        # Start consuming in a separate thread
        def consume_messages():
            for message in consumer:
                print(f"\nReceived message from {message.topic}:")
                print(json.dumps(message.value, indent=2))

        consumer_thread = Thread(target=consume_messages)
        consumer_thread.daemon = True
        consumer_thread.start()

        # Produce test messages
        test_messages = [
            {
                "topic": "test_topic1",
                "message": {"id": 1, "content": "Message for topic 1", "timestamp": datetime.utcnow().isoformat()},
            },
            {
                "topic": "test_topic2",
                "message": {"id": 2, "content": "Message for topic 2", "timestamp": datetime.utcnow().isoformat()},
            },
        ]

        for msg in test_messages:
            producer.send(msg["topic"], msg["message"])
            print(f"Sent message to {msg['topic']}")

        # Wait for messages to be processed
        time.sleep(2)

        # Get topic information
        print("\nTopic information:")
        for topic in topics:
            partitions = consumer.partitions_for_topic(topic)
            print(f"{topic}:")
            print(f"  Partitions: {partitions}")

        # Clean up
        producer.close()
        consumer.close()


if __name__ == "__main__":
    basic_example()
