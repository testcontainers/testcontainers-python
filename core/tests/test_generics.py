import re
from pathlib import Path
from typing import Optional

import pytest
from httpx import get

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.image import DockerImage
from testcontainers.core.generic import ServerContainer

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("test_image_cleanup", [True, False])
@pytest.mark.parametrize("test_image_tag", [None, "custom-image:test"])
def test_srv_container(test_image_tag: Optional[str], test_image_cleanup: bool, check_for_image, port=9000):
    with (
        DockerImage(
            path=TEST_DIR / "image_fixtures/python_server",
            tag=test_image_tag,
            clean_up=test_image_cleanup,
            #
        ) as docker_image,
        ServerContainer(port=port, image=docker_image) as srv,
    ):
        image_short_id = docker_image.short_id
        image_build_logs = docker_image.get_logs()
        # check if dict is in any of the logs
        assert {"stream": f"Step 2/3 : EXPOSE {port}"} in image_build_logs, "Image logs mismatch"
        assert (port, None) in srv.ports.items(), "Port mismatch"
        with pytest.raises(NotImplementedError):
            srv.get_api_url()
        test_url = srv._create_connection_url()
        assert re.match(r"http://localhost:\d+", test_url), "Connection URL mismatch"

    check_for_image(image_short_id, test_image_cleanup)


def test_like_doctest():
    with DockerImage(path=TEST_DIR / "image_fixtures/python_server", tag="test-srv:latest") as image:
        with ServerContainer(port=9000, image=image) as srv:
            url = srv._create_connection_url()
            response = get(f"{url}", timeout=5)
            assert response.status_code == 200, "Response status code is not 200"
            delay = wait_for_logs(srv, "GET / HTTP/1.1")
            print(delay)
