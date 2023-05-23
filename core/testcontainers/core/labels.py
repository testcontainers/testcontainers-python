from uuid import uuid4
from typing import Optional

from .config import RYUK_IMAGE


SESSION_ID: str = str(uuid4())
LABEL_SESSION_ID = "org.testcontainers.session-id"
LABEL_LANG = "org.testcontainers.lang"


def create_labels(image: str, labels: Optional[dict]) -> dict:
    if labels is None:
        labels = {}
    labels[LABEL_LANG] = "python"

    if image == RYUK_IMAGE:
        return labels

    labels[LABEL_SESSION_ID] = SESSION_ID
    return labels
