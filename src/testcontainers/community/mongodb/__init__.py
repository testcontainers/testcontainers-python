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
import base64
import os
import re
import shlex
import time
from typing import Any, Optional
from urllib.parse import urlencode

from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError
from typing_extensions import Self

from testcontainers.core.config import testcontainers_config
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy, LogMessageWaitStrategy

_REPLICA_SET_KEYFILE_PATH = "/tmp/testcontainers-mongodb-keyfile"
_REPLICA_SET_ENTRYPOINT_PATH = "/tmp/testcontainers-mongodb-entrypoint.sh"
_REPLICA_SET_ENTRYPOINT = f"""#!/bin/bash
set -Eeuo pipefail
chown mongodb:mongodb {_REPLICA_SET_KEYFILE_PATH}
chmod 400 {_REPLICA_SET_KEYFILE_PATH}
exec /usr/local/bin/docker-entrypoint.sh "$@"
""".encode()


def _is_root_container_user(user: Any) -> bool:
    if user in (None, "", 0, "0", "root"):
        return True
    return isinstance(user, str) and user.partition(":")[0] in ("0", "root")


class MongoDbContainer(DbContainer):
    """
    Mongo document-based database container.

    Example:

        .. doctest::

            >>> from testcontainers.community.mongodb import MongoDbContainer

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
        super().__init__(
            image=image,
            _wait_strategy=LogMessageWaitStrategy(re.compile(r"waiting for connections", re.IGNORECASE)),
            **kwargs,
        )
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
        # LogMessageWaitStrategy handles waiting for container readiness
        pass

    def get_connection_client(self) -> MongoClient:
        return MongoClient(self.get_connection_url())


class MongoDbReplicaSetContainer(MongoDbContainer):
    """MongoDB container configured as a single-node replica set.

    Authentication is enabled by default and uses an ephemeral keyfile for internal
    replica-set authentication. Set ``auth_enabled=False`` to run without
    authentication or a keyfile.

    Automatic keyfile setup targets the official ``mongo`` image and requires the
    container to start as root before the image drops privileges to ``mongodb``.

    Example:

        .. code-block:: python

            from testcontainers.community.mongodb import MongoDbReplicaSetContainer

            with MongoDbReplicaSetContainer("mongo:7.0.7") as mongo:
                client = mongo.get_connection_client()
                with client.start_session() as session, session.start_transaction():
                    client.test.items.insert_one({"name": "example"}, session=session)

            with MongoDbReplicaSetContainer(
                "mongo:7.0.7",
                auth_enabled=False,
            ) as mongo:
                client = mongo.get_connection_client()
    """

    def __init__(
        self,
        image: str = "mongo:latest",
        port: int = 27017,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        replica_set: str = "docker-rs",
        auth_enabled: bool = True,
        **kwargs: Any,
    ) -> None:
        if not replica_set:
            raise ValueError("replica_set must not be empty")
        if not auth_enabled and (username is not None or password is not None):
            raise ValueError("username and password cannot be set when authentication is disabled")
        if auth_enabled:
            if "entrypoint" in kwargs:
                raise ValueError("entrypoint cannot be overridden for an authenticated replica set")
            if "user" in kwargs and not _is_root_container_user(kwargs["user"]):
                raise ValueError("authenticated replica sets must start as the root container user")
            kwargs["entrypoint"] = _REPLICA_SET_ENTRYPOINT_PATH

        super().__init__(
            image=image,
            port=port,
            username=username,
            password=password,
            dbname=dbname,
            **kwargs,
        )
        self.auth_enabled = auth_enabled
        self.replica_set = replica_set
        if not auth_enabled:
            self.username = ""
            self.password = ""
        else:
            super().with_copy_into_container(_REPLICA_SET_ENTRYPOINT, _REPLICA_SET_ENTRYPOINT_PATH, mode=0o755)
            keyfile = base64.b64encode(os.urandom(756))
            super().with_copy_into_container(keyfile, _REPLICA_SET_KEYFILE_PATH, mode=0o400)
        command = MongoDbReplicaSetContainer._replica_set_command(self, self._command)
        super().with_command(command)

    def _replica_set_command(self, command: Optional[str | list[str]]) -> list[str]:
        command_parts = shlex.split(command) if isinstance(command, str) else list(command or [])
        if command_parts and not (command_parts[0].startswith("-") or os.path.basename(command_parts[0]) == "mongod"):
            raise ValueError("replica set commands must contain mongod options or start with mongod")
        if any(
            part in ("--replSet", "--keyFile") or part.startswith(("--replSet=", "--keyFile="))
            for part in command_parts
        ):
            raise ValueError("replica set and keyfile options are managed by MongoDbReplicaSetContainer")

        command_parts.extend(["--replSet", self.replica_set])
        if self.auth_enabled:
            command_parts.extend(["--keyFile", _REPLICA_SET_KEYFILE_PATH])
        return command_parts

    def with_command(self, command: str | list[str]) -> Self:
        return super().with_command(self._replica_set_command(command))

    def with_kwargs(self, **kwargs: Any) -> Self:
        if self.auth_enabled:
            if "entrypoint" in kwargs:
                raise ValueError("entrypoint cannot be overridden for an authenticated replica set")
            if "user" in kwargs and not _is_root_container_user(kwargs["user"]):
                raise ValueError("authenticated replica sets must start as the root container user")
            kwargs["entrypoint"] = _REPLICA_SET_ENTRYPOINT_PATH
        return super().with_kwargs(**kwargs)

    def _configure(self) -> None:
        if self.auth_enabled:
            assert self.username is not None
            assert self.password is not None
            self.with_env("MONGO_INITDB_ROOT_USERNAME", self.username)
            self.with_env("MONGO_INITDB_ROOT_PASSWORD", self.password)
        else:
            self.env.pop("MONGO_INITDB_ROOT_USERNAME", None)
            self.env.pop("MONGO_INITDB_ROOT_PASSWORD", None)
        self.with_env("MONGO_DB", self.dbname)

    def get_connection_url(self) -> str:
        if self.auth_enabled:
            url = super().get_connection_url()
        else:
            host = self.get_container_host_ip()
            port = self.get_exposed_port(self.port)
            url = f"mongodb://{host}:{port}"

        return f"{url}/?{urlencode({'replicaSet': self.replica_set, 'directConnection': 'true'})}"

    def _connect(self) -> None:
        direct_url = self.get_connection_url().replace(
            urlencode({"replicaSet": self.replica_set, "directConnection": "true"}),
            urlencode({"directConnection": "true"}),
        )
        client: MongoClient[dict[str, Any]] = MongoClient(
            direct_url,
            serverSelectionTimeoutMS=1000,
            connectTimeoutMS=1000,
            socketTimeoutMS=1000,
        )
        deadline = time.monotonic() + testcontainers_config.timeout

        try:
            self._wait_for_mongodb(client, deadline)
            self._wait_for_replica_set_primary(client, deadline)
        finally:
            client.close()

    def _wait_for_mongodb(self, client: MongoClient[dict[str, Any]], deadline: float) -> None:
        last_error: Optional[Exception] = None
        while time.monotonic() < deadline:
            self._raise_if_replica_set_container_stopped()
            try:
                client.admin.command("ping")
                return
            except PyMongoError as error:
                last_error = error
                time.sleep(testcontainers_config.sleep_time)

        raise ContainerStartException("MongoDB did not become ready") from last_error

    def _wait_for_replica_set_primary(self, client: MongoClient[dict[str, Any]], deadline: float) -> None:
        last_error: Optional[Exception] = None
        while time.monotonic() < deadline:
            self._raise_if_replica_set_container_stopped()
            try:
                self._initiate_replica_set_if_needed(client)
                if client.admin.command("hello").get("isWritablePrimary"):
                    return
            except OperationFailure:
                raise
            except PyMongoError as error:
                last_error = error
            time.sleep(testcontainers_config.sleep_time)

        raise ContainerStartException("MongoDB replica set did not elect a primary") from last_error

    def _initiate_replica_set_if_needed(self, client: MongoClient[dict[str, Any]]) -> None:
        try:
            client.admin.command("replSetGetStatus")
            return
        except OperationFailure as error:
            if error.code != 94:  # NotYetInitialized
                raise

        try:
            client.admin.command(
                {
                    "replSetInitiate": {
                        "_id": self.replica_set,
                        "members": [{"_id": 0, "host": f"localhost:{self.port}"}],
                    }
                }
            )
        except OperationFailure as error:
            if error.code != 23:  # AlreadyInitialized
                raise

    def _raise_if_replica_set_container_stopped(self) -> None:
        self.reload()
        if self.status not in ("exited", "dead"):
            return

        stdout, stderr = self.get_logs()
        logs = (stdout + stderr).decode(errors="replace")
        raise ContainerStartException(f"MongoDB stopped while initializing its replica set:\n{logs}")


class MongoDBAtlasLocalContainer(DbContainer):
    """
    MongoDB Atlas Local document-based database container.

    This is the local version of the Mongo Atlas service.
    It includes Mongo DB and Mongo Atlas Search services
    Example:

        .. doctest::

            >>> from testcontainers.community.mongodb import MongoDBAtlasLocalContainer
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
            ...    _ = db.restaurants.create_search_index(
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
