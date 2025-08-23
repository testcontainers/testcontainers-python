from pathlib import Path

import requests

import pytest
import sqlalchemy

from testcontainers.starrocks import StarRocksContainer


def test_docker_run_starrocks():
    starrocks_container = StarRocksContainer()
    with starrocks_container as starrocks:
        host = starrocks.get_container_host_ip()
        port = starrocks.get_exposed_port(8030)
        
        response = requests.get(f'http://{host}:{port}/api/health')

        assert response.status_code == 200

@pytest.mark.inside_docker_check
def test_docker_run_starrocks_with_sqlalchemy():
    starrocks_container = StarRocksContainer()
    with starrocks_container as starrocks:
        engine = sqlalchemy.create_engine(starrocks.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].lower().startswith("8.0.33")
