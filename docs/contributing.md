# Contributing to `testcontainers-python`

Welcome to the `testcontainers-python` community!
This should give you an idea about how we build, test and release `testcontainers-python`!

Highly recommended to read this document thoroughly to understand what we're working on right now
and what our priorities are before you are trying to contribute something.

This will greatly increase your chances of getting prompt replies as the maintainers are volunteers themselves.

## Before you begin

We recommend following these steps:

1. Finish reading this document.
2. Read the [recently updated issues](https://github.com/testcontainers/testcontainers-python/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc){:target="\_blank"}
3. Look for existing issues on the subject you are interested in - we do our best to label everything correctly

## Local development

### Pre-Requisites

You need to have the following tools available to you:

- `make` - You'll need a GNU Make for common developer activities
- `poetry` - This is the primary package manager for the project
- `pyenv` **Recommended**: For installing python versions for your system.
  Poetry infers the current latest version from what it can find on the `PATH` so you are still fine if you don't use `pyenv`.

### Build and test

- Run `make install` to get `poetry` to install all dependencies and set up `pre-commit`
  - **Recommended**: Run `make` or `make help` to see other commands available to you.
- After this, you should have a working virtual environment and proceed with writing code with your favorite IDE
- **TIP**: You can run `make core/tests` or `make modules/<my-module>/tests` to run the tests specifically for that to speed up feedback cycles
- You can also run `make lint` to run the `pre-commit` for the entire codebase.

## Adding new modules

We have an [issue template](https://github.com/testcontainers/testcontainers-python/blob/main/.github/ISSUE_TEMPLATE/new-container.md){:target="\_blank"} for adding new module containers, please refer to that for more information.
Once you've talked to the maintainers (we do our best to reply!) then you can proceed with contributing the new container.

!!!WARNING

    Please raise an issue before you try to contribute a new container! It helps maintainersunderstand your use-case and motivation.
    This way we can keep pull requests forced on the "how", not the "why"! :pray:
    It also gives maintainers a chance to give you last-minute guidance on caveats orexpectations, particularly with
    new extra dependencies and how to manage them.

### Module documentation

Leave examples for others with your mew module such as `modules/<new_module>/basic_example.py`. You can create as many examples as you want.

Create a new `docs/modules/<new_module>.md` describing the basic use of the new container. There is a [starter template provided here](https://raw.githubusercontent.com/testcontainers/testcontainers-python/blob/main/docs/modules/template.md){:target="\_blank"}.

!!! important

    Make sure to add your new module to the sidebar nav in the `mkdocs.yml`

## Raising issues

We have [Issue Templates](https://raw.githubusercontent.com/testcontainers/testcontainers-python/refs/heads/main/.github/ISSUE_TEMPLATE/new-container.md){:target="\_blank"} to cover most cases, please try to adhere to them, they will guide you through the process.
Try to look through the existing issues before you raise a new one.

## Releasing versions

We have automated Semantic Versioning and release via [release-please](https://github.com/testcontainers/testcontainers-python/blob/main/.github/workflows/release-please.yml){:target="\_blank"}.
This takes care of:

- Detecting the next version, based on the commits that landed on `main`
- When a Release PR has been merged
  - Create a GitHub Release with the CHANGELOG included
  - Update the [CHANGELOG](https://github.com/testcontainers/testcontainers-python/blob/main/CHANGELOG.md){:target="\_blank"}, similar to the GitHub Release
  - Release to PyPI via a [trusted publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/){:target="\_blank"}
  - Automatically script updates in files where it's needed instead of hand-crafting it (i.e. in `pyproject.toml`)

!!!DANGER

    Community modules are supported on a best-effort basis and for maintenance reasons, any change to them
    is only covered under minor and patch changes.
    Community modules changes DO NOT contribute to major version changes!
    If your community module container was broken by a minor or patch version change, check out the change logs!

## Documentation contributions

The _Testcontainers for Go_ documentation is a static site built with [MkDocs](https://www.mkdocs.org/){:target="\_blank"}.
We use the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/){:target="\_blank"} theme, which offers a number of useful extensions to MkDocs.

We publish our documentation using Netlify.

### Adding code snippets

To include code snippets in the documentation, we use the [codeinclude plugin](https://github.com/rnorth/mkdocs-codeinclude-plugin){:target="\_blank"}, which uses the following syntax:

> &lt;!--codeinclude--&gt;<br/> > &#91;Human readable title for snippet&#93;(./relative_path_to_example_code.go) targeting_expression<br/> > &#91;Human readable title for snippet&#93;(./relative_path_to_example_code.go) targeting_expression<br/> > &lt;!--/codeinclude--&gt;<br/>

Where each title snippet in the same `codeinclude` block would represent a new tab
in the snippet, and each `targeting_expression` would be:

- `block:someString` or
- `inside_block:someString`

Please refer to the [codeinclude plugin documentation](https://github.com/rnorth/mkdocs-codeinclude-plugin){:target="\_blank"} for more information.

### Previewing rendered content

From the root directory of the repository, you can use the following command to build and serve the documentation locally:

```shell
make serve-docs
```

It will use a Docker container to install the required dependencies and start a local server at `http://localhost:8000`.

Once finished, you can destroy the container with the following command:

```shell
make clean-docs
```

### PR preview deployments

Note that documentation for pull requests will automatically be published by Netlify as 'deploy previews'.
These deployment previews can be accessed via the `deploy/netlify` check that appears for each pull request.

Please check the GitHub comment Netlify posts on the PR for the URL to the deployment preview.
