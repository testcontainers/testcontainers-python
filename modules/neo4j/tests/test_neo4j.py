from testcontainers.neo4j import Neo4jContainer


def test_docker_run_neo4j_latest():
    with Neo4jContainer() as neo4j, neo4j.get_driver() as driver, driver.session() as session:
        result = session.run(
            """
            CALL dbms.components()
            YIELD name, versions, edition
            UNWIND versions as version
            RETURN name, version, edition
            """
        )
        record = result.single()
        assert record["name"].startswith("Neo4j")
