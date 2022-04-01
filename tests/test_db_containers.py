import sqlalchemy
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import pytest

from testcontainers.core.utils import is_arm
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for
from testcontainers.mongodb import MongoDbContainer
from testcontainers.mssql import SqlServerContainer
from testcontainers.mysql import MySqlContainer
from testcontainers.neo4j import Neo4jContainer
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
            print("server version:", row[0])


@pytest.mark.skip(reason='test does not verify additional code over `test_docker_run_postgres`')
def test_docker_run_greenplum():
    container = PostgresContainer("datagrip/greenplum:6.8", user="guest", password="guest",
                                  dbname="guest")
    with container:
        e = sqlalchemy.create_engine(container.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            print("server version:", row[0])


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


def test_docker_run_mongodb():
    with MongoDbContainer("mongo:latest") as mongo:
        db = mongo.get_connection_client().test
        doc = {
            "address": {
                "street": "2 Avenue",
                "zipcode": "10075",
                "building": "1480",
                "coord": [-73.9557413, 40.7720266]
            },
            "borough": "Manhattan",
            "cuisine": "Italian",
            "name": "Vella",
            "restaurant_id": "41704620"
        }
        db.restaurants.insert_one(doc)
        cursor = db.restaurants.find({"borough": "Manhattan"})
        assert cursor.next()['restaurant_id'] == doc['restaurant_id']


def test_docker_run_mongodb_connect_without_credentials():
    with MongoDbContainer() as mongo:
        connection_url = "mongodb://{}:{}".format(mongo.get_container_host_ip(),
                                                  mongo.get_exposed_port(mongo.port_to_expose))
        db = MongoClient(connection_url).test
        with pytest.raises(OperationFailure):
            db.restaurants.insert_one({})


def test_docker_run_neo4j_latest():
    with Neo4jContainer() as neo4j:
        with neo4j.get_driver() as driver:
            with driver.session() as session:
                result = session.run(
                    """
                    CALL dbms.components()
                    YIELD name, versions, edition
                    UNWIND versions as version
                    RETURN name, version, edition
                    """)
                record = result.single()
                print("server version:", record["name"], record["version"], record["edition"])
                assert record["name"].startswith("Neo4j")


def test_docker_generic_db():
    with DockerContainer("mongo:latest").with_bind_ports(27017, 27017) as mongo_container:
        def connect():
            return MongoClient("mongodb://{}:{}".format(mongo_container.get_container_host_ip(),
                                                        mongo_container.get_exposed_port(27017)))

        db = wait_for(connect).primer
        result = db.restaurants.insert_one(
            {
                "address": {
                    "street": "2 Avenue",
                    "zipcode": "10075",
                    "building": "1480",
                    "coord": [-73.9557413, 40.7720266]
                },
                "borough": "Manhattan",
                "cuisine": "Italian",
                "name": "Vella",
                "restaurant_id": "41704620"
            }
        )
        print(result.inserted_id)
        cursor = db.restaurants.find({"borough": "Manhattan"})
        for document in cursor:
            print(document)


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
