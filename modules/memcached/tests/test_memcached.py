import socket

from testcontainers.memcached import MemcachedContainer

import pytest


def test_memcached_host_and_exposed_port():
    with MemcachedContainer("memcached:1.6-alpine") as memcached:
        host, port = memcached.get_host_and_port()
        assert host == "localhost"
        assert port != 11211


@pytest.mark.parametrize("image", ["memcached:1.6-bookworm", "memcached:1.6-alpine"])
def test_memcached_can_connect_and_retrieve_data(image):
    with MemcachedContainer(image) as memcached:
        host, port = memcached.get_host_and_port()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(b"stats\n\r")
            data = s.recv(1024)
            assert len(data) > 0, "We should have received some data from memcached"

        pid_stat, uptime_stat, *_ = data.decode().split("\r\n")

        assert pid_stat.startswith("STAT pid")
        assert uptime_stat.startswith("STAT uptime")
