# Copying Data into Containers

Testcontainers-Python provides several ways to copy data into containers. This is essential for setting up test data, configuration files, or any other files needed for your tests.

## Basic File Copy

The simplest way to copy a file is using the `copy_file_to_container` method:

```python
from testcontainers.generic import GenericContainer

with GenericContainer("alpine:latest") as container:
    # Copy a single file
    container.copy_file_to_container(
        local_path="path/to/local/file.txt",
        container_path="/path/in/container/file.txt"
    )
```

## Copying Multiple Files

You can copy multiple files at once:

```python
with GenericContainer("alpine:latest") as container:
    # Copy multiple files
    container.copy_files_to_container([
        ("path/to/local/file1.txt", "/path/in/container/file1.txt"),
        ("path/to/local/file2.txt", "/path/in/container/file2.txt")
    ])
```

## Copying Directories

You can copy entire directories:

```python
with GenericContainer("alpine:latest") as container:
    # Copy a directory
    container.copy_directory_to_container(
        local_path="path/to/local/directory",
        container_path="/path/in/container/directory"
    )
```

## Copying with Permissions

You can set permissions for copied files:

```python
with GenericContainer("alpine:latest") as container:
    # Copy file with specific permissions
    container.copy_file_to_container(
        local_path="path/to/local/file.txt",
        container_path="/path/in/container/file.txt",
        permissions=0o644  # rw-r--r--
    )
```

## Copying with User

You can specify the owner of copied files:

```python
with GenericContainer("alpine:latest") as container:
    # Copy file with specific owner
    container.copy_file_to_container(
        local_path="path/to/local/file.txt",
        container_path="/path/in/container/file.txt",
        user="nobody"
    )
```

## Copying from Memory

You can copy data directly from memory:

```python
with GenericContainer("alpine:latest") as container:
    # Copy data from memory
    data = b"Hello, World!"
    container.copy_data_to_container(
        data=data,
        container_path="/path/in/container/file.txt"
    )
```

## Best Practices

1. Use appropriate file permissions
2. Clean up copied files
3. Use absolute paths
4. Handle file encoding
5. Consider file size
6. Use appropriate owners
7. Handle file conflicts
8. Consider security implications

## Common Use Cases

### Setting Up Test Data

```python
def test_with_data():
    with GenericContainer("alpine:latest") as container:
        # Copy test data
        container.copy_file_to_container(
            local_path="tests/data/test_data.json",
            container_path="/app/data/test_data.json"
        )

        # Copy configuration
        container.copy_file_to_container(
            local_path="tests/config/test_config.yaml",
            container_path="/app/config/config.yaml"
        )
```

### Setting Up Application Files

```python
def test_application():
    with GenericContainer("myapp:latest") as container:
        # Copy application files
        container.copy_directory_to_container(
            local_path="app/static",
            container_path="/app/static"
        )

        # Copy templates
        container.copy_directory_to_container(
            local_path="app/templates",
            container_path="/app/templates"
        )
```

### Setting Up Database Files

```python
def test_database():
    with GenericContainer("postgres:latest") as container:
        # Copy database initialization script
        container.copy_file_to_container(
            local_path="tests/db/init.sql",
            container_path="/docker-entrypoint-initdb.d/init.sql"
        )

        # Copy test data
        container.copy_file_to_container(
            local_path="tests/db/test_data.sql",
            container_path="/docker-entrypoint-initdb.d/test_data.sql"
        )
```

## Troubleshooting

If you encounter issues with copying data:

1. Check file permissions
2. Verify file paths
3. Check file encoding
4. Verify file size
5. Check container state
6. Verify user permissions
7. Check for file conflicts
8. Verify disk space
