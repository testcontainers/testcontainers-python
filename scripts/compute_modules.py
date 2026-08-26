#!/usr/bin/env python3
"""
Extract the community module names out of lists of changed files.
"""

import json
import os
import sys


def compute_modules(files: list[str]) -> list[str]:
    modules = set()
    for f in files:
        if f.startswith("src/testcontainers/community/"):
            part = f.split("/")[3]
        elif f.startswith("tests/community/"):
            part = f.split("/")[2]
        else:
            continue
        if not part or part.startswith("__") or part.endswith(".md"):
            continue
        modules.add(part)
    return sorted(modules)


if __name__ == "__main__":
    files = json.loads(sys.argv[1])
    modules = compute_modules(files)
    result = json.dumps(modules)
    print(f"computed_modules={result}")  # noqa: T201
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        fh.write(f"computed_modules={result}\n")
