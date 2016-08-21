import psycopg2

from testcontainers.generic import DockerContainer
from testcontainers.waiting_utils import wait_container_is_ready


class PostgresContainer(DockerContainer):
    def start(self):
        postgres = {
            "image": self.image,
            "env": {
                "POSTGRES_USER": "root",
                "POSTGRES_PASSWORD": "secret",
                "POSTGRES_DB": "test"
            },
            "bing_ports": {5432: 5432},
            "name": "postgres"
        }
        self._docker.run(**postgres)
        self.connection = self._get_connection
        return self

    @wait_container_is_ready()
    def _get_connection(self):
        return psycopg2.connect("dbname='test' user='root' host='localhost' password='secret'")

    def __init__(self, image="postgres:latest"):
        DockerContainer.__init__(self)
        self.image = image
        self.connection = None
