import json

import boto3

from testcontainers.localstack import LocalStackContainer


def basic_example():
    with LocalStackContainer() as localstack:
        # Get endpoint URL
        endpoint_url = localstack.get_endpoint_url()

        # Create S3 client
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
        )

        # Create SQS client
        sqs = boto3.client(
            "sqs",
            endpoint_url=endpoint_url,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
        )

        # Create S3 bucket
        bucket_name = "test-bucket"
        s3.create_bucket(Bucket=bucket_name)
        print(f"Created S3 bucket: {bucket_name}")

        # Upload file to S3
        test_data = {"message": "Hello from LocalStack!", "timestamp": "2024-01-01"}
        s3.put_object(Bucket=bucket_name, Key="test.json", Body=json.dumps(test_data))
        print("Uploaded test.json to S3")

        # Create SQS queue
        queue_name = "test-queue"
        queue = sqs.create_queue(QueueName=queue_name)
        queue_url = queue["QueueUrl"]
        print(f"Created SQS queue: {queue_name}")

        # Send message to SQS
        message = {"message": "Test message", "number": 42}
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
        print("Sent message to SQS")

        # Receive message from SQS
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

        if "Messages" in response:
            received_message = json.loads(response["Messages"][0]["Body"])
            print("\nReceived message from SQS:")
            print(json.dumps(received_message, indent=2))

            # Delete message
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=response["Messages"][0]["ReceiptHandle"])
            print("Deleted message from queue")

        # List S3 objects
        objects = s3.list_objects(Bucket=bucket_name)
        print("\nS3 bucket contents:")
        for obj in objects.get("Contents", []):
            print(f"Key: {obj['Key']}, Size: {obj['Size']} bytes")


if __name__ == "__main__":
    basic_example()
