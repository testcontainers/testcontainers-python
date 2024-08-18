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

A more advance use-case, where we are using a FastAPI container that is using Redis container:

.. doctest::

    >>> from testcontainers.redis import RedisContainer
    >>> from testcontainers.generic import ServerContainer

    >>> with RedisContainer() as redis:
    ...     redis_port = redis.get_exposed_port(redis.port)
    ...     redis_host = redis.get_container_host_ip()

    ...     with DockerImage(path="./modules/generic/tests/samples/advance_1", tag="advance-1:latest") as image:
    ...         web_server = ServerContainer(port=80, image=image)
    ...         web_server.with_env(key="REDIS_HOST", value=redis_host)
    ...         web_server.with_env(key="REDIS_PORT", value=redis_port)

    ...         with web_server:
    ...             web_server.get_api_url = lambda: web_server._create_connection_url() + "/api/v1/"
    ...             client = web_server.get_client()

    ...             response = client.get("/")
    ...             assert response.status_code == 200, "Server request failed"
    ...             assert response.json() == {"Status": "ok"}

    ...             test_data = {"key": "test_key", "value": "test_value"}
    ...             response = client.post("/set", json=test_data)
    ...             assert response.status_code == 200, "Failed to set data"

    ...             response = client.get(f"/get/{test_data['key']}")
    ...             assert response.status_code == 200. "Failed to get data"
    ...             assert response.json() == {"key": test_data["key"], "value": test_data["value"]}
