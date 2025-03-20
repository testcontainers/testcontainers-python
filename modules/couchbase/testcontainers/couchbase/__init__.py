import os
from datetime import timedelta
from time import sleep
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, ClusterTimeoutOptions, TLSVerifyMode
from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


# noinspection HttpUrlsUsage,SpellCheckingInspection
class CouchbaseContainer(DbContainer):
    """
    Couchbase database container.

    Example:
        The example spins up a Couchbase database and connects to it using
        the `Couchbase Python Client`.

        .. doctest::

            >>> from couchbase.auth import PasswordAuthenticator
            >>> from couchbase.cluster import Cluster
            >>> from testcontainers.couchbase import CouchbaseContainer

            >>> with CouchbaseContainer("couchbase:latest") as couchbase:
            ...     cluster = couchbase.client()
            ...     # Use the cluster for various operations

        This creates a single-node Couchbase database container with the default bucket, scope, and collection.

        If you would like to pass custom values for the image, cluster_port, username, password, bucket, scope, and collection, you can use:
            username = "administrator"
            password = "password"
            bucket_name = "mybucket"
            scope_name = "myscope"
            collection_name = "mycollection"
            image = "couchbase:latest"
            cluster_port = 8091

            with CouchbaseContainer(image=image, cluster_port=cluster_port, username=username, password=password, bucket=bucket_name, scope=scope_name,
                                    collection=collection_name) as couchbase_container:
                cluster = couchbase_container.client()
                collection = cluster.bucket(bucket_name=bucket_name).scope(name=scope_name).collection(name=collection_name)
                key = uuid.uuid4().hex
                value = "world"
                doc = {
                    "hello": value,
                }
                collection.upsert(key=key, value=doc)
                returned_doc = collection.get(key=key)
                print(returned_doc.value['hello'])

                # Output: world
    """

    def __init__(
        self,
        image: str = "couchbase:latest",
        cluster_port: Optional[int] = 8091,
        username: Optional[str] = None,
        password: Optional[str] = None,
        bucket: Optional[str] = None,
        scope: Optional[str] = None,
        collection: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self._username = username or os.environ.get("COUCHBASE_USERNAME", "Administrator")
        self._password = password or os.environ.get("COUCHBASE_PASSWORD", "password")
        self._bucket = bucket or os.environ.get("COUCHBASE_BUCKET", "default")
        self._scope = scope or os.environ.get("COUCHBASE_SCOPE", "default")
        self._collection = collection or os.environ.get("COUCHBASE_COLLECTION", "default")
        self._cluster_port = cluster_port

        ports = [
            cluster_port,
            8092,
            8093,
            8094,
            8095,
            8096,
            8097,
            9123,
            11207,
            11210,
            11280,
            18091,
            18092,
            18093,
            18094,
            18095,
            18096,
            18097,
        ]

        for port in ports:
            self.with_exposed_ports(port)
            self.with_bind_ports(port, port)

    @wait_container_is_ready()
    def _connect(self):
        wait_for_logs(self, "and logs available in")
        while True:
            sleep(1)
            try:
                url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self._cluster_port)}/settings/web"
                response = requests.get(url)
                if 200 <= response.status_code < 300:
                    break
                else:
                    pass
            except requests.exceptions.ConnectionError:
                pass

    def _configure(self) -> None:
        self.with_env("COUCHBASE_USERNAME", self._username)
        self.with_env("COUCHBASE_PASSWORD", self._password)
        self.with_env("COUCHBASE_BUCKET", self._bucket)

    def start(self) -> "CouchbaseContainer":
        self._configure()
        super().start()
        self._connect()
        self.set_admin_credentials()
        self._create_bucket()
        self._create_scope()
        self._create_collection()
        return self

    def set_admin_credentials(self):
        url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self._cluster_port)}/settings/web"
        data = {"username": self._username, "password": self._password, "port": "SAME"}
        response = requests.post(url, data=data)
        if 200 <= response.status_code < 300:
            return
        else:
            raise RuntimeError(response.text)

    def _create_bucket(self) -> None:
        url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self._cluster_port)}/pools/default/buckets"
        data = {"name": self._bucket, "bucketType": "couchbase", "ramQuotaMB": 256}
        response = requests.post(url, data=data, auth=HTTPBasicAuth(self._username, self._password))
        if 200 <= response.status_code < 300:
            return
        else:
            raise RuntimeError(response.text)

    def _create_scope(self):
        url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self._cluster_port)}/pools/default/buckets/{self._bucket}/scopes"
        data = {"name": self._scope}
        response = requests.post(url, data=data, auth=HTTPBasicAuth(self._username, self._password))
        if 200 <= response.status_code < 300:
            return
        else:
            raise RuntimeError(response.text)

    def _create_collection(self):
        url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self._cluster_port)}/pools/default/buckets/{self._bucket}/scopes/{self._scope}/collections"
        data = {"name": self._collection, "maxTTL": 3600, "history": str(False).lower()}
        response = requests.post(url, data=data, auth=HTTPBasicAuth(self._username, self._password))
        if 200 <= response.status_code < 300:
            return
        else:
            raise RuntimeError(response.text)

    def get_connection_url(self) -> str:
        return f"couchbases://{self.get_container_host_ip()}"

    def client(self, cluster_options: ClusterOptions = None):
        auth = PasswordAuthenticator(self._username, self._password)
        if cluster_options is None:
            cluster_options = ClusterOptions(
                auth,
                timeout_options=ClusterTimeoutOptions(kv_timeout=timedelta(seconds=10)),
                enable_tcp_keep_alive=True,
                tls_verify=TLSVerifyMode.NONE,
            )
        cluster = Cluster(self.get_connection_url(), cluster_options)
        cluster.wait_until_ready(timedelta(seconds=15))
        return cluster
