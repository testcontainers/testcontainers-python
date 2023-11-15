from testcontainers.google import PubSubContainer
from testcontainers.core.waiting_utils import wait_for_logs
from queue import Queue


def test_pubsub_container():
    pubsub: PubSubContainer
    with PubSubContainer() as pubsub:
        wait_for_logs(pubsub, r"Server started, listening on \d+", timeout=60)
        # Create a new topic
        publisher = pubsub.get_publisher_client()
        topic_path = publisher.topic_path(pubsub.project, "my-topic")
        publisher.create_topic(name=topic_path)

        # Create a subscription
        subscriber = pubsub.get_subscriber_client()
        subscription_path = subscriber.subscription_path(pubsub.project,
                                                         "my-subscription")
        subscriber.create_subscription(name=subscription_path, topic=topic_path)

        # Publish a message
        publisher.publish(topic_path, b"Hello world!")

        # Receive the message
        queue = Queue()
        subscriber.subscribe(subscription_path, queue.put)
        message = queue.get(timeout=1)
        assert message.data == b"Hello world!"
        message.ack()
