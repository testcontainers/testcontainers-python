from __future__ import annotations

from pathlib import Path

import pytest

try:
    import tomllib  # type: ignore[import-not-found]
except ImportError:
    import tomli as tomllib  # type: ignore[no-retyping, unused-ignore]


BASE_DIR = Path(__file__).parent.parent.parent.resolve()
PYPROJECT_TOML = BASE_DIR / "pyproject.toml"
SRC_DIR = BASE_DIR / "src" / "testcontainers" / "community"
DOCS_DIR = BASE_DIR / "docs" / "community"
TESTS_DIR = BASE_DIR / "tests" / "community"

SRC_MODULES = frozenset({f.stem for f in SRC_DIR.iterdir() if f.is_dir()})
DOCS_MODULES = frozenset({f.stem for f in DOCS_DIR.glob("*.rst")})
TESTS_MODULES = frozenset({f.stem for f in TESTS_DIR.iterdir() if f.is_dir()})

ALL_MODULES = frozenset((SRC_MODULES | DOCS_MODULES | TESTS_MODULES) - {"__init__", "__pycache__"})


@pytest.fixture(scope="session")
def pyproject_toml_extra() -> frozenset[str]:
    with PYPROJECT_TOML.open("rb") as f:
        pyproject = tomllib.load(f)
    return frozenset(pyproject["project"]["optional-dependencies"].keys())


@pytest.mark.parametrize("module", sorted(ALL_MODULES))
def test_community_definition(module: str, pyproject_toml_extra: frozenset[str]) -> None:
    """
    Check that community modules defined in docs, src, tests and pyproject.toml extras are in sync
    """
    assert module in SRC_MODULES, f"{module} is missing in src/testcontainers/community"
    assert module in DOCS_MODULES, f"{module} is missing in docs/community"
    assert module in TESTS_MODULES, f"{module} is missing in tests/community"
    assert module in pyproject_toml_extra, f"{module} is missing in pyproject.toml extras"
