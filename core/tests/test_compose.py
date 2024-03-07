from pathlib import Path
from re import split
from time import sleep
from typing import Union
from urllib.request import urlopen, Request

import pytest

from testcontainers.compose import DockerCompose, ContainerIsNotRunning, NoSuchPortExposed

FIXTURES = Path(__file__).parent.joinpath("compose_fixtures")


def test_compose_no_file_name():
    basic = DockerCompose(context=FIXTURES / "basic")
    assert basic.compose_file_name is None


def test_compose_str_file_name():
    basic = DockerCompose(context=FIXTURES / "basic", compose_file_name="docker-compose.yaml")
    assert basic.compose_file_name == ["docker-compose.yaml"]


def test_compose_list_file_name():
    basic = DockerCompose(context=FIXTURES / "basic", compose_file_name=["docker-compose.yaml"])
    assert basic.compose_file_name == ["docker-compose.yaml"]


def test_compose_stop():
    basic = DockerCompose(context=FIXTURES / "basic")
    basic.stop()


def test_compose_start_stop():
    basic = DockerCompose(context=FIXTURES / "basic")
    basic.start()
    basic.stop()


def test_compose():
    """stream-of-consciousness e2e test"""
    basic = DockerCompose(context=FIXTURES / "basic")
    try:
        # first it does not exist
        containers = basic.get_containers(include_all=True)
        assert len(containers) == 0

        # then we create it and it exists
        basic.start()
        containers = basic.get_containers(include_all=True)
        assert len(containers) == 1
        containers = basic.get_containers()
        assert len(containers) == 1

        # test that get_container returns the same object, value assertions, etc
        from_all = containers[0]
        assert from_all.State == "running"
        assert from_all.Service == "alpine"

        by_name = basic.get_container("alpine")

        assert by_name.Name == from_all.Name
        assert by_name.Service == from_all.Service
        assert by_name.State == from_all.State
        assert by_name.ID == from_all.ID

        assert by_name.ExitCode == 0

        # what if you want to get logs after it crashes:
        basic.stop(down=False)

        with pytest.raises(ContainerIsNotRunning):
            assert basic.get_container("alpine") is None

        # what it looks like after it exits
        stopped = basic.get_container("alpine", include_all=True)
        assert stopped.State == "exited"
    finally:
        basic.stop()


def test_compose_logs():
    basic = DockerCompose(context=FIXTURES / "basic")
    with basic:
        sleep(1)  # generate some logs every 200ms
        stdout, stderr = basic.get_logs()
        container = basic.get_container()

    assert not stderr
    assert stdout
    lines = split(r"\r?\n", stdout)

    assert len(lines) > 5  # actually 10
    for line in lines[1:]:
        # either the line is blank or the first column (|-separated) contains the service name
        # this is a safe way to split the string
        # docker changes the prefix between versions 24 and 25
        assert not line or container.Service in next(iter(line.split("|")), None)


# noinspection HttpUrlsUsage
def test_compose_ports():
    # fairly straight forward - can we get the right port to request it
    single = DockerCompose(context=FIXTURES / "port_single")
    with single:
        host, port = single.get_service_host_and_port()
        endpoint = f"http://{host}:{port}"
        single.wait_for(endpoint)
        code, response = fetch(Request(method="GET", url=endpoint))
        assert code == 200
        assert "<h1>" in response


# noinspection HttpUrlsUsage
def test_compose_multiple_containers_and_ports():
    """test for the logic encapsulated in 'one' function

    assert correctness of multiple logic
    """
    multiple = DockerCompose(context=FIXTURES / "port_multiple")
    with multiple:
        with pytest.raises(ContainerIsNotRunning) as e:
            multiple.get_container()
            e.match("get_container failed")
            e.match("not exactly 1 container")

        assert multiple.get_container("alpine")
        assert multiple.get_container("alpine2")

        a2p = multiple.get_service_port("alpine2")
        assert a2p > 0  # > 1024

        with pytest.raises(NoSuchPortExposed) as e:
            multiple.get_service_port("alpine")
            e.match("not exactly 1")
        with pytest.raises(NoSuchPortExposed) as e:
            multiple.get_container("alpine").get_publisher(by_host="example.com")
            e.match("not exactly 1")
        with pytest.raises(NoSuchPortExposed) as e:
            multiple.get_container("alpine").get_publisher(by_host="localhost")
            e.match("not exactly 1")

        try:
            # this fails when ipv6 is enabled and docker is forwarding for both 4 + 6
            multiple.get_container(service_name="alpine").get_publisher(by_port=81, prefer_ip_version="IPv6")
        except:  # noqa
            pass

        ports = [
            (
                80,
                multiple.get_service_host(service_name="alpine", port=80),
                multiple.get_service_port(service_name="alpine", port=80),
            ),
            (
                81,
                multiple.get_service_host(service_name="alpine", port=81),
                multiple.get_service_port(service_name="alpine", port=81),
            ),
            (
                82,
                multiple.get_service_host(service_name="alpine", port=82),
                multiple.get_service_port(service_name="alpine", port=82),
            ),
        ]

        # test correctness of port lookup
        for target, host, mapped in ports:
            assert mapped, f"we have a mapped port for target port {target}"
            url = f"http://{host}:{mapped}"
            code, body = fetch(Request(method="GET", url=url))

            expected_code = {
                80: 200,
                81: 202,
                82: 204,
            }.get(code, None)

            if not expected_code:
                continue

            message = f"response '{body}' ({code}) from url {url} should have code {expected_code}"
            assert code == expected_code, message


# noinspection HttpUrlsUsage
def test_exec_in_container():
    """we test that we can manipulate a container via exec"""
    single = DockerCompose(context=FIXTURES / "port_single")
    with single:
        url = f"http://{single.get_service_host()}:{single.get_service_port()}"
        single.wait_for(url)

        # unchanged
        code, body = fetch(url)
        assert code == 200
        assert "test_exec_in_container" not in body

        # change it
        single.exec_in_container(
            command=["sh", "-c", 'echo "test_exec_in_container" > /usr/share/nginx/html/index.html']
        )

        # and it is changed
        code, body = fetch(url)
        assert code == 200
        assert "test_exec_in_container" in body


# noinspection HttpUrlsUsage
def test_exec_in_container_multiple():
    """same as above, except we exec into a particular service"""
    multiple = DockerCompose(context=FIXTURES / "port_multiple")
    with multiple:
        sn = "alpine2"  # service name
        host, port = multiple.get_service_host_and_port(service_name=sn)
        url = f"http://{host}:{port}"
        multiple.wait_for(url)

        # unchanged
        code, body = fetch(url)
        assert code == 200
        assert "test_exec_in_container" not in body

        # change it
        multiple.exec_in_container(
            command=["sh", "-c", 'echo "test_exec_in_container" > /usr/share/nginx/html/index.html'], service_name=sn
        )

        # and it is changed
        code, body = fetch(url)
        assert code == 200
        assert "test_exec_in_container" in body


def fetch(req: Union[Request, str]):
    if isinstance(req, str):
        req = Request(method="GET", url=req)
    with urlopen(req) as res:
        body = res.read().decode("utf-8")
        if 200 < res.getcode() >= 400:
            raise Exception(f"HTTP Error: {res.getcode()} - {res.reason}: {body}")
        return res.getcode(), body
