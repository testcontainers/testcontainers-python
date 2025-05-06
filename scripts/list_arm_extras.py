#!/usr/bin/env python3

# used to generate the list of extras in the Makefile
import sys
from pathlib import Path

# Support both Python 3.10 (needs tomli) and 3.11+ (has tomllib)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        ## Python <3.11 detected but 'tomli' is not installed, poetry add --group dev tomli
        sys.exit(1)

SKIPPED_EXTRAS = {"db2"}  # skip incompatible extras


def get_filtered_extras() -> list[str]:
    with Path("pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    extras = data["tool"]["poetry"]["extras"]
    return [key for key in extras if key not in SKIPPED_EXTRAS]


if __name__ == "__main__":
    sys.stdout.write(" ".join(get_filtered_extras()) + "\n")
