"""
ArangoDB Container Tests
"""
import pytest
from arango import ArangoClient
from arango.exceptions import DatabaseCreateError, ServerVersionError
from testcontainers.arangodb import ArangoDbContainer

ARANGODB_IMAGE_NAME = 'arangodb'


def arango_test_ops(arango_client, expeced_version, db_user='root', db_pass=''):
    """
    Basic ArangoDB operations to test DB really up and running.
    """
    students_to_insert_cnt = 3

    # Taken from https://github.com/ArangoDB-Community/python-arango/blob/main/README.md
    # Connect to "_system" database as root user.
    sys_db = arango_client.db("_system", username=db_user, password=db_pass)
    assert sys_db.version() == expeced_version

    # Create a new database named "test".
    sys_db.create_database("test")

    # Connect to "test" database as root user.
    database = arango_client.db("test", username=db_user, password=db_pass)

    # Create a new collection named "students".
    students = database.create_collection("students")

    # Add a hash index to the collection.
    students.add_hash_index(fields=["name"], unique=True)

    # Insert new documents into the collection. (students_to_insert_cnt)
    students.insert({"name": "jane", "age": 39})
    students.insert({"name": "josh", "age": 18})
    students.insert({"name": "judy", "age": 21})

    # Execute an AQL query and iterate through the result cursor.
    cursor = database.aql.execute("FOR doc IN students RETURN doc")
    student_names = [document["name"] for document in cursor]

    assert len(student_names) == students_to_insert_cnt


def test_docker_run_arango():
    """
    Test ArangoDB container with default settings.
    """
    image_version = '3.9.1'
    image = f'{ARANGODB_IMAGE_NAME}:{image_version}'
    arango_db_root_password = 'passwd'

    with ArangoDbContainer(image) as arango:
        client = ArangoClient(hosts=arango.get_connection_url())

        # Test invalid auth
        with pytest.raises(DatabaseCreateError):
            sys_db = client.db("_system", username="root", password='notTheRightPass')
            sys_db.create_database("test")

        arango_test_ops(
            arango_client=client,
            expeced_version=image_version,
            db_pass=arango_db_root_password)


def test_docker_run_arango_without_auth():
    """
    Test ArangoDB container with ARANGO_NO_AUTH var set.
    """
    image_version = '3.9.1'
    image = f'{ARANGODB_IMAGE_NAME}:{image_version}'

    with ArangoDbContainer(image, arango_no_auth=True) as arango:
        client = ArangoClient(hosts=arango.get_connection_url())

        arango_test_ops(
            arango_client=client,
            expeced_version=image_version,
            db_pass='')


def test_docker_run_arango_older_version():
    """
    Test ArangoDB container with older tag/version.
    the idea behind it hides in the logic of arangodb._connect() ->
    Where it waits the container to sign "ready for business" -
    If someone will change the logic in the future
    we must verify older image tags still supported. (without that logic - we'll face race issues
    where we try to create & populate DB when ArangoDB not really ready.
    """
    image_version = '3.1.7'
    image = f'{ARANGODB_IMAGE_NAME}:{image_version}'

    with ArangoDbContainer(image, arango_no_auth=True) as arango:
        client = ArangoClient(hosts=arango.get_connection_url())

        arango_test_ops(
            arango_client=client,
            expeced_version=image_version,
            db_pass='')


def test_docker_run_arango_random_root_password():
    """
    Test ArangoDB container with ARANGO_RANDOM_ROOT_PASSWORD var set.
    """
    image_version = '3.9.1'
    image = f'{ARANGODB_IMAGE_NAME}:{image_version}'
    arango_db_root_password = 'passwd'

    with ArangoDbContainer(image, arango_random_root_password=True) as arango:
        client = ArangoClient(hosts=arango.get_connection_url())

        # Test invalid auth (we don't know the password in random mode)
        with pytest.raises(ServerVersionError):
            sys_db = client.db("_system", username='root', password=arango_db_root_password)
            assert sys_db.version() == image_version
