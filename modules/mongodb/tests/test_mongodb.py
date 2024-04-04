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
