import sqlalchemy

from testcontainers.mysql import MySqlContainer


def basic_example():
    config = MySqlContainer("mysql:8.3.0", dialect="pymysql")

    with config as mysql:
        connection_url = mysql.get_connection_url()

        engine = sqlalchemy.create_engine(connection_url)
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                print(f"MySQL version: {row[0]}")
