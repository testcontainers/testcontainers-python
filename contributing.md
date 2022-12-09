
# Contributing

## Contributing a container

You can contribute a new container in three steps:

1. Create a new module at `testcontainers/[my fancy container].py` that implements the new functionality.
2. Create a new test module at `tests/test_[my fancy container].py` that tests the new functionality.
3. Add `[my fancy container]` to the list of test components in the GitHub Action configuration at `.github/workflows/main.yml`.