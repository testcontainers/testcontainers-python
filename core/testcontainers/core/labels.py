from uuid import uuid4
from typing import Optional

from .reaper import REAPER_IMAGE

SESSION_ID: str = str(uuid4())
LABEL_SESSION_ID = "org.testcontainers.session-id"

def create_labels(image: str, labels: Optional[dict]) -> dict:
    if labels is None: labels = {}

    if image == REAPER_IMAGE:
        return labels

    labels[LABEL_SESSION_ID] = SESSION_ID
    return labels

