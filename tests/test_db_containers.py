import psycopg2
import sqlalchemy
from pymongo import MongoClient

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.mysql import MySqlContainer, MariaDbContainer
from testcontainers.postgres import PostgresContainer


def test_docker_run_mysql():
    config = MySqlContainer(version='5.7.17')
    with config as mysql:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0] == '5.7.17'


def test_docker_run_postgress():
    postgres_container = PostgresContainer(version="9.5")
    with postgres_container as postgres:
        e = sqlalchemy.create_engine(postgres.get_connection_url())
        result = e.execute("select version()")

        for row in result:
            print("server version:", row[0])


def test_docker_run_mariadb():
    mariadb_container = MariaDbContainer()
    with mariadb_container as mariadb:
        e = sqlalchemy.create_engine(mariadb.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0] == '10.1.21-MariaDB-1~jessie'


def test_docker_generic_db():
    mongo_container = DockerContainer("mongo", "latest")
    mongo_container.expose_port(27017, 27017)

    with mongo_container:
        @wait_container_is_ready()
        def connect():
            return MongoClient("mongodb://0.0.0.0:27017")

        db = connect().primer
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
