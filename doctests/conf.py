from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
TEST_DIR = BASE_DIR / "tests"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
]
master_doc = "README"

doctest_global_setup = f"TEST_DIR = '{TEST_DIR}'"
