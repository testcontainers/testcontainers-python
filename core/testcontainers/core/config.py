from os import environ
from warnings import warn

MAX_TRIES = int(environ.get("TC_MAX_TRIES", 120))

if "TC_POOLING_INTERVAL" in environ:
    warn("The TC_POOLING_INTERVAL environment variable is deprecated. Use TC_POLLING_INTERVAL instead.", DeprecationWarning)
    POLLING_INTERVAL = int(environ.get("TC_POOLING_INTERVAL", 1))
else:
    POLLING_INTERVAL = int(environ.get("TC_POLLING_INTERVAL", 1))
