import json

from neo4j import GraphDatabase

from testcontainers.neo4j import Neo4jContainer


def basic_example():
    with Neo4jContainer() as neo4j:
        # Get connection parameters
        host = neo4j.get_container_host_ip()
        port = neo4j.get_exposed_port(neo4j.port)
        username = neo4j.username
        password = neo4j.password

        # Create Neo4j driver
        driver = GraphDatabase.driver(f"bolt://{host}:{port}", auth=(username, password))
        print("Connected to Neo4j")

        # Create session
        with driver.session() as session:
            # Create nodes
            create_nodes_query = """
            CREATE (p1:Person {name: 'Alice', age: 30})
            CREATE (p2:Person {name: 'Bob', age: 35})
            CREATE (p3:Person {name: 'Charlie', age: 25})
            CREATE (c1:Company {name: 'Tech Corp', founded: 2000})
            CREATE (c2:Company {name: 'Data Inc', founded: 2010})
            """
            session.run(create_nodes_query)
            print("Created nodes")

            # Create relationships
            create_rels_query = """
            MATCH (p1:Person {name: 'Alice'}), (c1:Company {name: 'Tech Corp'})
            CREATE (p1)-[:WORKS_AT {since: 2015}]->(c1)

            MATCH (p2:Person {name: 'Bob'}), (c1:Company {name: 'Tech Corp'})
            CREATE (p2)-[:WORKS_AT {since: 2018}]->(c1)

            MATCH (p3:Person {name: 'Charlie'}), (c2:Company {name: 'Data Inc'})
            CREATE (p3)-[:WORKS_AT {since: 2020}]->(c2)

            MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
            CREATE (p1)-[:KNOWS {since: 2016}]->(p2)
            """
            session.run(create_rels_query)
            print("Created relationships")

            # Query nodes
            query_nodes = """
            MATCH (n)
            RETURN n
            """
            result = session.run(query_nodes)
            print("\nAll nodes:")
            for record in result:
                node = record["n"]
                print(json.dumps({"labels": list(node.labels), "properties": dict(node)}, indent=2))

            # Query relationships
            query_rels = """
            MATCH (n)-[r]->(m)
            RETURN n, r, m
            """
            result = session.run(query_rels)
            print("\nAll relationships:")
            for record in result:
                print(
                    json.dumps(
                        {
                            "from": {"labels": list(record["n"].labels), "properties": dict(record["n"])},
                            "relationship": {"type": record["r"].type, "properties": dict(record["r"])},
                            "to": {"labels": list(record["m"].labels), "properties": dict(record["m"])},
                        },
                        indent=2,
                    )
                )

            # Create index
            create_index = """
            CREATE INDEX person_name IF NOT EXISTS
            FOR (p:Person)
            ON (p.name)
            """
            session.run(create_index)
            print("\nCreated index on Person.name")

            # Query using index
            query_indexed = """
            MATCH (p:Person)
            WHERE p.name = 'Alice'
            RETURN p
            """
            result = session.run(query_indexed)
            print("\nQuery using index:")
            for record in result:
                node = record["p"]
                print(json.dumps({"labels": list(node.labels), "properties": dict(node)}, indent=2))

            # Create constraint
            create_constraint = """
            CREATE CONSTRAINT company_name IF NOT EXISTS
            FOR (c:Company)
            REQUIRE c.name IS UNIQUE
            """
            session.run(create_constraint)
            print("\nCreated constraint on Company.name")

            # Create full-text index
            create_ft_index = """
            CALL db.index.fulltext.createNodeIndex(
                "personSearch",
                ["Person"],
                ["name"]
            )
            """
            session.run(create_ft_index)
            print("Created full-text index")

            # Query using full-text index
            query_ft = """
            CALL db.index.fulltext.queryNodes(
                "personSearch",
                "Alice"
            )
            YIELD node
            RETURN node
            """
            result = session.run(query_ft)
            print("\nFull-text search results:")
            for record in result:
                node = record["node"]
                print(json.dumps({"labels": list(node.labels), "properties": dict(node)}, indent=2))

            # Create stored procedure
            create_proc = """
            CALL apoc.custom.asProcedure(
                'getCompanyEmployees',
                'MATCH (p:Person)-[:WORKS_AT]->(c:Company {name: $companyName})
                 RETURN p',
                'READ',
                [['p', 'NODE']],
                [['companyName', 'STRING']]
            )
            """
            session.run(create_proc)
            print("\nCreated stored procedure")

            # Call stored procedure
            call_proc = """
            CALL custom.getCompanyEmployees('Tech Corp')
            YIELD p
            RETURN p
            """
            result = session.run(call_proc)
            print("\nStored procedure results:")
            for record in result:
                node = record["p"]
                print(json.dumps({"labels": list(node.labels), "properties": dict(node)}, indent=2))

            # Create trigger
            create_trigger = """
            CALL apoc.trigger.add(
                'setTimestamp',
                'UNWIND apoc.trigger.nodesByLabel($assignedLabels, "Person") AS n
                 SET n.updated_at = datetime()',
                {phase: 'after'}
            )
            """
            session.run(create_trigger)
            print("\nCreated trigger")

            # Test trigger
            test_trigger = """
            MATCH (p:Person {name: 'Alice'})
            SET p.age = 31
            RETURN p
            """
            result = session.run(test_trigger)
            print("\nTrigger test results:")
            for record in result:
                node = record["p"]
                print(json.dumps({"labels": list(node.labels), "properties": dict(node)}, indent=2))

            # Clean up
            cleanup = """
            MATCH (n)
            DETACH DELETE n
            """
            session.run(cleanup)
            print("\nCleaned up database")

        driver.close()


if __name__ == "__main__":
    basic_example()
