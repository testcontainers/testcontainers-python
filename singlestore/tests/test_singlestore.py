import sqlalchemy

from testcontainers.singlestore import SingleStoreContainer


def test_docker_run_singlestore():
    with SingleStoreContainer(
            license_key=('BGE5YzE5NTdmN2I1NDQ4MjhhNTQ0MTM4YWQ4Y2Q5ZWNiAAAAAAA'
                         'AAAAEAAAAAAAAAAwwNQIYKbH2LOLeT189H+nBdRagLdLboVuJTs'
                         'gJAhkAtSepSZkq0Zn4FDVtvZyASWzovR2OeeyiAA==')
    ) as singlestore:
        engine = sqlalchemy.create_engine(singlestore.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    'select 1'
                )
            )
            assert result.mappings().all() == [{'1': 1}]
