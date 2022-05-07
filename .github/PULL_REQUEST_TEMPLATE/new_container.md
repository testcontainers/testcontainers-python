You have implemented a new container and would like to contribute it? Great! Here are the necessary steps:

- [ ] You have added the new container as a module in the `testcontainers` directory (such as `testcontainers/my_fancy_container.py`).
- [ ] You have added any new python dependencies in the `extras_require` section of `setup.py`.
- [ ] You have added the `extra_requires` key to `requirements.in`.
- [ ] You have updated all python requirements by running `make requirements` from the root directory.
- [ ] You have added tests for the new container in the `tests` directory, e.g. `tests/test_my_fancy_container.py`.
- [ ] You have added the name of the container (such as `my_fancy_container`) to the `test-components` matrix in `.github/workflows/main.yml` to ensure the tests are run.
