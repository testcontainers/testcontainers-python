from unittest import mock

import pytest
import sqlalchemy

from testcontainers.core.utils import is_arm
from testcontainers.db2 import Db2Container


@pytest.mark.skipif(is_arm(), reason="db2 container not available for ARM")
@pytest.mark.parametrize("version", ["11.5.9.0", "11.5.8.0"])
def test_docker_run_db2(version: str):
    with Db2Container(f"icr.io/db2_community/db2:{version}", password="password") as db2:
        engine = sqlalchemy.create_engine(db2.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select service_level from sysibmadm.env_inst_info"))
            for row in result:
                assert row[0] == f"DB2 v{version}"


# This is a feature in the generic DbContainer class
# but it can't be tested on its own
# so is tested in various database modules:
# - mysql / mariadb
# - postgresql
# - sqlserver
# - mongodb
# - db2
@pytest.mark.skipif(is_arm(), reason="db2 container not available for ARM")
def test_quoted_password():
    user = "db2inst1"
    dbname = "testdb"
    password = "p@$%25+0&%rd :/!=?"
    quoted_password = "p%40%24%2525+0%26%25rd %3A%2F%21%3D%3F"
    kwargs = {
        "username": user,
        "password": password,
        "dbname": dbname,
    }
    with Db2Container("icr.io/db2_community/db2:11.5.9.0", **kwargs) as container:
        port = container.get_exposed_port(50000)
        host = container.get_container_host_ip()
        expected_url = f"db2+ibm_db://{user}:{quoted_password}@{host}:{port}/{dbname}"
        assert expected_url == container.get_connection_url()
