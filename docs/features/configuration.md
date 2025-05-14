# Custom configuration

.....

## Docker host detection

_Testcontainers for Go_ will attempt to detect the Docker environment and configure everything to work automatically.

However, sometimes customization is required. _Testcontainers for Go_ will respect the following order:

1. Read the **tc.host** property in the `~/.testcontainers.properties` file. E.g. `tc.host=tcp://my.docker.host:1234`

2. Read the **DOCKER_HOST** environment variable. E.g. `DOCKER_HOST=unix:///var/run/docker.sock`
   See [Docker environment variables](https://docs.docker.com/engine/reference/commandline/cli/#environment-variables) for more information.

3. Read the Go context for the **DOCKER_HOST** key. E.g. `ctx.Value("DOCKER_HOST")`. This is used internally for the library to pass the Docker host to the resource reaper.

4. Read the default Docker socket path, without the unix schema. E.g. `/var/run/docker.sock`

5. Read the **docker.host** property in the `~/.testcontainers.properties` file. E.g. `docker.host=tcp://my.docker.host:1234`

6. Read the rootless Docker socket path, checking in the following alternative locations:

   1. `${XDG_RUNTIME_DIR}/.docker/run/docker.sock`.
   2. `${HOME}/.docker/run/docker.sock`.
   3. `${HOME}/.docker/desktop/docker.sock`.
   4. `/run/user/${UID}/docker.sock`, where `${UID}` is the user ID of the current user.

7. The library panics if none of the above are set, meaning that the Docker host was not detected.
