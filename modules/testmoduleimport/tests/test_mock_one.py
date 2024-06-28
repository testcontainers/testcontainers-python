import httpx

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.image import DockerImage
from testcontainers.testmoduleimport import NewSubModuleContainer


def test_like_doctest():
    with DockerImage(path="./modules/generic/tests/samples/python_server", tag="test-srv:latest") as image:
        with NewSubModuleContainer(port=9000, image=image) as srv:
            assert srv.print_mock() == "NewSubModuleContainer"
            url = srv._create_connection_url()
            response = httpx.get(f"{url}", timeout=5)
            assert response.status_code == 200, "Response status code is not 200"
            _ = wait_for_logs(srv, "GET / HTTP/1.1")
