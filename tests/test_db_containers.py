import MySQLdb
from pymongo import MongoClient

import psycopg2
import sqlalchemy
from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.mysql import MySqlContainer, MariaDbContainer
from testcontainers.postgres import PostgresContainer


def test_docker_run_mysql():
    config = MySqlContainer(version='5.7.17')
    with config as mysql:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0] == '5.7.15'


def test_docker_run_postgress():
    postgres_container = PostgresContainer(version="9.5")
    with postgres_container as postgres:
        conn = psycopg2.connect(postgres.get_connection_url())
        cur = conn.cursor()

        cur.execute("SELECT VERSION()")
        row = cur.fetchone()
        print("server version:", row[0])
        cur.close()
        assert len(row) > 0


def test_docker_run_mariadb():
    mariadb_container = MariaDbContainer("test", "test")
    with mariadb_container as mariadb:
        conn = MySQLdb.connect(host=mariadb.host_ip,
                               user=mariadb.username,
                               passwd=mariadb.password,
                               db=mariadb.database)
        cur = conn.cursor()

        cur.execute("SELECT VERSION()")
        row = cur.fetchone()
        cur.close()
        assert row[0] == '10.1.17-MariaDB-1~jessie'

def test_docker_generic_db():
    mongo_container = DockerContainer(image_name="mongo",
                                      version="latest",
                                      container_name="mongodb")
    mongo_container.bind_ports(27017, 27017)

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
