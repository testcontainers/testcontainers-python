from pymongo import MongoClient
from pymongo.errors import OperationFailure
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for
from testcontainers.mongodb import MongoDbContainer


def test_docker_generic_db():
    with DockerContainer("mongo:latest").with_bind_ports(27017, 27017) as mongo_container:
        def connect():
            host = mongo_container.get_container_host_ip()
            port = mongo_container.get_exposed_port(27017)
            return MongoClient(f"mongodb://{host}:{port}")

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
        assert result.inserted_id
        cursor = db.restaurants.find({"borough": "Manhattan"})
        for document in cursor:
            assert document


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
        connection_url = f"mongodb://{mongo.get_container_host_ip()}:" \
            f"{mongo.get_exposed_port(mongo.port)}"
        db = MongoClient(connection_url).test
        with pytest.raises(OperationFailure):
            db.restaurants.insert_one({})
