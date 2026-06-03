"""
This test contains sanity check for the project settings
"""

import tomli  # TODO: Migrate to tomllib once we drop 3.10 support
from pathlib import Path
from typing import Any, Mapping, Final

import pytest

PROJECT_DIR: Final = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def pyproject_toml() -> Mapping[str, Any]:
    with open(PROJECT_DIR / "pyproject.toml", "rb") as f:
        return tomli.load(f)


def test_wheel_dev_parity(pyproject_toml: Mapping[str, Any]) -> None:
    """
    The build wheel should contain the same modules like the develop installation

    Because of our special layout we need two hatch settings for this.

    This tests ensures that both lead to the same results.
    """

    wheel_modules = set(pyproject_toml["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"])

    # src modules create .pth files in site-packages. This folders are added to
    # sys.path, therefore they need no "testcontainers" part to work.
    src_modules = {
        f"{module}/testcontainers"
        for module in pyproject_toml["tool"]["hatch"]["build"]["targets"]["wheel"]["dev-mode-dirs"]
    }
    assert wheel_modules == src_modules
