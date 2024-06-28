:code:`testcontainers-generic` is a set of generic containers modules that can be used to creat containers.

.. autoclass:: testcontainers.generic.ServerContainer
.. title:: testcontainers.generic.ServerContainer

FastAPI container that is using :code:`ServerContainer`

.. doctest::

    >>> from testcontainers.generic import ServerContainer
    >>> from testcontainers.core.waiting_utils import wait_for_logs

    >>> with DockerImage(path="./modules/generic/tests/samples/fastapi", tag="fastapi-test:latest") as image:
    ...     with ServerContainer(port=80, image=image) as fastapi_server:
    ...         delay = wait_for_logs(fastapi_server, "Uvicorn running on http://0.0.0.0:80")
    ...         fastapi_server.get_api_url = lambda: fastapi_server._create_connection_url() + "/api/v1/"
    ...         client = fastapi_server.get_client()
    ...         response = client.get("/")
    ...         assert response.status_code == 200
    ...         assert response.json() == {"Status": "Working"}
