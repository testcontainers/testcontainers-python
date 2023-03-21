import pytest
import tempfile
import sqlalchemy
from testcontainers.core.utils import is_arm
from testcontainers.db2 import Db2Container


@pytest.mark.skipif(is_arm(), reason='ibm_db_sa adapter not compatible with ARM64')
def test_docker_run_db2():
    with tempfile.TemporaryDirectory() as tempdir:
        config = Db2Container("ibmcom/db2:11.5.7.0", privileged=True, platform="linux/amd64")
        with config.with_volume_mapping(tempdir, "/database", mode="rw") as db2:
            engine = sqlalchemy.create_engine(db2.get_connection_url())
            with engine.connect() as conn:
                query = sqlalchemy.text("SELECT SERVICE_LEVEL FROM SYSIBMADM.ENV_INST_INFO")
                result = conn.execute(query)
                version = result.scalar()
                assert version == "DB2 v11.5.7.0"
