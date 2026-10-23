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
import json
import os
import time
import urllib.error
import urllib.request
from datetime import timedelta
from typing import Any, Optional
from urllib.parse import urlencode

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.diagnostics import ServiceType
from couchbase.options import ClusterOptions, ClusterTimeoutOptions, WaitUntilReadyOptions
from typing_extensions import Self

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy

_DEFAULT_SCOPE = "_default"
_DEFAULT_COLLECTION = "_default"
_SERVICES = ("kv", "n1ql", "index", "fts")

# Container ports used by the services this module enables (non-TLS).
# https://docs.couchbase.com/server/current/install/install-ports.html
_MGMT_PORT = 8091
_VIEWS_PORT = 8092
_QUERY_PORT = 8093
_SEARCH_PORT = 8094
_KV_PORT = 11210


class CouchbaseContainer(DockerContainer):
    """
    Couchbase Server container.

    Starts a single-node cluster running the Data, Query, Index and Search services,
    and creates a bucket (and optionally a scope and collection) that is ready to use.
    It uses the Community Edition image by default; pass ``image`` to use another one,
    e.g. ``couchbase/server:enterprise-8.0.0``.

    Example:

        .. doctest::

            >>> from testcontainers.community.couchbase import CouchbaseContainer

            >>> with CouchbaseContainer() as couchbase:
            ...     cluster = couchbase.client()
            ...     collection = cluster.bucket("default").default_collection()
            ...     _ = collection.upsert("greeting", {"hello": "world"})
            ...     collection.get("greeting").content_as[dict]
            {'hello': 'world'}
    """

    def __init__(
        self,
        image: str = "couchbase/server:community-8.0.2",
        username: Optional[str] = None,
        password: Optional[str] = None,
        bucket: Optional[str] = None,
        scope: Optional[str] = None,
        collection: Optional[str] = None,
        bucket_ram_quota_mb: int = 256,
        **kwargs: Any,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.username = username or os.environ.get("COUCHBASE_USERNAME", "Administrator")
        self.password = password or os.environ.get("COUCHBASE_PASSWORD", "password")
        self.bucket = bucket or os.environ.get("COUCHBASE_BUCKET", "default")
        self.scope = scope or os.environ.get("COUCHBASE_SCOPE", _DEFAULT_SCOPE)
        self.collection = collection or os.environ.get("COUCHBASE_COLLECTION", _DEFAULT_COLLECTION)
        self.bucket_ram_quota_mb = bucket_ram_quota_mb

        self.with_exposed_ports(_MGMT_PORT, _VIEWS_PORT, _QUERY_PORT, _SEARCH_PORT, _KV_PORT)
        # The node answers on /pools as soon as the management service is up,
        # even before the cluster is initialized.
        self.waiting_for(HttpWaitStrategy(_MGMT_PORT, "/pools"))

    def start(self) -> Self:
        super().start()
        self._initialize_cluster()
        self._create_bucket()
        if self.scope != _DEFAULT_SCOPE:
            self._post(_MGMT_PORT, f"/pools/default/buckets/{self.bucket}/scopes", {"name": self.scope})
        if self.collection != _DEFAULT_COLLECTION:
            self._post(
                _MGMT_PORT,
                f"/pools/default/buckets/{self.bucket}/scopes/{self.scope}/collections",
                {"name": self.collection},
            )
        self._wait_for_query_keyspace()
        return self

    def get_connection_url(self) -> str:
        return f"couchbase://{self.get_container_host_ip()}:{self.get_exposed_port(_KV_PORT)}"

    def client(self, cluster_options: Optional[ClusterOptions] = None) -> Cluster:
        """Return a connected :class:`couchbase.cluster.Cluster`."""
        if cluster_options is None:
            cluster_options = ClusterOptions(
                PasswordAuthenticator(self.username, self.password),
                timeout_options=ClusterTimeoutOptions(kv_timeout=timedelta(seconds=10)),
            )
        cluster = Cluster(self.get_connection_url(), cluster_options)
        cluster.wait_until_ready(
            timedelta(seconds=30),
            WaitUntilReadyOptions(service_types=[ServiceType.KeyValue, ServiceType.Query, ServiceType.Search]),
        )
        return cluster

    def _initialize_cluster(self) -> None:
        # Mirrors the REST-based setup recommended for scripted cluster initialization:
        # https://docs.couchbase.com/server/current/manage/manage-nodes/initialize-node.html
        internal_ip = self.get_docker_client().bridge_ip(str(self.get_wrapped_container().id))
        self._post(_MGMT_PORT, "/node/controller/rename", {"hostname": internal_ip}, auth=False)
        self._post(_MGMT_PORT, "/node/controller/setupServices", {"services": ",".join(_SERVICES)}, auth=False)
        self._post(
            _MGMT_PORT,
            "/pools/default",
            {"memoryQuota": 256, "indexMemoryQuota": 256, "ftsMemoryQuota": 256},
            auth=False,
        )
        self._post(
            _MGMT_PORT,
            "/settings/web",
            {"username": self.username, "password": self.password, "port": "SAME"},
            auth=False,
        )

        # Advertise the host-mapped ports so SDKs running on the host can reach every service.
        host = self.get_container_host_ip()
        self._request(
            "PUT",
            _MGMT_PORT,
            "/node/controller/setupAlternateAddresses/external",
            {
                "hostname": host,
                "mgmt": self.get_exposed_port(_MGMT_PORT),
                "capi": self.get_exposed_port(_VIEWS_PORT),
                "n1ql": self.get_exposed_port(_QUERY_PORT),
                "fts": self.get_exposed_port(_SEARCH_PORT),
                "kv": self.get_exposed_port(_KV_PORT),
            },
        )

        # Community Edition only supports the ForestDB-based standard GSI storage mode.
        is_enterprise = self._get(_MGMT_PORT, "/pools").get("isEnterprise", False)
        storage_mode = "memory_optimized" if is_enterprise else "forestdb"
        self._post(_MGMT_PORT, "/settings/indexes", {"storageMode": storage_mode})

    def _create_bucket(self) -> None:
        self._post(
            _MGMT_PORT,
            "/pools/default/buckets",
            {
                "name": self.bucket,
                "bucketType": "couchbase",
                "storageBackend": "couchstore",
                "ramQuotaMB": self.bucket_ram_quota_mb,
                "replicaNumber": 0,
                "flushEnabled": 1,
            },
        )
        self._poll(self._is_bucket_ready, f"bucket '{self.bucket}' to become ready")

    def _is_bucket_ready(self) -> bool:
        # The bucket config is what SDKs bootstrap from, so wait until it is served
        # and advertises every enabled service (index ports are named e.g. "indexAdmin").
        try:
            nodes = self._get(_MGMT_PORT, f"/pools/default/b/{self.bucket}").get("nodesExt", [])
        except OSError:
            return False
        return bool(nodes) and all(
            any(name.startswith(service) for name in node.get("services", {}))
            for node in nodes
            for service in _SERVICES
        )

    def _wait_for_query_keyspace(self) -> None:
        statement = f'SELECT COUNT(*) > 0 AS present FROM system:keyspaces WHERE name = "{self.bucket}"'

        def is_present() -> bool:
            try:
                result = self._post(_QUERY_PORT, "/query/service", {"statement": statement})
            except OSError:
                return False
            return bool(result.get("results") and result["results"][0].get("present"))

        self._poll(is_present, f"bucket '{self.bucket}' to be queryable")

    @staticmethod
    def _poll(condition: Any, description: str) -> None:
        deadline = time.monotonic() + c.timeout
        while time.monotonic() < deadline:
            if condition():
                return
            time.sleep(c.sleep_time)
        raise TimeoutError(f"Timed out after {c.timeout}s waiting for {description}")

    def _get(self, port: int, path: str) -> Any:
        return self._request("GET", port, path)

    def _post(self, port: int, path: str, data: dict[str, Any], auth: bool = True) -> Any:
        return self._request("POST", port, path, data, auth)

    def _request(
        self, method: str, port: int, path: str, data: Optional[dict[str, Any]] = None, auth: bool = True
    ) -> Any:
        url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(port)}{path}"
        body = urlencode(data).encode() if data is not None else None
        request = urllib.request.Request(url, data=body, method=method)
        if auth:
            token = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            request.add_header("Authorization", f"Basic {token}")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode()
        except urllib.error.HTTPError as e:
            e.msg = f"{e.msg}: {e.read().decode(errors='replace')}"
            raise
        try:
            return json.loads(payload) if payload else None
        except json.JSONDecodeError:
            return payload
