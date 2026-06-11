import urllib.parse

import pytest
import sqlalchemy

from testcontainers.community.cratedb import CrateDBContainer


@pytest.mark.parametrize("version", ["5.10", "latest"])
def test_docker_run_cratedb(version: str):
    with CrateDBContainer(f"crate:{version}") as cratedb:
        engine = sqlalchemy.create_engine(cratedb.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select 1 + 2 + 3 + 4 + 5"))
            assert result.fetchone()[0] == 15


def test_cratedb_connection_url():
    with CrateDBContainer("crate:latest", username="crate", password="crate") as cratedb:
        url = urllib.parse.urlparse(cratedb.get_connection_url())
        assert url.scheme == "crate"
        credentials, location = url.netloc.split("@")
        assert credentials == "crate:crate"
        host, port = location.split(":")
        assert host == cratedb.get_container_host_ip()
        assert int(port) == cratedb.get_exposed_port(cratedb.port)


@pytest.mark.parametrize(
    "cmd_opts, expected",
    [
        pytest.param(
            {"indices.breaker.total.limit": "90%"},
            "-Cdiscovery.type=single-node -Cindices.breaker.total.limit=90%",
            id="add_cmd_option",
        ),
        pytest.param(
            {"discovery.type": "zen", "indices.breaker.total.limit": "90%"},
            "-Cdiscovery.type=zen -Cindices.breaker.total.limit=90%",
            id="override_defaults",
        ),
    ],
)
def test_build_command(cmd_opts, expected):
    # Pure unit test: the command line is assembled in __init__, no container is started.
    cratedb = CrateDBContainer(cmd_opts=cmd_opts)
    assert cratedb._command == expected
