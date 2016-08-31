Database containers
===================

Allows to spin up docker database images such as MySQL, PostgreSQL, MariaDB and Oracle XE.

MySQL example
-------------

::

    config = MySqlContainer(username="user", password="secret", version="5.7")
    with config as mysql:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0] == '5.7.14'

It will spin up MySQL version 5.7. Then you can connect to database with credentials passed in constructor or just

call ``get_connection_url()`` method which returns sqlalchemy compatible url in format ``dialect+driver://username:password@host:port/database``.

PostgresSQL
-----------

Example of PostgresSQL database usage:

::

    postgres_container = PostgresContainer("user", "secret", version="9.5")
    with postgres_container as postgres:
        conn = psycopg2.connect(host=postgres.host_ip,
                                user=postgres.username,
                                password=postgres.password,
                                database=postgres.database)
        cur = conn.cursor()

        cur.execute("SELECT VERSION()")
        row = cur.fetchone()
        cur.close()

Connection set by using raw python ``psycopg2`` driver for Postgres.

MariaDB
-------

Maria DB is a fork of MySQL database, so the only difference with MySQL is the name of Docker container.

::

    mariadb_container = MariaDbContainer("test", "test")
    with mariadb_container as mariadb:
        conn = MySQLdb.connect(host=mariadb.host_ip,
                               user=mariadb.username,
                               passwd=mariadb.password,
                               db=mariadb.database)
        cur = conn.cursor()

        cur.execute("SELECT VERSION()")
        row = cur.fetchone()
        cur.close()

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
