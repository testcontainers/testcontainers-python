import importlib
from typing import Optional
from uuid import uuid4

from testcontainers.core.config import testcontainers_config as c

SESSION_ID: str = str(uuid4())
TEST_CONTAINERS_NAMESPACE = "org.testcontainers"

LABEL_TEST_CONTAINERS = TEST_CONTAINERS_NAMESPACE
LABEL_SESSION_ID = "org.testcontainers.session-id"
LABEL_VERSION = "org.testcontainers.version"
LABEL_LANG = "org.testcontainers.lang"


def create_labels(image: str, labels: Optional[dict[str, str]]) -> dict[str, str]:
    if labels is None:
        labels = {}
    else:
        for k in labels:
            if k.startswith(TEST_CONTAINERS_NAMESPACE):
                raise ValueError("The org.testcontainers namespace is reserved for interal use")

    labels[LABEL_LANG] = "python"
    labels[LABEL_TEST_CONTAINERS] = "true"
    labels[LABEL_VERSION] = importlib.metadata.version("testcontainers")

    if image == c.ryuk_image:
        return labels

    labels[LABEL_SESSION_ID] = SESSION_ID
    return labels
