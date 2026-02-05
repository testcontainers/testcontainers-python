import pytest
import re
import sqlalchemy

from testcontainers.core.utils import is_arm
from testcontainers.mysql import MySqlContainer

# imports for issue 707
from testcontainers.core.waiting_utils import wait_for_logs
from types import MethodType


# Testcontainers-Python 4.8.2 / main branch: This method gets the following error:
# E   TimeoutError: Container did not emit logs satisfying predicate in 120.000 seconds
@pytest.mark.skipif(is_arm(), reason="mysql container not available for ARM")
def test_docker_run_mysql_8_custom(mysql_custom_image):
    config = MySqlContainer(mysql_custom_image)
    with config as mysql:
        engine = sqlalchemy.create_engine(mysql.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select * from stuff"))
            assert len(list(result)) == 4, "Should have gotten all the stuff"


# Testcontainers-Python 4.8.2 / main branch: This method works
@pytest.mark.skipif(is_arm(), reason="mysql container not available for ARM")
def test_docker_run_mysql_8_custom_overwrite_connect_method(mysql_custom_image):
    config = MySqlContainer(mysql_custom_image)

    # 20241025 patch the _connect method to change the wait_for_logs regex
    def _connect(self) -> None:
        wait_for_logs(
            self,
            re.compile(".* ready for connections.* ready for connections.*", flags=re.DOTALL | re.MULTILINE).search,
        )

    config._connect = MethodType(_connect, config)

    with config as mysql:
        mysql_url = mysql.get_connection_url()
        engine = sqlalchemy.create_engine(mysql_url)
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select * from stuff"))
            assert len(list(result)) == 4, "Should have gotten all the stuff"
