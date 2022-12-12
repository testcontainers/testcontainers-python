import pytest
import sqlalchemy
# import time

from testcontainers.postgres import PostgresContainer

# >= v14 use scram-sha-256 by default, so test changing to MD5
@pytest.mark.parametrize('version', ['14.5', '15.1'])
def test_docker_run_postgresql_md5(version):
    _docker_run_postgresql_test(version, "md5")


# >= v10 to <v14 use md5 by default, so test changing to scram-sha-256.
@pytest.mark.parametrize('version', ['12.8', '13.5'])
def test_docker_run_postgresql_scram(version):
    _docker_run_postgresql_test(version, "scram-sha-256")


def _docker_run_postgresql_test(version, method):
    test_user = 'bob' + method[:3]
    with PostgresContainer(
        image=f'postgres:{version}',
        user=test_user,
        password='hi bob',
        initdb_args=f'--auth-host={method}',
        host_auth_method=f'{method}'
    ).with_bind_ports(5432, 45432) as postgres:
        engine = sqlalchemy.create_engine(postgres.get_connection_url())
        with engine.connect() as conn:
            test_query = "SELECT rolname, rolpassword FROM pg_authid "\
                         f" WHERE rolname = '{test_user}';"
            result = conn.execute(test_query)
            name, password = result.fetchone()

            assert name == test_user

            # password_method = str(password[:len(method)])
            # password_method = password_method.lower()
            assert method == str(password[:len(method)]).lower()
