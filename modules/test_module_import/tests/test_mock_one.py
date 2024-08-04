import httpx

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.image import DockerImage
from testcontainers.test_module_import import NewSubModuleContainer


def test_like_doctest():
    with DockerImage(path="./modules/generic/tests/samples/python_server", tag="test-new-mod:latest") as image:
        with NewSubModuleContainer(port=9000, image=image) as new_mod:
            url = new_mod._create_connection_url()
            response = httpx.get(f"{url}", timeout=5)
            assert response.status_code == 200, "Response status code is not 200"
            assert new_mod.additional_capability() == "NewSubModuleContainer"
