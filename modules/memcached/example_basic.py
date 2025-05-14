import json
import pickle

import memcache

from testcontainers.memcached import MemcachedContainer


def basic_example():
    with MemcachedContainer() as memcached:
        # Get connection parameters
        host = memcached.get_container_host_ip()
        port = memcached.get_exposed_port(memcached.port)

        # Create Memcached client
        client = memcache.Client([f"{host}:{port}"])
        print("Connected to Memcached")

        # Store simple values
        client.set("string_key", "Hello from Memcached")
        client.set("int_key", 42)
        client.set("float_key", 3.14)
        print("Stored simple values")

        # Store complex data
        complex_data = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
        client.set("complex_key", json.dumps(complex_data))
        print("Stored complex data")

        # Store with expiration
        client.set("expiring_key", "This will expire", time=5)
        print("Stored value with expiration")

        # Store with pickle
        class TestObject:
            def __init__(self, name, value):
                self.name = name
                self.value = value

        test_obj = TestObject("test", 123)
        client.set("object_key", pickle.dumps(test_obj))
        print("Stored pickled object")

        # Retrieve values
        print("\nRetrieved values:")
        print(f"string_key: {client.get('string_key')}")
        print(f"int_key: {client.get('int_key')}")
        print(f"float_key: {client.get('float_key')}")

        # Retrieve complex data
        complex_value = json.loads(client.get("complex_key"))
        print("\nComplex data:")
        print(json.dumps(complex_value, indent=2))

        # Retrieve pickled object
        obj_data = pickle.loads(client.get("object_key"))
        print("\nPickled object:")
        print(f"name: {obj_data.name}")
        print(f"value: {obj_data.value}")

        # Check expiration
        print("\nChecking expiring key:")
        print(f"expiring_key: {client.get('expiring_key')}")
        print("Waiting for key to expire...")
        import time

        time.sleep(6)
        print(f"expiring_key after expiration: {client.get('expiring_key')}")

        # Store multiple values
        multi_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
        client.set_multi(multi_data)
        print("\nStored multiple values")

        # Retrieve multiple values
        multi_keys = ["key1", "key2", "key3"]
        multi_values = client.get_multi(multi_keys)
        print("\nMultiple values:")
        print(json.dumps(multi_values, indent=2))

        # Increment and decrement
        client.set("counter", 0)
        client.incr("counter")
        client.incr("counter", 2)
        print("\nCounter after increment:")
        print(f"counter: {client.get('counter')}")

        client.decr("counter")
        print("Counter after decrement:")
        print(f"counter: {client.get('counter')}")

        # Store with flags
        client.set("flagged_key", "value", flags=1)
        print("\nStored value with flags")

        # Get stats
        stats = client.get_stats()
        print("\nMemcached stats:")
        for server, server_stats in stats:
            print(f"\nServer: {server}")
            print(json.dumps(dict(server_stats), indent=2))

        # Delete values
        client.delete("string_key")
        client.delete_multi(["key1", "key2", "key3"])
        print("\nDeleted values")

        # Check deleted values
        print("\nChecking deleted values:")
        print(f"string_key: {client.get('string_key')}")
        print(f"key1: {client.get('key1')}")

        # Store with CAS
        client.set("cas_key", "initial")
        cas_value = client.gets("cas_key")
        print("\nCAS value:")
        print(f"value: {cas_value}")

        # Update with CAS
        success = client.cas("cas_key", "updated", cas_value[1])
        print(f"CAS update success: {success}")
        print(f"Updated value: {client.get('cas_key')}")

        # Try to update with invalid CAS
        success = client.cas("cas_key", "failed", 0)
        print(f"Invalid CAS update success: {success}")
        print(f"Value after failed update: {client.get('cas_key')}")

        # Clean up
        client.flush_all()
        print("\nFlushed all values")


if __name__ == "__main__":
    basic_example()
