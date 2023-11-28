import re
from unittest import mock

import sqlalchemy
from testcontainers.greptimedb import GreptimeDBContainer


def test_docker_run_greptimedb():
    config = GreptimeDBContainer("greptime/greptimedb:v0.4.3")
    with config as greptimedb:
        engine = sqlalchemy.create_engine(greptimedb.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].startswith("v0.4.3")
