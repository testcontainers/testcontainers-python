Database containers
===================

Allows to spin up docker database images such as MySQL, PostgreSQL, MariaDB and Oracle XE.

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
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select 1 from dual")

It uses **https://hub.docker.com/r/wnameless/oracle-xe-11g/** docker image.

Connection detail for Oracle DB.

::

    hostname: localhost
    port: 49161
    sid: xe
    username: system
    password: oracle
