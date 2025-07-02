from datetime import timedelta

import redis

from testcontainers.redis import RedisContainer


def basic_example():
    with RedisContainer() as redis_container:
        # Get connection parameters
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(redis_container.port)

        # Create Redis client
        client = redis.Redis(host=host, port=port, decode_responses=True)
        print("Connected to Redis")

        # String operations
        client.set("greeting", "Hello, Redis!")
        value = client.get("greeting")
        print(f"\nString value: {value}")

        # List operations
        client.lpush("tasks", "task1", "task2", "task3")
        tasks = client.lrange("tasks", 0, -1)
        print("\nTasks list:")
        for task in tasks:
            print(f"- {task}")

        # Set operations
        client.sadd("tags", "python", "redis", "docker", "testing")
        tags = client.smembers("tags")
        print("\nTags set:")
        for tag in tags:
            print(f"- {tag}")

        # Hash operations
        user_data = {"name": "John Doe", "email": "john@example.com", "age": "30"}
        client.hset("user:1", mapping=user_data)
        user = client.hgetall("user:1")
        print("\nUser hash:")
        for field, value in user.items():
            print(f"{field}: {value}")

        # Sorted set operations
        scores = {"player1": 100, "player2": 200, "player3": 150}
        client.zadd("leaderboard", scores)
        leaderboard = client.zrevrange("leaderboard", 0, -1, withscores=True)
        print("\nLeaderboard:")
        for player, score in leaderboard:
            print(f"{player}: {score}")

        # Key expiration
        client.setex("temp_key", timedelta(seconds=10), "This will expire")
        ttl = client.ttl("temp_key")
        print(f"\nTemp key TTL: {ttl} seconds")

        # Pipeline operations
        with client.pipeline() as pipe:
            pipe.set("pipeline_key1", "value1")
            pipe.set("pipeline_key2", "value2")
            pipe.set("pipeline_key3", "value3")
            pipe.execute()
        print("\nPipeline operations completed")

        # Pub/Sub operations
        pubsub = client.pubsub()
        pubsub.subscribe("test_channel")

        # Publish a message
        client.publish("test_channel", "Hello from Redis!")

        # Get the message
        message = pubsub.get_message()
        if message and message["type"] == "message":
            print(f"\nReceived message: {message['data']}")

        # Clean up
        pubsub.unsubscribe()
        pubsub.close()


if __name__ == "__main__":
    basic_example()
