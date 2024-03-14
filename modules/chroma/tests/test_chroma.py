from testcontainers.chroma import ChromaContainer


def test_docker_run_chroma():
    with ChromaContainer(image="chromadb/chroma:0.4.24") as chroma:
        client = chroma.get_client()
        col = client.get_or_create_collection("test")
        assert col.name == "test"
