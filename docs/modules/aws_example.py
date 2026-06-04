import json
from datetime import datetime

import boto3

from testcontainers.aws import AwsContainer


def basic_example():
    with AwsContainer() as aws:
        # Get connection parameters
        host = aws.get_container_host_ip()
        port = aws.get_exposed_port(aws.port)
        access_key = aws.access_key
        secret_key = aws.secret_key
        region = aws.region

        # Initialize AWS clients
        s3 = boto3.client(
            "s3",
            endpoint_url=f"http://{host}:{port}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

        dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url=f"http://{host}:{port}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

        sqs = boto3.client(
            "sqs",
            endpoint_url=f"http://{host}:{port}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

        print("Connected to AWS services")

        # Test S3
        bucket_name = f"test-bucket-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        s3.create_bucket(Bucket=bucket_name)
        print(f"\nCreated S3 bucket: {bucket_name}")

        # Upload a file
        s3.put_object(Bucket=bucket_name, Key="test.txt", Body="Hello, S3!")
        print("Uploaded test file")

        # List objects
        objects = s3.list_objects(Bucket=bucket_name)
        print("\nObjects in bucket:")
        for obj in objects.get("Contents", []):
            print(f"- {obj['Key']}")

        # Test DynamoDB
        table_name = "test_table"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        print(f"\nCreated DynamoDB table: {table_name}")

        # Wait for table to be created
        table.meta.client.get_waiter("table_exists").wait(TableName=table_name)

        # Insert items
        table.put_item(Item={"id": "1", "name": "Test Item", "value": 42, "timestamp": datetime.utcnow().isoformat()})
        print("Inserted test item")

        # Query items
        response = table.scan()
        print("\nDynamoDB items:")
        for item in response["Items"]:
            print(json.dumps(item, indent=2))

        # Test SQS
        queue_name = "test-queue"
        queue = sqs.create_queue(QueueName=queue_name)
        queue_url = queue["QueueUrl"]
        print(f"\nCreated SQS queue: {queue_name}")

        # Send message
        response = sqs.send_message(QueueUrl=queue_url, MessageBody="Hello, SQS!")
        print(f"Sent message: {response['MessageId']}")

        # Receive message
        messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        print("\nReceived messages:")
        for message in messages.get("Messages", []):
            print(json.dumps(message, indent=2))

        # Clean up
        # Delete S3 bucket and its contents
        objects = s3.list_objects(Bucket=bucket_name)
        for obj in objects.get("Contents", []):
            s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
        s3.delete_bucket(Bucket=bucket_name)
        print("\nDeleted S3 bucket")

        # Delete DynamoDB table
        table.delete()
        print("Deleted DynamoDB table")

        # Delete SQS queue
        sqs.delete_queue(QueueUrl=queue_url)
        print("Deleted SQS queue")


if __name__ == "__main__":
    basic_example()
