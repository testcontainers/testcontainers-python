import importlib
from typing import Optional
from uuid import uuid4

from testcontainers.core.config import testcontainers_config as c

SESSION_ID: str = str(uuid4())
TESTCONTAINERS_NAMESPACE = "org.testcontainers"

LABEL_TESTCONTAINERS = TESTCONTAINERS_NAMESPACE
LABEL_SESSION_ID = "org.testcontainers.session-id"
LABEL_VERSION = "org.testcontainers.version"
LABEL_LANG = "org.testcontainers.lang"


def create_labels(image: str, labels: Optional[dict[str, str]]) -> dict[str, str]:
    if labels is None:
        labels = {}
    else:
        for k in labels:
            if k.startswith(TESTCONTAINERS_NAMESPACE):
                raise ValueError("The org.testcontainers namespace is reserved for internal use")

    labels[LABEL_LANG] = "python"
    labels[LABEL_TESTCONTAINERS] = "true"
    labels[LABEL_VERSION] = importlib.metadata.version("testcontainers")

    if image == c.ryuk_image:
        return labels

    labels[LABEL_SESSION_ID] = SESSION_ID
    return labels
