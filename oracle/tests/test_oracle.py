import sqlalchemy
from testcontainers.oracle import OracleDbContainer


def test_docker_run_oracle():
    with OracleDbContainer() as oracledb:
        engine = sqlalchemy.create_engine(oracledb.get_connection_url())
        with engine.begin() as connection:
            test_val = 1
            result = connection.execute(sqlalchemy.text("SELECT {} FROM dual".format(test_val)))
            for row in result:
                assert row[0] == test_val
