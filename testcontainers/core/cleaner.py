from docker.errors import NotFound

from testcontainers.core.utils import setup_logger

logger = setup_logger(__name__)


def stop_silent(container):
    try:
        container.stop()
    except NotFound:
        pass
    except Exception as e:
        logger.exception(e)
