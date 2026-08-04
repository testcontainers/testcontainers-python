import time
from urllib.parse import parse_qs, urlsplit

import pytest

from testcontainers.community.mongodb import MongoDBAtlasLocalContainer, MongoDbContainer, MongoDbReplicaSetContainer


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


@pytest.mark.parametrize("version", ["7.0.7", "6.0.14", "5.0.26"])
def test_docker_run_mongodb_replica_set_without_authentication(version: str):
    with MongoDbReplicaSetContainer(f"mongo:{version}", replica_set="docker-rs", auth_enabled=False) as mongo:
        connection_url = urlsplit(mongo.get_connection_url())
        assert connection_url.username is None
        assert parse_qs(connection_url.query) == {
            "directConnection": ["true"],
            "replicaSet": ["docker-rs"],
        }

        client = mongo.get_connection_client()

        hello = client.admin.command("hello")
        assert hello["setName"] == "docker-rs"
        assert hello["isWritablePrimary"] is True

        collection = client.test.transactions
        with client.start_session() as session, session.start_transaction():
            result = collection.insert_one({"message": "replica sets support transactions"}, session=session)

        assert collection.find_one({"_id": result.inserted_id}) is not None


@pytest.mark.parametrize("version", ["7.0.7", "6.0.14", "5.0.26"])
def test_docker_run_authenticated_mongodb_replica_set(version: str):
    container = MongoDbReplicaSetContainer(
        f"mongo:{version}",
        username="replica-user",
        password="replica-password",
        replica_set="secure-rs",
        command=["--profile", "1"],
    ).with_kwargs(labels={"testcontainers.mongodb.replica-set": "true"})

    with container as mongo:
        connection_url = urlsplit(mongo.get_connection_url())
        assert connection_url.username == "replica-user"
        assert connection_url.password == "replica-password"
        assert parse_qs(connection_url.query) == {
            "directConnection": ["true"],
            "replicaSet": ["secure-rs"],
        }

        client = mongo.get_connection_client()

        hello = client.admin.command("hello")
        assert hello["setName"] == "secure-rs"
        assert hello["isWritablePrimary"] is True

        result = client.test.documents.insert_one({"authenticated": True})
        assert client.test.documents.find_one({"_id": result.inserted_id}) == {
            "_id": result.inserted_id,
            "authenticated": True,
        }


@pytest.mark.parametrize("username,password", [("user", None), (None, "password")])
def test_mongodb_rejects_credentials_when_authentication_is_disabled(
    username: str | None,
    password: str | None,
):
    with pytest.raises(ValueError, match="authentication is disabled"):
        MongoDbReplicaSetContainer(auth_enabled=False, username=username, password=password)


def test_authenticated_mongodb_replica_set_rejects_non_root_container_user():
    with pytest.raises(ValueError, match="root container user"):
        MongoDbReplicaSetContainer(replica_set="secure-rs", user="mongodb")


def test_mongodb_replica_set_rejects_non_mongod_command():
    with pytest.raises(ValueError, match="mongod options"):
        MongoDbReplicaSetContainer(replica_set="secure-rs", command=["bash", "-lc", "exec mongod"])


@pytest.mark.parametrize("version", ["8.0.13", "7.0.23"])
def test_docker_run_mongodb_atlas_local(version: str):
    with MongoDBAtlasLocalContainer(f"mongodb/mongodb-atlas-local:{version}") as mongo_atlas:
        db = mongo_atlas.get_connection_client().test
        index_doc = {
            "definition": {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        "borough": {"analyzer": "lucene.keyword", "type": "string"},
                    },
                },
            },
            "name": "test",
        }

        db.create_collection("restaurants")

        db.restaurants.create_search_index(index_doc)

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

        # Wait for index to catch up
        indexes = db.restaurants.list_search_indexes()
        while indexes.next()["status"] != "READY":
            time.sleep(0.1)
            indexes = db.restaurants.list_search_indexes()

        cursor = db.restaurants.aggregate(
            [{"$search": {"index": "test", "text": {"query": "Manhattan", "path": "borough"}}}]
        )
        assert cursor.next()["restaurant_id"] == doc["restaurant_id"]


# This is a feature in the generic DbContainer class
# but it can't be tested on its own
# so is tested in various database modules:
# - mysql / mariadb
# - postgresql
# - sqlserver
# - mongodb
# - db2
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
