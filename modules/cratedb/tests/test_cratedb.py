import urllib.parse
import os

import sqlalchemy
import pytest

from testcontainers.cratedb import CrateDBContainer


@pytest.mark.parametrize("version", ["5.9", "5.10", "6.0", "latest"])
def test_docker_run_cratedb_versions(version: str):
    with CrateDBContainer(f"crate:{version}") as container:
        engine = sqlalchemy.create_engine(container.get_connection_url())
        with engine.begin() as conn:
            result = conn.execute(sqlalchemy.text("select 1+2+3+4+5"))
            sum_result = result.fetchone()[0]
            assert sum_result == 15


@pytest.mark.parametrize(
    "ports, expected",
    [
        ({5432: None, 4200: None}, False),
        ({5432: 5432, 4200: 4200}, {5432: 5432, 4200: 4200}),
    ],
)
def test_docker_run_cratedb_ports(ports, expected):
    with CrateDBContainer("crate:latest", ports=ports) as container:
        exposed_ports = container.exposed_ports()
        assert len(exposed_ports) == 2
        assert all(map(lambda port: isinstance(port, int), exposed_ports))
        if expected:
            assert exposed_ports == expected


def test_docker_run_cratedb_credentials():
    expected_user, expected_password, expected_port = "user1", "pass1", 4200
    expected_default_dialect, expected_default_host = "crate", "localhost"
    expected_defined_dialect, expected_defined_host = "somedialect", "somehost"
    os.environ["CRATEDB_USER"], os.environ["CRATEDB_PASSWORD"] = expected_user, expected_password

    with CrateDBContainer("crate:latest", ports={4200: expected_port}) as container:
        url = urllib.parse.urlparse(container.get_connection_url())
        user, password = url.netloc.split("@")[0].split(":")
        host, port = url.netloc.split("@")[1].split(":")
        assert user == expected_user
        assert password == expected_password
        assert url.scheme == expected_default_dialect
        assert host == expected_default_host
        assert int(port) == expected_port

        url = urllib.parse.urlparse(
            container.get_connection_url(dialect=expected_defined_dialect, host=expected_defined_host)
        )
        host, _ = url.netloc.split("@")[1].split(":")

        assert url.scheme == expected_defined_dialect
        assert host == expected_defined_host


@pytest.mark.parametrize(
    "opts, expected",
    [
        pytest.param(
            {"indices.breaker.total.limit": "90%"},
            ("-Cdiscovery.type=single-node -Cindices.breaker.total.limit=90%"),
            id="add_cmd_option",
        ),
        pytest.param(
            {"discovery.type": "zen", "indices.breaker.total.limit": "90%"},
            ("-Cdiscovery.type=zen -Cindices.breaker.total.limit=90%"),
            id="override_defaults",
        ),
    ],
)
def test_build_command(opts, expected):
    db = CrateDBContainer(cmd_opts=opts)
    assert db._command == expected
