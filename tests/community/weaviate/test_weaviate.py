from testcontainers.weaviate import WeaviateContainer
import weaviate


def test_docker_run_weaviate():
    with WeaviateContainer() as container:
        client = weaviate.connect_to_custom(
            http_host=container.get_http_host(),
            http_port=container.get_http_port(),
            http_secure=container.get_http_secure(),
            grpc_host=container.get_grpc_host(),
            grpc_port=container.get_grpc_port(),
            grpc_secure=container.get_grpc_secure(),
        )

        meta = client.get_meta()
        assert len(meta.get("version")) > 0

        client.close()


def test_docker_run_weaviate_with_client():
    with WeaviateContainer() as container:
        with container.get_client() as client:
            assert client.is_live()

            meta = client.get_meta()
            assert len(meta.get("version")) > 0


def test_docker_run_weaviate_with_modules():
    enable_modules = [
        "backup-filesystem",
        "text2vec-openai",
        "text2vec-cohere",
        "text2vec-huggingface",
        "generative-openai",
    ]
    with WeaviateContainer(
        env_vars={
            "ENABLE_MODULES": ",".join(enable_modules),
            "BACKUP_FILESYSTEM_PATH": "/tmp/backups",
        }
    ) as container:
        with container.get_client() as client:
            assert client.is_live()

            meta = client.get_meta()
            assert len(meta.get("version")) > 0

            modules = meta.get("modules")
            assert len(modules) == len(enable_modules)

            for name in enable_modules:
                assert len(modules[name]) > 0
