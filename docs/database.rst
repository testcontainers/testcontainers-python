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

Generic Database containers
---------------------------

Generally you are able to run any database container, but you need to configure it yourself.

Mongo example:

::

    mongo_container = DockerContainer(image_name="mongo",
                                      version="latest",
                                      container_name="mongodb")
    mongo_container.bind_ports(27017, 27017)

    with mongo_container:
        @wait_container_is_ready()
        def connect():
            return MongoClient("mongodb://0.0.0.0:27017")

        db = connect().primer
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

