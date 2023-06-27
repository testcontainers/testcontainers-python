.. autoclass:: testcontainers.nginx.NginxContainer

Creates a container with the `nginx <https://hub.docker.com/_/nginx/>`_ image
and waits for the container to accept connections.

Defaults to the latest release of nginx, and supports version 1.20+.
For older versions, use the generic DockerContainer class from `testcontainers-core`.
