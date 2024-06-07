import pytest
from typing import Optional
from testcontainers.core.generic import ServerContainer

import re


@pytest.mark.parametrize("test_image_cleanup", [True, False])
@pytest.mark.parametrize("test_image_tag", [None, "custom-image:test"])
def test_srv_container(test_image_tag: Optional[str], test_image_cleanup: bool, check_for_image, port=9000):
    with ServerContainer(
        path="./core/tests/image_fixtures/python_server",
        port=port,
        tag=test_image_tag,
        image_cleanup=test_image_cleanup,
    ) as srv:
        image_short_id = srv.docker_image.short_id
        image_build_logs = srv.docker_image.get_logs()
        # check if dict is in any of the logs
        assert {"stream": f"Step 2/3 : EXPOSE {port}"} in image_build_logs, "Image logs mismatch"
        assert (port, None) in srv.ports.items(), "Port mismatch"
        with pytest.raises(NotImplementedError):
            srv.get_api_url()
        test_url = srv._create_connection_url()
        assert re.match(r"http://localhost:\d+", test_url), "Connection URL mismatch"

    check_for_image(image_short_id, test_image_cleanup)
