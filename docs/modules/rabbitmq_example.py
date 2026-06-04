import json
import time
from threading import Thread

import pika

from testcontainers.rabbitmq import RabbitMQContainer


def basic_example():
    with RabbitMQContainer() as rabbitmq:
        # Get connection parameters
        host = rabbitmq.get_container_host_ip()
        port = rabbitmq.get_exposed_port(rabbitmq.port)
        username = rabbitmq.username
        password = rabbitmq.password

        # Create connection
        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(host=host, port=port, credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        print("Connected to RabbitMQ")

        # Declare exchange
        exchange_name = "test_exchange"
        channel.exchange_declare(exchange=exchange_name, exchange_type="direct", durable=True)
        print(f"Declared exchange: {exchange_name}")

        # Declare queues
        queues = {"queue1": "routing_key1", "queue2": "routing_key2"}

        for queue_name, routing_key in queues.items():
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
            print(f"Declared and bound queue: {queue_name}")

        # Define message handler
        def message_handler(ch, method, properties, body):
            message = json.loads(body)
            print(f"\nReceived message on {method.routing_key}:")
            print(json.dumps(message, indent=2))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        # Start consuming in a separate thread
        def consume_messages():
            channel.basic_qos(prefetch_count=1)
            for queue_name in queues:
                channel.basic_consume(queue=queue_name, on_message_callback=message_handler)
            channel.start_consuming()

        consumer_thread = Thread(target=consume_messages)
        consumer_thread.daemon = True
        consumer_thread.start()

        # Publish messages
        test_messages = [
            {
                "queue": "queue1",
                "routing_key": "routing_key1",
                "message": {"id": 1, "content": "Message for queue 1", "timestamp": time.time()},
            },
            {
                "queue": "queue2",
                "routing_key": "routing_key2",
                "message": {"id": 2, "content": "Message for queue 2", "timestamp": time.time()},
            },
        ]

        for msg in test_messages:
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=msg["routing_key"],
                body=json.dumps(msg["message"]),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type="application/json",
                ),
            )
            print(f"Published message to {msg['queue']}")

        # Wait for messages to be processed
        time.sleep(2)

        # Get queue information
        print("\nQueue information:")
        for queue_name in queues:
            queue = channel.queue_declare(queue=queue_name, passive=True)
            print(f"{queue_name}:")
            print(f"  Messages: {queue.method.message_count}")
            print(f"  Consumers: {queue.method.consumer_count}")

        # Clean up
        connection.close()


if __name__ == "__main__":
    basic_example()
