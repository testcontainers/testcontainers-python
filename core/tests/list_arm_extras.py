from pathlib import Path
from testcontainers.core.utils import is_arm

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

SKIPPED_EXTRAS = {"db2"}  # skip incompatible extras


def get_arm_extras():
    with Path("pyproject.toml").open("rb") as f:
        data = tomllib.load(f)

    extras = data["tool"]["poetry"]["extras"]
    skip = SKIPPED_EXTRAS
    return " ".join(k for k in extras if k not in skip)
