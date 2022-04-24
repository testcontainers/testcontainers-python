import atexit

from docker.errors import NotFound

from testcontainers.core.utils import setup_logger

logger = setup_logger(__name__)


class ResourceCleaner:
    __INSTANCE = None

    def __init__(self):
        self.containers = []

    def attach(self, container):
        self.containers.append(container)

        return container

    def clean(self):
        for c in self.containers:
            try:
                c.stop()
            except NotFound:
                pass
            except Exception as e:
                logger.exception(e)

    @classmethod
    def instance(cls):
        if cls.__INSTANCE is None:
            cls.__INSTANCE = ResourceCleaner()
            atexit.register(cls.__INSTANCE.clean)

        return cls.__INSTANCE
