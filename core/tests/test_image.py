import pytest
from testcontainers.core.image import DockerImage


def test_docker_image_from_dockerfile():
    image = DockerImage().from_dockerfile(path="core/tests/", tag="testcontainers/test-image")

    assert image.exists("testcontainers/test-image") == True

    retrieved_image = image.get("testcontainers/test-image")

    assert retrieved_image.id == image.id
    assert retrieved_image.short_id == image.short_id
    assert retrieved_image.tags == image.tags

    image.remove(force=True)

    assert image.exists("testcontainers/test-image") == False


def test_docker_image_from_image():
    image = DockerImage().from_image(repository="alpine")

    assert image.exists("alpine") == True

    retrieved_image = image.get("alpine")

    assert retrieved_image.id == image.id
    assert retrieved_image.short_id == image.short_id
    assert retrieved_image.tags == image.tags

    image.remove(force=True)

    assert image.exists("alpine") == False
