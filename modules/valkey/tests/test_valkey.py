import socket

from testcontainers.valkey import ValkeyContainer


def test_docker_run_valkey():
    with ValkeyContainer() as valkey:
        host = valkey.get_host()
        port = valkey.get_exposed_port()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(b"*1\r\n$4\r\nPING\r\n")
            response = s.recv(1024)
            assert b"+PONG" in response


def test_docker_run_valkey_with_password():
    with ValkeyContainer().with_password("mypass") as valkey:
        host = valkey.get_host()
        port = valkey.get_exposed_port()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            # Authenticate
            s.sendall(b"*2\r\n$4\r\nAUTH\r\n$6\r\nmypass\r\n")
            auth_response = s.recv(1024)
            assert b"+OK" in auth_response

            # Test SET command
            s.sendall(b"*3\r\n$3\r\nSET\r\n$5\r\nhello\r\n$5\r\nworld\r\n")
            set_response = s.recv(1024)
            assert b"+OK" in set_response

            # Test GET command
            s.sendall(b"*2\r\n$3\r\nGET\r\n$5\r\nhello\r\n")
            get_response = s.recv(1024)
            assert b"world" in get_response


def test_get_connection_url():
    with ValkeyContainer() as valkey:
        url = valkey.get_connection_url()
        assert url.startswith("valkey://")
        assert str(valkey.get_exposed_port()) in url


def test_get_connection_url_with_password():
    with ValkeyContainer().with_password("secret") as valkey:
        url = valkey.get_connection_url()
        assert url.startswith("valkey://:secret@")
        assert str(valkey.get_exposed_port()) in url


def test_with_image_tag():
    container = ValkeyContainer().with_image_tag("8.0")
    assert "valkey/valkey:8.0" in container.image


def test_with_bundle():
    container = ValkeyContainer().with_bundle()
    assert container.image == "valkey/valkey-bundle:latest"


def test_with_bundle_and_tag():
    container = ValkeyContainer().with_bundle().with_image_tag("9.0")
    assert container.image == "valkey/valkey-bundle:9.0"


def test_bundle_starts():
    with ValkeyContainer().with_bundle() as valkey:
        host = valkey.get_host()
        port = valkey.get_exposed_port()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(b"*1\r\n$4\r\nPING\r\n")
            response = s.recv(1024)
            assert b"+PONG" in response
