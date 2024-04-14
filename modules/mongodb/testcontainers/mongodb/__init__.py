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
from typing import Optional

from pymongo import MongoClient

from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
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
        wait_for_logs(self, "Waiting for connections")

    def get_connection_client(self) -> MongoClient:
        return MongoClient(self.get_connection_url())
