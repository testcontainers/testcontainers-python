import sqlalchemy
from sqlalchemy import text

from testcontainers.community.cratedb import CrateDBContainer


def basic_example():
    with CrateDBContainer("crate:latest") as cratedb:
        # CrateDB speaks the SQLAlchemy `crate://` dialect over its HTTP interface.
        engine = sqlalchemy.create_engine(cratedb.get_connection_url())

        with engine.begin() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS summits (
                    name TEXT PRIMARY KEY,
                    height INT
                )
            """)
            )
            print("Created table")

            conn.execute(
                text("INSERT INTO summits (name, height) VALUES (:name, :height)"),
                [
                    {"name": "Mont Blanc", "height": 4808},
                    {"name": "Monte Rosa", "height": 4634},
                    {"name": "Dom", "height": 4545},
                ],
            )
            # CrateDB is eventually consistent for reads; refresh to read-your-writes.
            conn.execute(text("REFRESH TABLE summits"))
            print("Inserted data")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT name, height FROM summits ORDER BY height DESC"))
            print("\nQuery results:")
            for row in result:
                print(f"Name: {row.name}, Height: {row.height}")


if __name__ == "__main__":
    basic_example()
