from pathlib import Path
import re
from unittest import mock

import pytest
import sqlalchemy

from testcontainers.core.utils import is_arm
from testcontainers.cockroachdb import CockroachDBContainer

def test_docker_run_mysql():
    config = CockroachDBContainer("cockroachdb/cockroach:24.0.1")
    with config as crdb:
        engine = sqlalchemy.create_engine(crdb.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].startswith("24.0.1")