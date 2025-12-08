import socket

from testcontainers.valkey import ValkeyContainer


def basic_example():
    with ValkeyContainer() as valkey_container:
        # Get connection parameters
        host = valkey_container.get_host()
        port = valkey_container.get_exposed_port()
        connection_url = valkey_container.get_connection_url()

        print(f"Valkey connection URL: {connection_url}")
        print(f"Host: {host}, Port: {port}")

        # Connect using raw socket and RESP protocol
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            # PING command
            s.sendall(b"*1\r\n$4\r\nPING\r\n")
            response = s.recv(1024)
            print(f"PING response: {response.decode()}")

            # SET command
            s.sendall(b"*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n")
            response = s.recv(1024)
            print(f"SET response: {response.decode()}")

            # GET command
            s.sendall(b"*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n")
            response = s.recv(1024)
            print(f"GET response: {response.decode()}")


def password_example():
    with ValkeyContainer().with_password("mypassword") as valkey_container:
        host = valkey_container.get_host()
        port = valkey_container.get_exposed_port()
        connection_url = valkey_container.get_connection_url()

        print(f"\nValkey with password connection URL: {connection_url}")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            # AUTH command
            s.sendall(b"*2\r\n$4\r\nAUTH\r\n$10\r\nmypassword\r\n")
            response = s.recv(1024)
            print(f"AUTH response: {response.decode()}")

            # PING after auth
            s.sendall(b"*1\r\n$4\r\nPING\r\n")
            response = s.recv(1024)
            print(f"PING response: {response.decode()}")


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

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(b"*1\r\n$4\r\nPING\r\n")
            response = s.recv(1024)
            print(f"PING response: {response.decode()}")


if __name__ == "__main__":
    basic_example()
    password_example()
    version_example()
    bundle_example()
