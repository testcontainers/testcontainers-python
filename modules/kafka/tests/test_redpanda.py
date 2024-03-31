import pytest
from requests import post, get
from json import dumps

from kafka import KafkaConsumer, KafkaProducer, TopicPartition, KafkaAdminClient
from kafka.admin import NewTopic

from testcontainers.kafka import RedpandaContainer


def test_redpanda_producer_consumer():
    with RedpandaContainer() as container:
        produce_and_consume_message(container)


@pytest.mark.parametrize("version", ["v23.1.13", "v23.3.10"])
def test_redpanda_confluent_version(version):
    with RedpandaContainer(image=f"docker.redpanda.com/redpandadata/redpanda:{version}") as container:
        produce_and_consume_message(container)


def test_schema_registry():
    with RedpandaContainer() as container:
        address = container.get_schema_registry_address()
        subject_name = "test-subject-value"
        url = f"{address}/subjects"

        payload = {"schema": dumps({"type": "string"})}
        headers = {"Content-Type": "application/vnd.schemaregistry.v1+json"}
        create_result = post(f"{url}/{subject_name}/versions", data=dumps(payload), headers=headers)
        assert create_result.status_code == 200

        result = get(url)
        assert result.status_code == 200
        assert subject_name in result.json()


def produce_and_consume_message(container):
    topic = "test-topic"
    bootstrap_server = container.get_bootstrap_server()

    admin = KafkaAdminClient(bootstrap_servers=[bootstrap_server])
    admin.create_topics([NewTopic(topic, 1, 1)])

    producer = KafkaProducer(bootstrap_servers=[bootstrap_server])
    future = producer.send(topic, b"verification message")
    future.get(timeout=10)
    producer.close()

    consumer = KafkaConsumer(bootstrap_servers=[bootstrap_server])
    tp = TopicPartition(topic, 0)
    consumer.assign([tp])
    consumer.seek_to_beginning()
    assert consumer.end_offsets([tp])[tp] == 1, "Expected exactly one test message to be present on test topic !"
