extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
]
master_doc = "README"

doctest_global_setup = r"""
import sys
from importlib.metadata import version, PackageNotFoundError
from packaging.version import Version

try:
    _cassandra_driver_version = Version(version("cassandra-driver"))
except PackageNotFoundError:
    _cassandra_driver_version = None

SKIP_CASSANDRA_EXAMPLE = (
    _cassandra_driver_version is not None
    and _cassandra_driver_version <= Version("3.29.3")
    and sys.version_info > (3, 14)
)
"""
