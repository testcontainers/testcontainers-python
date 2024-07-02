# New Container

<!-- You have implemented a new container and would like to contribute it? Great! Here are the necessary checklist steps. -->

Fixes ...

<!--
Please do not raise a PR for new container without having raised an issue first.
It helps reduce unnecessary work for you and the maintainers!
-->


# PR Checklist

- [ ] Your PR title follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) syntax
  as we make use of this for detecting Semantic Versioning changes.
  - Additions to the community modules do not contribute to SemVer scheme:
    all community features will be tagged [community-feat](https://github.com/testcontainers/testcontainers-python/issues?q=label%3Acommunity-feat+),
    but we do not want to release minor or major versions due to features or breaking changes outside of core.
    So please use `fix(postgres):` or `fix(my_new_vector_db):` if you want to add or modify community modules. 
    This may change in the future if we have a separate package released with community modules.
- [ ] Your PR allows maintainers to edit your branch, this will speed up resolving minor issues!
- [ ] The new container is implemented under `modules/*`
  - Your module follows [PEP 420](https://peps.python.org/pep-0420/) with implicit namespace packages
    (if unsure, look at other existing community modules)
  - Your package namespacing follows `testcontainers.<modulename>.*`
    and you DO NOT have an `__init__.py` above your module's level.
  - Your module has its own tests under `modules/*/tests`
  - Your module has a `README.rst` and hooks in the `.. auto-class` and `.. title` of your container
  - Implement the new feature (typically in `__init__.py`) and corresponding tests.
- [ ] Your module is added in `pyproject.toml`
  - it is declared under `tool.poetry.packages` - see other community modules
  - it is declared under `tool.poetry.extras` with the same name as your module name,
    we still prefer adding _NO EXTRA DEPENDENCIES_, meaning `mymodule = []` is the preferred addition
    (see the notes at the bottom)
- [ ] Your branch is up-to-date (or your branch will be rebased with `git rebase`)

# Preferred implementation

- The current consensus among maintainers is to try to avoid enforcing the client library
  for the given tools you are triyng to implement.
- This means we want you to avoid adding specific libraries as dependencies to `testcontainers`.
- Therefore, you should implement the configuration and the waiting with as little extra as possible
- You may still find it useful to add your preferred client library as a dev dependency
