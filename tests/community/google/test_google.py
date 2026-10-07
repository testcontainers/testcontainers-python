from queue import Queue

from google.cloud.datastore import Entity

from testcontainers.community.google import BigQueryContainer, DatastoreContainer, PubSubContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_bigquery_container_query():
    with BigQueryContainer() as bigquery:
        client = bigquery.get_client()
        job = client.query("SELECT 1 AS one")
        rows = list(job.result())
        assert [dict(row) for row in rows] == [{"one": 1}]


def test_bigquery_container_ddl_dml_roundtrip():
    with BigQueryContainer() as bigquery:
        client = bigquery.get_client()
        client.create_dataset(f"{bigquery.project}.ds")
        client.query("CREATE TABLE ds.people (name STRING, age INT64)").result()
        client.query("INSERT INTO ds.people (name, age) VALUES ('Ada', 36), ('Grace', 85)").result()

        job = client.query("SELECT name FROM ds.people WHERE age > 50 ORDER BY name")
        rows = [dict(row) for row in job.result()]
        assert rows == [{"name": "Grace"}]


def test_bigquery_container_isolation():
    with BigQueryContainer() as bigquery, BigQueryContainer() as bigquery2:
        assert bigquery.get_rest_endpoint() != bigquery2.get_rest_endpoint(), "BigQuery containers use the same port."
        client = bigquery.get_client()
        client.create_dataset(f"{bigquery.project}.ds")

        # A positive check (dataset lists differ) rather than expecting a query
        # against the missing dataset to fail: the emulator reports a
        # not-found error as a generic retryable INTERNAL, so the client
        # library's default retry policy spends a minute retrying it instead
        # of failing fast.
        client2 = bigquery2.get_client()
        assert [d.dataset_id for d in client.list_datasets()] == ["ds"]
        assert [d.dataset_id for d in client2.list_datasets()] == []


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
        subscription_path = subscriber.subscription_path(pubsub.project, "my-subscription")
        subscriber.create_subscription(name=subscription_path, topic=topic_path)

        # Publish a message
        publisher.publish(topic_path, b"Hello world!")

        # Receive the message
        queue = Queue()
        subscriber.subscribe(subscription_path, queue.put)
        message = queue.get(timeout=1)
        assert message.data == b"Hello world!"
        message.ack()


def test_datastore_container_creation():
    # Initialize the Datastore emulator container
    with DatastoreContainer() as datastore:
        # Obtain a datastore client configured to connect to the emulator
        client = datastore.get_datastore_client()

        # Define a unique key for a test entity to ensure test isolation
        key = client.key("TestKind", "test_id_1")

        # Create and insert a new entity
        entity = Entity(key=key)
        entity.update({"foo": "bar"})
        client.put(entity)

        # Fetch the just-inserted entity directly
        fetched_entity = client.get(key)

        # Assert that the fetched entity matches what was inserted
        assert fetched_entity is not None, "Entity was not found in the datastore."
        assert fetched_entity["foo"] == "bar", "Entity attribute 'foo' did not match expected value 'bar'."


def test_datastore_container_isolation():
    # Initialize the Datastore emulator container
    with DatastoreContainer() as datastore:
        # Obtain a datastore client configured to connect to the emulator
        client = datastore.get_datastore_client()

        # Define a unique key for a test entity to ensure test isolation
        key = client.key("TestKind", "test_id_1")

        # Create and insert a new entity
        entity = Entity(key=key)
        entity.update({"foo": "bar"})
        client.put(entity)

        # Create a second container and try to fetch the entity to makesure its a different container
        with DatastoreContainer() as datastore2:
            assert datastore.get_datastore_emulator_host() != datastore2.get_datastore_emulator_host(), (
                "Datastore containers use the same port."
            )
            client2 = datastore2.get_datastore_client()
            fetched_entity2 = client2.get(key)
            assert fetched_entity2 is None, "Entity was found in the datastore."
