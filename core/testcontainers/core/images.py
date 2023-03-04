from os import environ


REAPER_IMAGE = environ.get("RYUK_CONTAINER_IMAGE", "testcontainers/ryuk:0.3.4")
