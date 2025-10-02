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
    ...     redis_container_port = redis.port
    ...     redis_container_ip_address = redis.get_docker_client().bridge_ip(redis._container.id)

    ...     with DockerImage(path="./modules/generic/tests/samples/advance_1", tag="advance-1:latest") as image:
    ...         web_server = ServerContainer(port=80, image=image)
    ...         web_server.with_env(key="REDIS_HOST", value=redis_container_ip_address)
    ...         web_server.with_env(key="REDIS_PORT", value=redis_container_port)

    ...         with web_server:
    ...             web_server.get_api_url = lambda: web_server._create_connection_url()
    ...             client = web_server.get_client()

    ...             response = client.get("/")
    ...             assert response.status_code == 200, "Server request failed"
    ...             assert response.json() == {"Status": "ok"}

    ...             test_data = {"key": "test_key", "value": "test_value"}
    ...             response = client.post("/set", params=test_data)
    ...             assert response.status_code == 200, "Failed to set data"

    ...             response = client.get(f"/get/{test_data['key']}")
    ...             assert response.status_code == 200, "Failed to get data"
    ...             assert response.json() == {"key": test_data["key"], "value": test_data["value"]}

.. autoclass:: testcontainers.generic.SqlContainer
.. title:: testcontainers.generic.SqlContainer

SQL container that is using :code:`SqlContainer`

.. doctest::

    >>> from testcontainers.generic import SqlContainer
    >>> from sqlalchemy import text
    >>> import sqlalchemy

    >>> with SqlContainer(image="postgres:15-alpine", port=5432, username="test", password="test", dbname="test") as postgres:
    ...     engine = sqlalchemy.create_engine(postgres.get_connection_url())
    ...     with engine.connect() as conn:
    ...         result = conn.execute(text("SELECT 1"))
    ...         assert result.scalar() == 1
