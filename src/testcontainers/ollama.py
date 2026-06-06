import warnings

from testcontainers.community.ollama import (
    OllamaContainer,
    OllamaModel,
)

warnings.warn(
    "testcontainers.ollama is deprecated, use testcontainers.community.ollama instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "OllamaContainer",
    "OllamaModel",
]
