#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
import re
from typing import Optional

from pymongo import MongoClient

from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy
from testcontainers.core.waiting_utils import wait_for_logs


class MongoDbContainer(DbContainer):
    """
    Mongo document-based database container.

    Example:

        .. doctest::

            >>> from testcontainers.mongodb import MongoDbContainer

            >>> with MongoDbContainer("mongo:7.0.7") as mongo:
            ...    db = mongo.get_connection_client().test
            ...    # Insert a database entry
            ...    result = db.restaurants.insert_one(
            ...        {
            ...            "name": "Vella",
            ...            "cuisine": "Italian",
            ...            "restaurant_id": "123456"
            ...        }
            ...    )
            ...    # Find the restaurant document
            ...    result = db.restaurants.find_one({"name": "Vella"})
            ...    result["restaurant_id"]
            '123456'
    """

    def __init__(
        self,
        image: str = "mongo:latest",
        port: int = 27017,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image=image, **kwargs)
        self.username = username if username else os.environ.get("MONGO_INITDB_ROOT_USERNAME", "test")
        self.password = password if password else os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "test")
        self.dbname = dbname if dbname else os.environ.get("MONGO_DB", "test")
        self.port = port
        self.with_exposed_ports(self.port)

    def _configure(self) -> None:
        self.with_env("MONGO_INITDB_ROOT_USERNAME", self.username)
        self.with_env("MONGO_INITDB_ROOT_PASSWORD", self.password)
        self.with_env("MONGO_DB", self.dbname)

    def get_connection_url(self) -> str:
        return self._create_connection_url(
            dialect="mongodb",
            username=self.username,
            password=self.password,
            port=self.port,
        )

    def _connect(self) -> None:
        regex = re.compile(r"waiting for connections", re.MULTILINE | re.IGNORECASE)

        def predicate(text: str) -> bool:
            return regex.search(text) is not None

        wait_for_logs(self, predicate)

    def get_connection_client(self) -> MongoClient:
        return MongoClient(self.get_connection_url())


class MongoDBAtlasLocalContainer(DbContainer):
    """
    MongoDB Atlas Local document-based database container.

    This is the local version of the Mongo Atlas service.
    It includes Mongo DB and Mongo Atlas Search services
    Example:

        .. doctest::

            >>> from testcontainers.mongodb import MongoDBAtlasLocalContainer
            >>> import time
            >>> with MongoDBAtlasLocalContainer("mongodb/mongodb-atlas-local:8.0.13") as mongo:
            ...    db = mongo.get_connection_client().test
            ...    # Insert a database entry
            ...    result = db.restaurants.insert_one(
            ...        {
            ...            "name": "Vella",
            ...            "cuisine": "Italian",
            ...            "restaurant_id": "123456"
            ...        }
            ...    )
            ...    # add an index
            ...    db.restaurants.create_search_index(
            ...        {
            ...            "definition": {
            ...                "mappings": {
            ...                    "dynamic": True
            ...                }
            ...            },
            ...            "name": "default"
            ...        }
            ...    )
            ...     # wait for the index to be created
            ...    time.sleep(1)
            ...
            ...    # Find the restaurant document
            ...    result = db.restaurants.aggregate([{
            ...        "$search": {
            ...            "index": "default",
            ...            "text": {
            ...                "query": "Vella",
            ...                "path": "name"
            ...            }
            ...        }
            ...    }]).next()
            ...    result["restaurant_id"]
            '123456'
    """

    def __init__(
        self,
        image: str = "mongodb/mongodb-atlas-local:latest",
        port: int = 27017,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image=image, **kwargs)
        self.username = username if username else os.environ.get("MONGODB_INITDB_ROOT_USERNAME", "test")
        self.password = password if password else os.environ.get("MONGODB_INITDB_ROOT_PASSWORD", "test")
        self.dbname = dbname if dbname else os.environ.get("MONGODB_INITDB_DATABASE", "test")
        self.port = port
        self.with_exposed_ports(self.port)

    def _configure(self) -> None:
        self.with_env("MONGODB_INITDB_ROOT_USERNAME", self.username)
        self.with_env("MONGODB_INITDB_ROOT_PASSWORD", self.password)
        self.with_env("MONGODB_INITDB_DATABASE", self.dbname)

    def get_connection_url(self) -> str:
        return (
            self._create_connection_url(
                dialect="mongodb",
                username=self.username,
                password=self.password,
                port=self.port,
            )
            + "?directConnection=true"
        )

    def _connect(self) -> None:
        strategy = HealthcheckWaitStrategy()
        strategy.wait_until_ready(self)

    def get_connection_client(self) -> MongoClient:
        return MongoClient(self.get_connection_url())
