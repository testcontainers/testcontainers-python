import os
from azure.core.exceptions import ServiceRequestError
from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy, PartitionKey
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.backends import default_backend
import datetime

class CosmosDbEmulatorContainer(DockerContainer):

    AZURE_COSMOS_EMULATOR_PARTITION_COUNT = 3
    AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE = False
    AZURE_COSMOS_EMULATOR_IP_ADDRESS_OVERRIDE = "127.0.0.1"
    WEBSITE_DYNAMIC_CACHE = 0
    IP_ADDRESS = 'https://127.0.0.1'
    SSL_CERT_FILE = 'cosmos_emulator.crt'
    SSL_KEY_FILE = 'cosmos_emulator.key'

    def __init__(self, image: str = "mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator",
                 port_to_expose: int = 8081, **kwargs):
        super(CosmosDbEmulatorContainer, self).__init__(image=image, **kwargs)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        self.with_bind_ports(port_to_expose, port_to_expose)
        self._configure()

    def _generate_self_signed_cert(self, hostname):
        # Generate a private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Create a self-signed certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ])
        certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            # Certificate valid for 1 year
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(hostname)]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())

        # Write the private key to a file
        with open(self.SSL_KEY_FILE, "wb") as key_file:
            key_file.write(private_key.private_bytes(
                Encoding.PEM,
                PrivateFormat.TraditionalOpenSSL,
                NoEncryption()
            ))

        with open(self.SSL_CERT_FILE, "wb") as cert_file:
            cert_file.write(certificate.public_bytes(Encoding.PEM))

    def _configure(self):
        self._generate_self_signed_cert(self.IP_ADDRESS)
        self.with_volume_mapping(os.path.abspath(self.SSL_CERT_FILE), '/bin/bin/bin/cosmos' + self.SSL_CERT_FILE)
        self.with_volume_mapping(os.path.abspath(self.SSL_KEY_FILE), '/bin/bin/bin/cosmos' + self.SSL_KEY_FILE)

        for p in range(10251, 10254):
            self.with_bind_ports(p, p)
        self.with_bind_ports(self.port_to_expose, self.port_to_expose)

        self.with_env("AZURE_COSMOS_EMULATOR_PARTITION_COUNT", self.AZURE_COSMOS_EMULATOR_PARTITION_COUNT)
        self.with_env("AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE", self.AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE)
        self.with_env("AZURE_COSMOS_EMULATOR_IP_ADDRESS_OVERRIDE", self.AZURE_COSMOS_EMULATOR_IP_ADDRESS_OVERRIDE)
        self.with_env("WEBSITE_DYNAMIC_CACHE", self.WEBSITE_DYNAMIC_CACHE)
        self.with_env("IP_ADDRESS", self.IP_ADDRESS)

    def get_account_key(self):
        return "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

    def get_connection_url(self):
        return f"{self.IP_ADDRESS}:{self.port_to_expose}/"

    @wait_container_is_ready(ServiceRequestError)
    def _connect(self) -> CosmosClient:
        client = CosmosClient(self.get_connection_url(), credential=self.get_account_key(), connection_verify=False)
        return client

    def get_connection_client(self) -> CosmosClient:
        return self._connect()

    def bootstrap_container(self, db_name: str, container_name: str, container_partition_key: str) -> ContainerProxy:
        client = self._connect()
        db: DatabaseProxy = client.create_database_if_not_exists(db_name)
        partitioning: PartitionKey = PartitionKey(path=f"/{container_partition_key}", kind='Hash')
        container: ContainerProxy = db.create_container(id=container_name, partition_key=partitioning)
        return container
