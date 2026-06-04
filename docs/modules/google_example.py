import json
from datetime import datetime

from google.cloud import bigquery, datastore, pubsub, storage

from testcontainers.google import GoogleContainer


def basic_example():
    with GoogleContainer() as google:
        # Get connection parameters
        project_id = google.project_id

        # Initialize clients
        storage_client = storage.Client(project=project_id)
        pubsub_client = pubsub.PublisherClient()
        bigquery_client = bigquery.Client(project=project_id)
        datastore_client = datastore.Client(project=project_id)

        print("Connected to Google Cloud services")

        # Test Cloud Storage
        bucket_name = f"test-bucket-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        bucket = storage_client.create_bucket(bucket_name)
        print(f"\nCreated bucket: {bucket_name}")

        # Upload a file
        blob = bucket.blob("test.txt")
        blob.upload_from_string("Hello, Google Cloud Storage!")
        print("Uploaded test file")

        # List files
        blobs = list(bucket.list_blobs())
        print("\nFiles in bucket:")
        for blob in blobs:
            print(f"- {blob.name}")

        # Test Pub/Sub
        topic_name = f"projects/{project_id}/topics/test-topic"
        pubsub_client.create_topic(name=topic_name)
        print(f"\nCreated topic: {topic_name}")

        # Create subscription
        subscription_name = f"projects/{project_id}/subscriptions/test-subscription"
        pubsub_client.create_subscription(name=subscription_name, topic=topic_name)
        print(f"Created subscription: {subscription_name}")

        # Publish message
        message = "Hello, Pub/Sub!"
        future = pubsub_client.publish(topic_name, message.encode())
        message_id = future.result()
        print(f"Published message: {message_id}")

        # Test BigQuery
        dataset_id = "test_dataset"
        bigquery_client.create_dataset(dataset_id)
        print(f"\nCreated dataset: {dataset_id}")

        # Create table
        table_id = f"{project_id}.{dataset_id}.test_table"
        schema = [
            bigquery.SchemaField("name", "STRING"),
            bigquery.SchemaField("age", "INTEGER"),
            bigquery.SchemaField("city", "STRING"),
        ]
        table = bigquery_client.create_table(bigquery.Table(table_id, schema=schema))
        print(f"Created table: {table_id}")

        # Insert data
        rows_to_insert = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "Los Angeles"},
            {"name": "Bob", "age": 35, "city": "Chicago"},
        ]
        errors = bigquery_client.insert_rows_json(table, rows_to_insert)
        if not errors:
            print("Inserted test data")
        else:
            print(f"Encountered errors: {errors}")

        # Query data
        query = f"SELECT * FROM `{table_id}` WHERE age > 30"
        query_job = bigquery_client.query(query)
        results = query_job.result()
        print("\nQuery results:")
        for row in results:
            print(json.dumps(dict(row), indent=2))

        # Test Datastore
        kind = "test_entity"
        key = datastore_client.key(kind)
        entity = datastore.Entity(key=key)
        entity.update({"name": "Test Entity", "value": 42, "timestamp": datetime.utcnow()})
        datastore_client.put(entity)
        print(f"\nCreated {kind} entity")

        # Query entities
        query = datastore_client.query(kind=kind)
        results = list(query.fetch())
        print("\nDatastore entities:")
        for entity in results:
            print(json.dumps(dict(entity), indent=2))

        # Clean up
        # Delete bucket and its contents
        bucket.delete(force=True)
        print("\nDeleted bucket")

        # Delete topic and subscription
        pubsub_client.delete_subscription(subscription_name)
        pubsub_client.delete_topic(topic_name)
        print("Deleted Pub/Sub topic and subscription")

        # Delete BigQuery dataset and table
        bigquery_client.delete_table(table_id)
        bigquery_client.delete_dataset(dataset_id, delete_contents=True)
        print("Deleted BigQuery dataset and table")

        # Delete Datastore entities
        query = datastore_client.query(kind=kind)
        keys = [entity.key for entity in query.fetch()]
        datastore_client.delete_multi(keys)
        print("Deleted Datastore entities")


if __name__ == "__main__":
    basic_example()
