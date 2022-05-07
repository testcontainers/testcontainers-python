import sqlalchemy
import pytest
from testcontainers.core.utils import is_arm
from testcontainers.mssql import SqlServerContainer
from testcontainers.mysql import MySqlContainer
from testcontainers.oracle import OracleDbContainer
from testcontainers.postgres import PostgresContainer


@pytest.mark.skipif(is_arm(), reason='mysql container not available for ARM')
def test_docker_run_mysql():
    config = MySqlContainer('mysql:5.7.17')
    with config as mysql:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0].startswith('5.7.17')


def test_docker_run_postgres():
    postgres_container = PostgresContainer("postgres:9.5")
    with postgres_container as postgres:
        e = sqlalchemy.create_engine(postgres.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0].lower().startswith("postgresql 9.5")


def test_docker_run_postgres_with_driver_pg8000():
    postgres_container = PostgresContainer("postgres:9.5", driver="pg8000")
    with postgres_container as postgres:
        e = sqlalchemy.create_engine(postgres.get_connection_url())
        e.execute("select 1=1")


def test_docker_run_mariadb():
    with MySqlContainer("mariadb:10.6.5").maybe_emulate_amd64() as mariadb:
        e = sqlalchemy.create_engine(mariadb.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0].startswith('10.6.5')


@pytest.mark.skip(reason="needs oracle client libraries unavailable on Travis")
def test_docker_run_oracle():
    with OracleDbContainer() as oracledb:
        e = sqlalchemy.create_engine(oracledb.get_connection_url())
        result = e.execute("select * from V$VERSION")
        versions = {'Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production',
                    'PL/SQL Release 11.2.0.2.0 - Production',
                    'CORE\t11.2.0.2.0\tProduction',
                    'TNS for Linux: Version 11.2.0.2.0 - Production',
                    'NLSRTL Version 11.2.0.2.0 - Production'}
        assert {row[0] for row in result} == versions


def test_docker_run_mssql():
    image = 'mcr.microsoft.com/azure-sql-edge'
    dialect = 'mssql+pymssql'
    with SqlServerContainer(image, dialect=dialect) as mssql:
        e = sqlalchemy.create_engine(mssql.get_connection_url())
        result = e.execute('select @@servicename')
        for row in result:
            assert row[0] == 'MSSQLSERVER'

    with SqlServerContainer(image, password="1Secure*Password2", dialect=dialect) as mssql:
        e = sqlalchemy.create_engine(mssql.get_connection_url())
        result = e.execute('select @@servicename')
        for row in result:
            assert row[0] == 'MSSQLSERVER'
