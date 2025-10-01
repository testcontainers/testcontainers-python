import sqlalchemy
import pytest
from testcontainers.cratedb import CrateDBContainer


@pytest.mark.parametrize("version", ["5.9", "5.10", "6.0", "latest"])
def test_docker_run_cratedb(version: str):
    with CrateDBContainer(f"crate:{version}") as container:
        engine = sqlalchemy.create_engine(container.get_connection_url())
        with engine.begin() as conn:
            result = conn.execute(sqlalchemy.text("select 1+2+3+4+5"))
            sum_result = result.fetchone()[0]
            assert sum_result == 15


@pytest.mark.parametrize(
    "opts, expected",
    [
        pytest.param(
            {"indices.breaker.total.limit": "90%"},
            (
                "-Cdiscovery.type=single-node "
                "-Cnode.attr.storage=hot "
                "-Cpath.repo=/tmp/snapshots "
                "-Cindices.breaker.total.limit=90%"
            ),
            id="add_cmd_option",
        ),
        pytest.param(
            {"discovery.type": "zen", "indices.breaker.total.limit": "90%"},
            (
                "-Cdiscovery.type=zen "
                "-Cnode.attr.storage=hot "
                "-Cpath.repo=/tmp/snapshots "
                "-Cindices.breaker.total.limit=90%"
            ),
            id="override_defaults",
        ),
    ],
)
def test_build_command(opts, expected):
    db = CrateDBContainer(cmd_opts=opts)
    assert db._command == expected
