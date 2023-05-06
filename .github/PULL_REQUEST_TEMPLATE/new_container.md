You have implemented a new container and would like to contribute it? Great! Here are the necessary steps.

- [ ] Create a new feature directory and populate it with the package structure [described in the documentation](https://testcontainers-python.readthedocs.io/en/latest/#package-structure). Copying one of the existing features is likely the best way to get started.
- [ ] Implement the new feature (typically in `__init__.py`) and corresponding tests.
- [ ] Add a line `-e file:[feature name]` to `requirements.in` and run `make requirements`. This command will find any new requirements and generate lock files to ensure reproducible builds (see the [pip-tools documentation](https://pip-tools.readthedocs.io/en/latest/) for details). Then run `pip install -r requirements/[your python version].txt` to install the new requirements.
- [ ] Update the feature `README.rst` and add it to the table of contents (`toctree` directive) in the top-level `README.rst`.
- [ ] Add a line `[feature name]` to the list of components in the  GitHub Action workflow in `.github/workflows/main.yml` to run tests, build, and publish your package when pushed to the `main` branch.
- [ ] Rebase your development branch on `main` (or merge `main` into your development branch).
