# Contributing to `testcontainers-python`

Welcome to the `testcontainers-python` community!
This should give you an idea about how we build, test and release `testcontainers-python`!

Highly recommended to read this document thoroughly to understand what we're working on right now
and what our priorities are before you are trying to contribute something.

This will greatly increase your chances of getting prompt replies as the maintainers are volunteers themselves.

## Before you Begin

We recommend following these steps:

1. Finish reading this document.
2. Read the [recently updated issues][1]
3. Look for existing issues on the subject you are interested in - we do our best to label everything correctly


## Local Development

### Pre-Requisites

You need to have the following tools available to you:
- `make` - You'll need a GNU Make for common developer activities
- `poetry` - This is the primary package manager for the project
- `pyenv` **Recommended**: For installing python versions for your system.
  Poetry infers the current latest version from what it can find on the `PATH` so you are still fine if you don't use `pyenv`.

### Build and test


- Run `make install` to get `poetry` to install all dependencies and set up `pre-commit`
  - **Recommended**: Run `make` or `make help` to see other commands available to you.
- After this, you should have a working virtual environment and proceed with writing code with your favourite IDE
- **TIP**: You can run `make core/tests` or `make module/<my-module>/tests` to run the tests specifically for that to speed up feedback cycles
- You can also run `make lint` to run the `pre-commit` for the entire codebase.


## Adding new containers

We have an [issue template](./ISSUE_TEMPLATE/new-container.md) for adding new containers, please refer to that for more information.
Once you've talked to the maintainers (we do our best to reply!) then you can proceed with contributing the new container.

> [!WARNING]
> PLease raise an issue before you try to contribute a new container! It helps maintainers understand your use-case and motivation.
> This way we can keep pull requests foruced on the "how", not the "why"! :pray:
> It also gives maintainers a chance to give you last-minute guidance on caveats or expectations, particularly with
> new extra dependencies and how to manage them.


## Raising Issues

We have [Issue Templates][2] to cover most cases, please try to adhere to them, they will guide you through the process.
Try to look through the existing issues before you raise a new one.


## Releasing Versions

We have automated Semantic Versioning and release via [release-please](workflows/release-please.yml).
This takes care of:
- Detecting the next version, based on the commits that landed on `main`
- When a Release PR has been merged
  - Create a GitHub Release with the CHANGELOG included
  - Update the [CHANGELOG](../CHANGELOG.md), similar to the GitHub Release
  - Release to PyPI via a [trusted publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
  - Automatically script updates in files where it's needed instead of hand-crafting it (i.e. in `pyproject.toml`)

> [!CRITICAL]
> Community modules are supported on a best-effort basis and for maintenance reasons, any change to them
> is only covered under minor and patch changes.
>
> Community modules changes DO NOT contribute to major version changes!
>
> If your community module container was broken by a minor or patch version change, check out the change logs!

# Thank you!

Thanks for reading, feedback on documentation is always welcome!

[1]: https://github.com/testcontainers/testcontainers-python/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc "Recently Updated Issues showing you what we're focusing on"
[2]: https://github.com/testcontainers/testcontainers-python/issues/new/choose "List of current issue templates, please use them"
