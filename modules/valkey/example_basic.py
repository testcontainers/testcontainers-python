from glide import GlideClient, NodeAddress

from testcontainers.valkey import ValkeyContainer


def basic_example():
    with ValkeyContainer() as valkey_container:
        # Get connection parameters
        host = valkey_container.get_host()
        port = valkey_container.get_exposed_port()
        connection_url = valkey_container.get_connection_url()

        print(f"Valkey connection URL: {connection_url}")
        print(f"Host: {host}, Port: {port}")

        # Connect using Glide client
        client = GlideClient([NodeAddress(host, port)])

        # PING command
        pong = client.ping()
        print(f"PING response: {pong}")

        # SET command
        client.set("key", "value")
        print("SET response: OK")

        # GET command
        value = client.get("key")
        print(f"GET response: {value}")

        client.close()


def password_example():
    with ValkeyContainer().with_password("mypassword") as valkey_container:
        host = valkey_container.get_host()
        port = valkey_container.get_exposed_port()
        connection_url = valkey_container.get_connection_url()

        print(f"\nValkey with password connection URL: {connection_url}")

        # Connect using Glide client with password
        client = GlideClient([NodeAddress(host, port)], password="mypassword")

        # PING after auth
        pong = client.ping()
        print(f"PING response: {pong}")

        client.close()


def version_example():
    # Using specific version
    with ValkeyContainer().with_image_tag("8.0") as valkey_container:
        print(f"\nUsing image: {valkey_container.image}")
        connection_url = valkey_container.get_connection_url()
        print(f"Connection URL: {connection_url}")


def bundle_example():
    # Using bundle with all modules (JSON, Bloom, Search, etc.)
    with ValkeyContainer().with_bundle() as valkey_container:
        print(f"\nUsing bundle image: {valkey_container.image}")
        host = valkey_container.get_host()
        port = valkey_container.get_exposed_port()

        # Connect using Glide client
        client = GlideClient([NodeAddress(host, port)])
        pong = client.ping()
        print(f"PING response: {pong}")
        client.close()


if __name__ == "__main__":
    basic_example()
    password_example()
    version_example()
    bundle_example()
