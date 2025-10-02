import sqlalchemy

from testcontainers import cratedb

with cratedb.CrateDBContainer("crate:latest", ports={4200: None, 5432: None}) as container:
    engine = sqlalchemy.create_engine(container.get_connection_url())
    with engine.begin() as conn:
        result = conn.execute(sqlalchemy.text("select version()"))
        version = result.fetchone()
