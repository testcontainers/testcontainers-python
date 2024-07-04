import pytest
from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer, TopicPartition

from testcontainers.core.network import Network
from testcontainers.kafka import KafkaContainer, kafka_config


def test_kafka_producer_consumer():
    with KafkaContainer() as container:
        produce_and_consume_kafka_message(container)


def test_kafka_with_kraft_producer_consumer():
    with KafkaContainer().with_kraft() as container:
        assert container.kraft_enabled
        produce_and_consume_kafka_message(container)


def test_kafka_producer_consumer_custom_port():
    with KafkaContainer(port=9888) as container:
        assert container.port == 9888
        produce_and_consume_kafka_message(container)


def test_kafka_on_networks(monkeypatch: pytest.MonkeyPatch):
    """
    this test case comes from testcontainers/testcontainers-python#637
    """
    monkeypatch.setattr(kafka_config, "limit_broker_to_first_host", True)

    with Network() as network:
        kafka_ctr = KafkaContainer()
        kafka_ctr.with_network(network)
        kafka_ctr.with_network_aliases("kafka")

        with kafka_ctr:
            print("started")  # Will not reach here and timeout
            admin_client = KafkaAdminClient(bootstrap_servers=[kafka_ctr.get_bootstrap_server()])
            print(admin_client.describe_cluster())


def produce_and_consume_kafka_message(container):
    topic = "test-topic"
    bootstrap_server = container.get_bootstrap_server()

    producer = KafkaProducer(bootstrap_servers=[bootstrap_server])
    producer.send(topic, b"verification message")
    producer.flush()
    producer.close()

    consumer = KafkaConsumer(bootstrap_servers=[bootstrap_server])
    tp = TopicPartition(topic, 0)
    consumer.assign([tp])
    consumer.seek_to_beginning()
    assert consumer.end_offsets([tp])[tp] == 1, "Expected exactly one test message to be present on test topic !"
