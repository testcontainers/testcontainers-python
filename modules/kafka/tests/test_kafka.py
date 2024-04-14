from kafka import KafkaConsumer, KafkaProducer, TopicPartition

from testcontainers.kafka import KafkaContainer


def test_kafka_producer_consumer():
    with KafkaContainer() as container:
        produce_and_consume_kafka_message(container)


def test_kafka_producer_consumer_custom_port():
    with KafkaContainer(port=9888) as container:
        assert container.port == 9888
        produce_and_consume_kafka_message(container)


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
