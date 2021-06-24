import pytest
import sqlalchemy
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for
from testcontainers.mongodb import MongoDbContainer
from testcontainers.mssql import SqlServerContainer
from testcontainers.mysql import MySqlContainer
from testcontainers.neo4j import Neo4jContainer
from testcontainers.oracle import OracleDbContainer
from testcontainers.postgres import PostgresContainer


def test_docker_run_mysql():
    config = MySqlContainer('mysql:5.7.17')
    with config as mysql:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0] == '5.7.17'


def test_docker_run_postgres():
    postgres_container = PostgresContainer("postgres:9.5")
    with postgres_container as postgres:
        e = sqlalchemy.create_engine(postgres.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            print("server version:", row[0])


def test_docker_run_greenplum():
    postgres_container = PostgresContainer("datagrip/greenplum:6.8",
                                           user="guest", password="guest", dbname="guest")
    with postgres_container as postgres:
        e = sqlalchemy.create_engine(postgres.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            print("server version:", row[0])


def test_docker_run_mariadb():
    mariadb_container = MySqlContainer("mariadb:10.2.9")
    with mariadb_container as mariadb:
        e = sqlalchemy.create_engine(mariadb.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0] == '10.2.9-MariaDB-10.2.9+maria~jessie'


@pytest.mark.skip(reason="needs oracle client libraries unavailable on Travis")
def test_docker_run_oracle():
    oracledb_container = OracleDbContainer()
    with oracledb_container as oracledb:
        e = sqlalchemy.create_engine(oracledb.get_connection_url())
        result = e.execute("select * from V$VERSION")
        versions = {'Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production',
                    'PL/SQL Release 11.2.0.2.0 - Production',
                    'CORE\t11.2.0.2.0\tProduction',
                    'TNS for Linux: Version 11.2.0.2.0 - Production',
                    'NLSRTL Version 11.2.0.2.0 - Production'}
        assert {row[0] for row in result} == versions


def test_docker_run_mongodb():
    mongo_container = MongoDbContainer("mongo:latest")
    with mongo_container as mongo:
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


def test_docker_run_neo4j_v35():
    neo4j_container = Neo4jContainer("neo4j:3.5")
    with neo4j_container as neo4j:
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
                assert record["version"].startswith("3.5")


def test_docker_run_neo4j_latest():
    neo4j_container = Neo4jContainer()
    with neo4j_container as neo4j:
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
    mongo_container = DockerContainer("mongo:latest")
    mongo_container.with_bind_ports(27017, 27017)

    with mongo_container:
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
    config = SqlServerContainer()
    with config as mssql:
        e = sqlalchemy.create_engine(mssql.get_connection_url())
        result = e.execute('select @@servicename')
        for row in result:
            assert row[0] == 'MSSQLSERVER'

    config = SqlServerContainer(password="1Secure*Password2")
    with config as mssql:
        e = sqlalchemy.create_engine(mssql.get_connection_url())
        result = e.execute('select @@servicename')
        for row in result:
            assert row[0] == 'MSSQLSERVER'
