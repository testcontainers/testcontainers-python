"""
Valkey container usage examples with valkey-glide sync client.

Requires: pip install valkey-glide-sync
"""

from glide_sync import GlideClient, GlideClientConfiguration, NodeAddress, ServerCredentials

from testcontainers.valkey import ValkeyContainer


def basic_example():
    with ValkeyContainer() as valkey_container:
        host = valkey_container.get_host()
        port = valkey_container.get_exposed_port()
        connection_url = valkey_container.get_connection_url()

        print(f"Valkey connection URL: {connection_url}")
        print(f"Host: {host}, Port: {port}")

        config = GlideClientConfiguration([NodeAddress(host, port)])
        client = GlideClient.create(config)

        pong = client.ping()
        print(f"PING response: {pong}")

        client.set("key", "value")
        print("SET response: OK")

        value = client.get("key")
        print(f"GET response: {value}")

        client.close()


def password_example():
    with ValkeyContainer().with_password("mypassword") as valkey_container:
        host = valkey_container.get_host()
        port = valkey_container.get_exposed_port()
        connection_url = valkey_container.get_connection_url()

        print(f"\nValkey with password connection URL: {connection_url}")

        config = GlideClientConfiguration(
            [NodeAddress(host, port)],
            credentials=ServerCredentials(password="mypassword"),
        )
        client = GlideClient.create(config)

        pong = client.ping()
        print(f"PING response: {pong}")

        client.close()


def version_example():
    with ValkeyContainer().with_image_tag("8.0") as valkey_container:
        print(f"\nUsing image: {valkey_container.image}")
        connection_url = valkey_container.get_connection_url()
        print(f"Connection URL: {connection_url}")


def bundle_example():
    with ValkeyContainer().with_bundle() as valkey_container:
        print(f"\nUsing bundle image: {valkey_container.image}")
        host = valkey_container.get_host()
        port = valkey_container.get_exposed_port()

        config = GlideClientConfiguration([NodeAddress(host, port)])
        client = GlideClient.create(config)

        pong = client.ping()
        print(f"PING response: {pong}")

        client.close()


if __name__ == "__main__":
    basic_example()
    password_example()
    version_example()
    bundle_example()
