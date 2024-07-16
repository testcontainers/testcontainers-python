import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from testcontainers.mongodb import MongoDbContainer


@pytest.mark.parametrize("version", ["7.0.7", "6.0.14", "5.0.26"])
def test_docker_run_mongodb(version: str):
    with MongoDbContainer(f"mongo:{version}") as mongo:
        db = mongo.get_connection_client().test
        doc = {
            "address": {
                "street": "2 Avenue",
                "zipcode": "10075",
                "building": "1480",
                "coord": [-73.9557413, 40.7720266],
            },
            "borough": "Manhattan",
            "cuisine": "Italian",
            "name": "Vella",
            "restaurant_id": "41704620",
        }
        result = db.restaurants.insert_one(doc)
        assert result.inserted_id

        cursor = db.restaurants.find({"borough": "Manhattan"})
        assert cursor.next()["restaurant_id"] == doc["restaurant_id"]


# This is a feature in the generic DbContainer class
# but it can't be tested on its own
# so is tested in various database modules:
# - mysql / mariadb
# - postgresql
# - sqlserver
# - mongodb
def test_quoted_password():
    user = "root"
    password = "p@$%25+0&%rd :/!=?"
    quoted_password = "p%40%24%2525+0%26%25rd %3A%2F%21%3D%3F"
    # driver = "pymongo"
    kwargs = {
        "username": user,
        "password": password,
    }
    with MongoDbContainer("mongo:7.0.7", **kwargs) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(27017)
        expected_url = f"mongodb://{user}:{quoted_password}@{host}:{port}"
        url = container.get_connection_url()
        assert url == expected_url
