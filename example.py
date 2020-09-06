import sqlalchemy
from testcontainers.mysql import MySqlContainer

with MySqlContainer('mysql:5.7.17') as mysql:
	engine = sqlalchemy.create_engine(mysql.get_connection_url())
	version, = engine.execute("select version()").fetchone()
	print(version)  # 5.7.17
