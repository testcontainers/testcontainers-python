from os import environ

MAX_TRIES = int(environ.get("TC_MAX_TRIES", 120))
SLEEP_TIME = int(environ.get("TC_POOLING_INTERVAL", 1))
