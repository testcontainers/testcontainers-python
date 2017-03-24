.. python-testcontainers documentation master file, created by
   sphinx-quickstart on Mon Aug 22 13:39:46 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-testcontainers's documentation!
=================================================

**python-testcontainers** provides capabilities to spin up a docker containers for test purposes would that be a database, Selenium web browser or any other cotainer.

Currently available features:

- Selenium Grid containers
- Selenim Standalone containers
- MySql db container
- PostgreSQL db container
- Generic Docker containers

Installation
------------

The testcontainers module is available from PyPi at:

https://pypi.python.org/pypi/testcontainers
and can be installed using pip.

::

   pip install testcontainers


Compatibility
-------------

Tested with Docker for Ubuntu, Mac and Windows.

Was not tested with Docker-machine and Docker Toolbox.

Usage modes
-----------

.. toctree::
   :maxdepth: 1

   Database containers <database>
   Selenium containers <selenium>
   Generic containers <generic> 

