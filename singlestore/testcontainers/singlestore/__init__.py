from os import environ
from tempfile import NamedTemporaryFile
from testcontainers.core.generic import DbContainer

SINGLESTORE_INIT_SCRIPT_FILE = '/init.sql'


class SingleStoreContainer(DbContainer):
    """
    SingleStore database container.

    Example:

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.singlestore import SingleStoreContainer
            >>> with SingleStoreContainer() as singlestore:
            ...    engine = sqlalchemy.create_engine(singlestore.get_connection_url())
            ...    with engine.begin() as connection:
            ...        result = connection.execute(sqlalchemy.text(
            ...            'select 1'
            ...        ))
    """

    def __init__(
            self,
            image: str = "ghcr.io/singlestore-labs/singlestoredb-dev:latest",
            port: int = 3306,
            password: str = 'password',
            dbname: str = 'test_db',
            dialect: str = 'mysql+pymysql',
            singlestore_license: str = None,
            singlestore_version: str = None,
            **kwargs
    ):
        super(SingleStoreContainer, self).__init__(image, **kwargs)

        self.port = port
        self.with_exposed_ports(self.port)

        self.username = 'root'
        self.password = password or environ.get(
            'SINGLESTORE_ROOT_PASSWORD',
            'password'
        )
        self.dbname = dbname or environ.get('SINGLESTORE_DATABASE', 'test_db')
        self.singlestore_license = singlestore_license or environ.get('SINGLESTORE_LICENSE')
        self.singlestore_version = singlestore_version or environ.get('SINGLESTORE_VERSION')

        self.dialect = dialect

        self.init_script = NamedTemporaryFile(prefix='singlestore-init-script')

    def _configure(self):
        self.with_env("ROOT_PASSWORD", self.password)
        self.with_env("SINGLESTORE_LICENSE", self.singlestore_license)
        self.with_env("LICENSE_KEY", self.singlestore_license)
        self.with_env("START_AFTER_INIT", 'Y')

        if self.singlestore_version:
            self.with_env("SINGLESTORE_VERSION", self.singlestore_version)

        self.maybe_emulate_amd64()

        self.map_init_script()

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect=self.dialect,
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            port=self.port
        )

    def map_init_script(self):
        self.init_script.write(f'CREATE DATABASE IF NOT EXISTS {self.dbname};')
        self.init_script.flush()
        self.with_volume_mapping(self.init_script.name, SINGLESTORE_INIT_SCRIPT_FILE)

    def stop(self, force=True, delete_volume=True):
        self.init_script.close()
        super().stop(force, delete_volume)
