import pytest
import sqlalchemy

from testcontainers.core.utils import is_arm
from testcontainers.oracle import OracleDbContainer


@pytest.mark.skipif(is_arm(), reason="oracle-free container not available for ARM")
def test_docker_run_oracle_with_system_password():
    with OracleDbContainer(oracle_password="test") as oracledb:
        engine = sqlalchemy.create_engine(oracledb.get_connection_url())
        with engine.begin() as connection:
            test_val = 1
            result = connection.execute(sqlalchemy.text("SELECT {} FROM dual".format(test_val)))
            for row in result:
                assert row[0] == test_val


@pytest.mark.skipif(is_arm(), reason="oracle-free container not available for ARM")
def test_docker_run_oracle_with_username_password():
    with OracleDbContainer(username="test", password="test") as oracledb:
        engine = sqlalchemy.create_engine(oracledb.get_connection_url())
        with engine.begin() as connection:
            test_val = 1
            result = connection.execute(sqlalchemy.text("SELECT {} FROM dual".format(test_val)))
            for row in result:
                assert row[0] == test_val


@pytest.mark.skipif(is_arm(), reason="oracle-free container not available for ARM")
def test_docker_run_oracle_with_custom_db_and_system_username_password():
    with OracleDbContainer(oracle_password="coolpassword", dbname="myTestPDB") as oracledb:
        engine = sqlalchemy.create_engine(oracledb.get_connection_url())
        with engine.begin() as connection:
            test_val = 1
            result = connection.execute(sqlalchemy.text("SELECT {} FROM dual".format(test_val)))
            for row in result:
                assert row[0] == test_val


@pytest.mark.skipif(is_arm(), reason="oracle-free container not available for ARM")
def test_docker_run_oracle_with_custom_db_and_app_username_password():
    with OracleDbContainer(username="mycooluser", password="123connect", dbname="anotherPDB") as oracledb:
        engine = sqlalchemy.create_engine(oracledb.get_connection_url())
        with engine.begin() as connection:
            test_val = 1
            result = connection.execute(sqlalchemy.text("SELECT {} FROM dual".format(test_val)))
            for row in result:
                assert row[0] == test_val


@pytest.mark.skipif(is_arm(), reason="oracle-free container not available for ARM")
def test_docker_run_oracle_with_default_db_and_app_username_password():
    with OracleDbContainer(username="mycooluser", password="123connect") as oracledb:
        engine = sqlalchemy.create_engine(oracledb.get_connection_url())
        with engine.begin() as connection:
            test_val = 1
            result = connection.execute(sqlalchemy.text("SELECT {} FROM dual".format(test_val)))
            for row in result:
                assert row[0] == test_val


@pytest.mark.skipif(is_arm(), reason="oracle-free container not available for ARM")
def test_docker_run_oracle_with_cdb_and_system_username():
    with OracleDbContainer(oracle_password="MyOraclePWD1", dbname="free") as oracledb:
        engine = sqlalchemy.create_engine(oracledb.get_connection_url())
        with engine.begin() as connection:
            test_val = 1
            result = connection.execute(sqlalchemy.text("SELECT {} FROM dual".format(test_val)))
            for row in result:
                assert row[0] == test_val


@pytest.mark.skipif(is_arm(), reason="oracle-free container not available for ARM")
def test_doctest():
    with OracleDbContainer() as oracle:
        print(oracle.get_connection_url())
        engine = sqlalchemy.create_engine(oracle.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT 1 FROM dual"))
            assert result.fetchall() == [(1,)]
