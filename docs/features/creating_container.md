# How to create a container

Testcontainers-Python is a thin wrapper around Docker designed for use in tests. Anything you can run in Docker, you can spin up with Testcontainers-Python:

- NoSQL databases or other data stores (e.g. Redis, ElasticSearch, MongoDB)
- Web servers/proxies (e.g. NGINX, Apache)
- Log services (e.g. Logstash, Kibana)
- Other services developed by your team/organization which are already Dockerized

## Run

- Since Testcontainers-Python [v3.10.0]()

You can use the high-level run helper to start a container in one call, similar to Docker’s docker run. Under the hood it builds a temporary network, mounts files or tmpfs, and waits for readiness for you.

```python
import io
import pytest
from docker import DockerClient
from testcontainers.core.container import run
from testcontainers.core.network import DockerNetwork
from testcontainers.core.waiting_utils import wait_for_logs

def test_nginx_run():
    # Create an isolated network
    network = DockerNetwork()
    network.create()
    pytest.addfinalizer(network.remove)

    # File to mount into the container
    test_file_content = b"Hello from file!"
    host_file = io.BytesIO(test_file_content)

    # Run the container with various options
    container = run(
        image="nginx:alpine",
        network=network.name,
        files=[(host_file, "/tmp/file.txt")],
        tmpfs={"/tmp": "rw"},
        labels={"testcontainers.label": "true"},
        environment={"TEST": "true"},
        ports={"80/tcp": None},  # expose port 80
        command=["/bin/sh", "-c", "echo hello world"],
        wait=wait_for_logs("Configuration complete; ready for start"),
        startup_timeout=5,
    )
    # Ensure cleanup
    pytest.addfinalizer(container.stop)
    pytest.addfinalizer(container.remove)

    # Inspect runtime state
    client = DockerClient.from_env()
    info = client.containers.get(container.id).attrs

    # Networks
    aliases = info["NetworkSettings"]["Networks"][network.name]["Aliases"]
    assert "nginx-alias" in aliases

    # Environment
    env = info["Config"]["Env"]
    assert any(e.startswith("TEST=true") for e in env)

    # Tmpfs
    tmpfs = info["HostConfig"]["Tmpfs"].get("/tmp")
    assert tmpfs == ""

    # Labels
    assert info["Config"]["Labels"]["testcontainers.label"] == "true"

    # File copy
    bits, _ = client.api.get_archive(container.id, "/tmp/file.txt")
    archive = io.BytesIO().join(bits)
    # extract and verify...
```
