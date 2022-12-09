# Contributing

### Contributing a new container

You can contribute a new container in three steps:

1. Create a new module with a class for the container at `testcontainers/[my fancy container].py` that implements the new functionality.
2. Add a working usage example and short functionality description to the new class's docstring.
3. Integrate new class with [Sphinx](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html) using the reStructuredText files in `docs/`.
3. Create a new test module at `tests/test_[my fancy container].py` that tests the new functionality.
3. Add `[my fancy container]` to the list of test components in the GitHub Action configuration at `.github/workflows/main.yml`.