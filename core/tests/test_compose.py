import subprocess
from pathlib import Path
from re import split
from time import sleep
from typing import Union, Optional
from urllib.request import urlopen, Request

import pytest
from pytest_mock import MockerFixture

from testcontainers.compose import DockerCompose
from testcontainers.core.exceptions import ContainerIsNotRunning, NoSuchPortExposed

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


def test_start_stop_multiple():
    """Start and stop multiple containers individually."""

    # Create two DockerCompose instances from the same file, one service each.
    dc_a = DockerCompose(context=FIXTURES / "basic_multiple", services=["alpine1"])
    dc_b = DockerCompose(context=FIXTURES / "basic_multiple", services=["alpine2"])

    # After starting the first instance, alpine1 should be running
    dc_a.start()
    dc_a.get_container("alpine1")  # Raises if it isn't running
    dc_b.get_container("alpine1")  # Raises if it isn't running

    # Both instances report the same number of containers
    assert len(dc_a.get_containers()) == 1
    assert len(dc_b.get_containers()) == 1

    # Although alpine1 is running, alpine2 has not started yet.
    with pytest.raises(ContainerIsNotRunning):
        dc_a.get_container("alpine2")
    with pytest.raises(ContainerIsNotRunning):
        dc_b.get_container("alpine2")

    # After starting the second instance, alpine2 should also be running
    dc_b.start()
    dc_a.get_container("alpine2")  # No longer raises
    dc_b.get_container("alpine2")  # No longer raises
    assert len(dc_a.get_containers()) == 2
    assert len(dc_b.get_containers()) == 2

    # After stopping the first instance, alpine1 should no longer be running
    dc_a.stop()
    dc_a.get_container("alpine2")
    dc_b.get_container("alpine2")
    assert len(dc_a.get_containers()) == 1
    assert len(dc_b.get_containers()) == 1

    # alpine1 no longer running
    with pytest.raises(ContainerIsNotRunning):
        dc_a.get_container("alpine1")
    with pytest.raises(ContainerIsNotRunning):
        dc_b.get_container("alpine1")

    # Stop the second instance
    dc_b.stop()

    assert len(dc_a.get_containers()) == 0
    assert len(dc_b.get_containers()) == 0


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
        assert not line or container.Service in next(iter(line.split("|")))


def test_compose_volumes():
    _file_in_volume = "/var/lib/example/data/hello"
    volumes = DockerCompose(context=FIXTURES / "basic_volume", keep_volumes=True)
    with volumes:
        stdout, stderr, exitcode = volumes.exec_in_container(
            ["/bin/sh", "-c", f"echo hello > {_file_in_volume}"], "alpine"
        )
    assert exitcode == 0

    # execute another time to confirm the file is still there, but we're not keeping the volumes this time
    volumes.keep_volumes = False
    with volumes:
        stdout, stderr, exitcode = volumes.exec_in_container(["cat", _file_in_volume], "alpine")
    assert exitcode == 0
    assert "hello" in stdout

    # third time we expect the file to be missing
    with volumes, pytest.raises(subprocess.CalledProcessError):
        volumes.exec_in_container(["cat", _file_in_volume], "alpine")


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

        multiple.get_container("alpine")
        multiple.get_container("alpine2")

        a2p = multiple.get_service_port("alpine2")
        assert a2p is not None
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


CONTEXT_FIXTURES = [pytest.param(ctx, id=ctx.name) for ctx in FIXTURES.iterdir()]


@pytest.mark.parametrize("context", CONTEXT_FIXTURES)
def test_compose_config(context: Path, mocker: MockerFixture) -> None:
    compose = DockerCompose(context)
    run_command = mocker.spy(compose, "_run_command")
    expected_cmd = [*compose.compose_command_property, "config", "--format", "json"]

    received_config = compose.get_config()

    assert received_config
    assert isinstance(received_config, dict)
    assert "services" in received_config
    assert run_command.call_args.kwargs["cmd"] == expected_cmd


@pytest.mark.parametrize("context", CONTEXT_FIXTURES)
def test_compose_config_raw(context: Path, mocker: MockerFixture) -> None:
    compose = DockerCompose(context)
    run_command = mocker.spy(compose, "_run_command")
    expected_cmd = [
        *compose.compose_command_property,
        "config",
        "--format",
        "json",
        "--no-path-resolution",
        "--no-normalize",
        "--no-interpolate",
    ]

    received_config = compose.get_config(path_resolution=False, normalize=False, interpolate=False)

    assert received_config
    assert isinstance(received_config, dict)
    assert "services" in received_config
    assert run_command.call_args.kwargs["cmd"] == expected_cmd


def fetch(req: Union[Request, str]):
    if isinstance(req, str):
        req = Request(method="GET", url=req)
    with urlopen(req) as res:
        body = res.read().decode("utf-8")
        if 200 < res.getcode() >= 400:
            raise Exception(f"HTTP Error: {res.getcode()} - {res.reason}: {body}")
        return res.getcode(), body


@pytest.mark.parametrize(
    argnames=["profiles", "running", "not_running"],
    argvalues=[
        pytest.param(None, ["runs-always"], ["runs-profile-a", "runs-profile-b"], id="default"),
        pytest.param(
            ["profile-a"], ["runs-always", "runs-profile-a"], ["runs-profile-b"], id="one-additional-profile-via-str"
        ),
        pytest.param(
            ["profile-a", "profile-b"],
            ["runs-always", "runs-profile-a", "runs-profile-b"],
            [],
            id="all-profiles-explicitly",
        ),
    ],
)
def test_compose_profile_support(profiles: Optional[list[str]], running: list[str], not_running: list[str]):
    with DockerCompose(context=FIXTURES / "profile_support", profiles=profiles) as compose:
        for service in running:
            assert compose.get_container(service) is not None
        for service in not_running:
            with pytest.raises(ContainerIsNotRunning):
                compose.get_container(service)


def test_container_info():
    """Test get_container_info functionality"""
    basic = DockerCompose(context=FIXTURES / "basic")
    with basic:
        container = basic.get_container("alpine")

        info = container.get_container_info()
        assert info is not None
        assert info.Id is not None
        assert info.Name is not None
        assert info.Image is not None

        assert info.State is not None
        assert info.State.Status == "running"
        assert info.State.Running is True
        assert info.State.Pid is not None

        assert info.Config is not None
        assert info.Config.Image is not None
        assert info.Config.Hostname is not None

        network_settings = info.get_network_settings()
        assert network_settings is not None
        assert network_settings.Networks is not None

        info2 = container.get_container_info()
        assert info is info2


def test_container_info_network_details():
    """Test network details in container info"""
    single = DockerCompose(context=FIXTURES / "port_single")
    with single:
        container = single.get_container()
        info = container.get_container_info()
        assert info is not None

        network_settings = info.get_network_settings()
        assert network_settings is not None

        if network_settings.Networks:
            # Test first network
            network_name, network = next(iter(network_settings.Networks.items()))
            assert network.IPAddress is not None
            assert network.Gateway is not None
            assert network.NetworkID is not None


def test_container_info_none_when_no_docker_compose():
    """Test get_container_info returns None when docker_compose reference is missing"""
    from testcontainers.compose.compose import ComposeContainer

    container = ComposeContainer()
    info = container.get_container_info()
    assert info is None
