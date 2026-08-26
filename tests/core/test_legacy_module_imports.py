import importlib
import sys

import pytest

MODULES = {
    "arangodb": ["ArangoDbContainer"],
    "aws": ["AWSLambdaContainer"],
    "azurite": ["AzuriteContainer", "ConnectionStringType"],
    "cassandra": ["CassandraContainer"],
    "chroma": ["ChromaContainer"],
    "clickhouse": ["ClickHouseContainer"],
    "cockroachdb": ["CockroachDBContainer"],
    "cosmosdb": ["CosmosDBMongoEndpointContainer", "CosmosDBNoSQLEndpointContainer"],
    "db2": ["Db2Container"],
    "elasticsearch": ["ElasticSearchContainer"],
    "generic": ["ServerContainer", "SqlContainer"],
    "google": ["DatastoreContainer", "PubSubContainer"],
    "influxdb": ["InfluxDbContainer"],
    "influxdb1": ["InfluxDb1Container"],
    "influxdb2": ["InfluxDb2Container"],
    "k3s": ["K3SContainer"],
    "kafka": ["KafkaContainer", "RedpandaContainer", "kafka_config"],
    "keycloak": ["KeycloakContainer"],
    "localstack": ["LocalStackContainer"],
    "mailpit": ["MailpitContainer", "MailpitUser"],
    "memcached": ["MemcachedContainer", "MemcachedNotReady"],
    "milvus": ["MilvusContainer"],
    "minio": ["MinioContainer"],
    "mongodb": ["MongoDbContainer", "MongoDBAtlasLocalContainer"],
    "mqtt": ["MosquittoContainer"],
    "mssql": ["SqlServerContainer"],
    "mysql": ["MySqlContainer"],
    "nats": ["NatsContainer"],
    "neo4j": ["Neo4jContainer"],
    "nginx": ["NginxContainer"],
    "ollama": ["OllamaContainer", "OllamaModel"],
    "openfga": ["OpenFGAContainer"],
    "opensearch": ["OpenSearchContainer"],
    "oracle": ["OracleDbContainer"],
    "postgres": ["PostgresContainer"],
    "qdrant": ["QdrantContainer"],
    "rabbitmq": ["RabbitMqContainer"],
    "redis": ["AsyncRedisContainer", "PingWaitStrategy", "RedisContainer"],
    "registry": ["DockerRegistryContainer"],
    "scylla": ["ScyllaContainer"],
    "selenium": ["BrowserWebDriverContainer", "SeleniumVideoContainer", "get_image_name"],
    "sftp": ["SFTPContainer", "SFTPUser"],
    "trino": ["TrinoContainer"],
    "valkey": ["ValkeyContainer"],
    "vault": ["VaultContainer"],
    "weaviate": ["WeaviateContainer"],
}


def _fresh_import(mod: str):
    full_name = f"testcontainers.{mod}"
    sys.modules.pop(full_name, None)
    return importlib.import_module(full_name)


@pytest.mark.parametrize("mod,symbols", MODULES.items(), ids=MODULES.keys())
def test_deprecation_warning(mod, symbols):
    with pytest.warns(DeprecationWarning, match=f"testcontainers.community.{mod}"):
        _fresh_import(mod)


@pytest.mark.parametrize("mod,symbols", MODULES.items(), ids=MODULES.keys())
def test_symbols_exported(mod, symbols):
    imported = _fresh_import(mod)
    assert hasattr(imported, "__all__")
    for symbol in symbols:
        assert symbol in imported.__all__, f"{symbol} missing from testcontainers.{mod}.__all__"
        assert hasattr(imported, symbol), f"{symbol} not accessible on testcontainers.{mod}"
