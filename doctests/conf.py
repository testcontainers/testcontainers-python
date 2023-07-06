extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
]
master_doc = "README"
# fixes import errors for docker
autodoc_mock_imports = ["docker"]
