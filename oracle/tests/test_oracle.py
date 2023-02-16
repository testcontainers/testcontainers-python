import sqlalchemy
import pytest
from testcontainers.oracle import OracleDbContainer


@pytest.mark.skip(reason="needs oracle client libraries unavailable on Travis")
def test_docker_run_oracle():
    versions = {'Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production',
                'PL/SQL Release 11.2.0.2.0 - Production',
                'CORE\t11.2.0.2.0\tProduction',
                'TNS for Linux: Version 11.2.0.2.0 - Production',
                'NLSRTL Version 11.2.0.2.0 - Production'}
    with OracleDbContainer() as oracledb:
        engine = sqlalchemy.create_engine(oracledb.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select * from V$VERSION"))
            assert {row[0] for row in result} == versions
