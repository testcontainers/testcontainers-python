.. autoclass:: testcontainers.redis.RedisContainer



Creates a container with the `redis <https://hub.docker.com/_/redis>`_ image
and waits for the container to accept connections.

Defaults to the latest release of redis, and supports version 6.0+.
For older versions, use the generic DockerContainer class from `testcontainers-core`.
