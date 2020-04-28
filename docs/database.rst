Database containers
===================

Allows to spin up docker database images such as MySQL, PostgreSQL, MariaDB, Oracle XE and MongoDb.

MySQL example
-------------

::

    def test_docker_run_mysql():
        config = MySqlContainer('mysql:5.7.17')
        with config as mysql:
            e = sqlalchemy.create_engine(mysql.get_connection_url())
            result = e.execute("select version()")

It will spin up MySQL version 5.7. Then you can connect to database with credentials passed in constructor or just

call ``get_connection_url()`` method which returns sqlalchemy compatible url in format ``dialect+driver://username:password@host:port/database``.

PostgresSQL
-----------

Example of PostgresSQL database usage:

::

    def test_docker_run_postgress():
        postgres_container = PostgresContainer("postgres:9.5")
        with postgres_container as postgres:
            e = sqlalchemy.create_engine(postgres.get_connection_url())
            result = e.execute("select version()")

Connection set by using raw python ``psycopg2`` driver for Postgres.

MariaDB
-------

Maria DB is a fork of MySQL database, so the only difference with MySQL is the name of Docker container.

::

    def test_docker_run_mariadb():
        mariadb_container = MariaDbContainer("mariadb:latest")
        with mariadb_container as mariadb:
            e = sqlalchemy.create_engine(mariadb.get_connection_url())
            result = e.execute("select version()")

Oracle XE
---------

::

    oracle = OracleDbContainer()

    with oracle:
        e = sqlalchemy.create_engine(oracle.get_connection_url())
        result = e.execute("select 1 from dual")

It uses **https://hub.docker.com/r/wnameless/oracle-xe-11g-r2/** docker image.

Necessary to use it:

- ``cx_Oracle``
- `Oracle client libraries <https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html>`_

::

    hostname: localhost
    port: 49161
    sid: xe
    username: system
    password: oracle

Elasticsearch
-------------

::

    es = ElasticSearchContainer()
    with es:
        es.get_url()  # gives you the http URL to connect to Elasticsearch

MongoDb
-----------

Example of MongoDb database usage:

::

    def test_docker_run_mongodb():
        mongo_container = MongoDbContainer("mongo:latest")
        with mongo_container as mongo:
            db = mongo.get_connection_client().test
            result = db.restaurants.insert_one(
                {
                    "address": {
                        "street": "2 Avenue",
                        "zipcode": "10075",
                        "building": "1480",
                        "coord": [-73.9557413, 40.7720266]
                    },
                    "borough": "Manhattan",
                    "cuisine": "Italian",
                    "name": "Vella",
                    "restaurant_id": "41704620"
                }
            )
            print(result.inserted_id)
            cursor = db.restaurants.find({"borough": "Manhattan"})
            for document in cursor:
                print(document)

Connection is made using pymongo package and MongoClient class.
Alternatively, you can use get_connection_url method to use the driver that better fits for your use case.

Microsoft SQL Server
--------------------

::

    mssql = SqlServerContainer()

    with mssql:
        e = sqlalchemy.create_engine(mssql.get_connection_url())
        result = e.execute("select @@VERSION")

It uses the Microsoft-provided Docker image and requires `ODBC Driver 17 for SQL Server
<https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server>`_.
