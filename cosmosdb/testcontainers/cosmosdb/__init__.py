from azure.core.exceptions import ServiceRequestError
from azure.cosmos import DatabaseProxy, CosmosClient, ContainerProxy, PartitionKey

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class CosmosDbEmulatorContainer(DockerContainer):
    AZURE_COSMOS_EMULATOR_PARTITION_COUNT = 3
    AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE = False
    IP_ADDRESS = 'localhost'

    def __init__(self,
                 image: str = "mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator",
                 ssl_verify: bool = False,
                 port_to_expose: int = 8081,
                 **kwargs):
        super(CosmosDbEmulatorContainer, self).__init__(image=image, **kwargs)
        self.ssl_verify = ssl_verify
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        self.with_bind_ports(port_to_expose, port_to_expose)
        self._configure()

    def _configure(self):
        # Additional Ports required by the emulator
        for p in range(10251, 10254):
            self.with_bind_ports(p, p)
        # Other emulator based config as per microsoft docs
        self.with_env("AZURE_COSMOS_EMULATOR_PARTITION_COUNT", self.AZURE_COSMOS_EMULATOR_PARTITION_COUNT)
        self.with_env("AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE",
                      self.AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE)
        # Bind to ip address
        self.with_env("IP_ADDRESS", self.IP_ADDRESS)

    def get_account_key(self):
        # static random key
        return "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

    def get_connection_url(self):
        return f"https://localhost:{self.port_to_expose}/"

    @wait_container_is_ready(ServiceRequestError)
    def _connect(self) -> CosmosClient:
        client = CosmosClient(self.get_connection_url(), credential=self.get_account_key(),
                              connection_verify=self.ssl_verify)
        return client

    def get_connection_client(self) -> CosmosClient:
        return self._connect()

    def boostrap_container(self, db_name: str, container_name: str, container_partition_key: str) -> ContainerProxy:
        client = self._connect()
        db: DatabaseProxy = client.create_database_if_not_exists(db_name)
        print(f"Database '{db_name}' created")
        partitioning: PartitionKey = PartitionKey(path=f"/{container_partition_key}", kind='Hash')
        container: ContainerProxy = db.create_container(id=container_name, partition_key=partitioning)
        print(f"Container '{container_name}' created")
        return container