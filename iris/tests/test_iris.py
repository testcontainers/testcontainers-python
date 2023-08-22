import sqlalchemy
from testcontainers.iris import IRISContainer


def test_docker_run_iris():
    iris_container = IRISContainer("intersystemsdc/iris-community:2023.1.1.380.0-zpm")
    with iris_container as iris:
        engine = sqlalchemy.create_engine(iris.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select $zversion"))
            for row in result:
                assert "2023.1.1 (Build 380U)" in row[0]
