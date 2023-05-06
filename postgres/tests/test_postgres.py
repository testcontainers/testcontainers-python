from testcontainers.postgres import PostgresContainer


def test_docker_run_postgres():
    # https://www.postgresql.org/support/versioning/
    supported_versions = ["11", "12", "13", "14", "latest"]

    for version in supported_versions:
        postgres_container = PostgresContainer(f"postgres:{version}")
        with postgres_container as postgres:
            status, msg = postgres.exec(
                f"pg_isready -hlocalhost -p{postgres.port} -U{postgres.username}"
            )

            assert msg.decode("utf-8").endswith("accepting connections\n")
            assert status == 0
