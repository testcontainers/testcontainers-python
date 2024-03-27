from testcontainers.chroma import ChromaContainer
import chromadb


def test_docker_run_chroma():
    with ChromaContainer(image="chromadb/chroma:0.4.24") as chroma:
        client = chromadb.HttpClient(host=chroma.get_config()["host"], port=chroma.get_config()["port"])
        col = client.get_or_create_collection("test")
        assert col.name == "test"
