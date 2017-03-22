# testcontainers-python

![testcontainer](http://robertwdempsey.com/wp-content/uploads/2015/10/docker-python.png)

[![Build Status](https://travis-ci.org/SergeyPirogov/testcontainers-python.svg?branch=master)](https://travis-ci.org/SergeyPirogov/testcontainers-python) [![PyPI](https://img.shields.io/pypi/v/testcontainers.svg?style=flat-square)](https://pypi.python.org/pypi/testcontainers)



Python port for testcontainers-java that allows using docker containers for functional and/or integration testing.

Testcontainers-python provides capabilities to spin up a docker containers for test purposes would that be a database, Selenium web browser or any other cotainer.

Currently available features:

* Selenium Grid containers
* Selenium Standalone containers
* MySql Db container
* MariaDb container
* PostgreSQL Db container
* Generic docker containers

### Quick start

Installation
------------

The **testcontainers** module is available from PyPi at:

* https://pypi.python.org/pypi/testcontainers

and can be installed using ``pip``.

    pip install testcontainers

Database containers
-------------------

Allows to spin up docker database images such as MySQL, PostgreSQL, MariaDB and Oracle XE.

MySQL example
-------------

        config = MySqlContainer('mysql:5.7.17')
        with config as mysql:
            e = sqlalchemy.create_engine(mysql.get_connection_url())
            result = e.execute("select version()")
            
It will spin up MySQL version 5.7. Then you can connect to database using ``get_connection_url()`` method which returns sqlalchemy compatible url in format ``dialect+driver://username:password@host:port/database``.

PostgresSQL
-----------

Example of PostgresSQL database usage:

        postgres_container = PostgresContainer("postgres:9.5")
        with postgres_container as postgres:
            e = sqlalchemy.create_engine(postgres.get_connection_url())
            result = e.execute("select version()")
            
Connection set by using raw python ``psycopg2`` driver for Postgres.

MariaDB
-------

Maria DB is a fork of MySQL database, so the only difference with MySQL is the name of Docker container.

        mariadb_container = MariaDbContainer("mariadb:latest")
        with mariadb_container as mariadb:
            e = sqlalchemy.create_engine(mariadb.get_connection_url())
            result = e.execute("select version()")
                
Oracle XE
---------

    oracle = OracleDbContainer()

    with oracle:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select 1 from dual")

It uses **https://hub.docker.com/r/wnameless/oracle-xe-11g/** docker image.

Connection detail for Oracle DB.

    hostname: localhost
    port: 49161
    sid: xe
    username: system
    password: oracle                
    
Generic Database containers
---------------------------

Generally you are able to run any database container, but you need to configure it yourself.

Mongo example:

        mongo_container = DockerContainer("mongo:latest")
        mongo_container.expose_port(27017, 27017)

        with mongo_container:
            @wait_container_is_ready()
            def connect():
                return MongoClient("mongodb://{}:{}".format(mongo_container.get_container_host_ip(),
                                                        mongo_container.get_exposed_port(27017)))

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