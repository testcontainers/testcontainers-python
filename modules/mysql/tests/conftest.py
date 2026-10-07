from pathlib import Path
import pytest
import docker


# build a custom MySQL image
@pytest.fixture(scope="session")
def mysql_custom_image() -> str:
    tag = "mysql-custom:8.0"
    client = docker.from_env()
    DOCKERFILE_PATH = (Path(__file__).parent / "seeds").absolute().as_posix()
    image, _ = client.images.build(path=DOCKERFILE_PATH, tag=tag)
    return tag
