import re
import pytest

from testcontainers.fastapi import FastAPIContainer


def test_fastapi_container():
    with FastAPIContainer(
        path="./modules/fastapi/tests/sample", port=80, tag="fastapi:test", image_cleanup=False
    ) as fastapi:
        assert fastapi.get_container_host_ip() == "localhost"
        assert fastapi.internal_port == 80
        assert re.match(r"http://localhost:\d+/api/v1/", fastapi.get_api_url())
        assert fastapi.get_client().get("/").status_code == 200
        assert fastapi.get_client().get("/").json() == {"Status": "Working"}


def test_fastapi_container_no_tag():
    with FastAPIContainer(path="./modules/fastapi/tests/sample", port=80, image_cleanup=False) as fastapi:
        assert fastapi.get_client().get("/").status_code == 200
        assert fastapi.get_client().get("/").json() == {"Status": "Working"}


def test_fastapi_container_no_port():
    with pytest.raises(TypeError):
        with FastAPIContainer(path="./modules/fastapi/tests/sample", tag="fastapi:test", image_cleanup=False):
            pass


def test_fastapi_container_no_path():
    with pytest.raises(TypeError):
        with FastAPIContainer(port=80, tag="fastapi:test", image_cleanup=True):
            pass
