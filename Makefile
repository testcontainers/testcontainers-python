.DEFAULT_GOAL := help


PYTHON_VERSION ?= 3.10
IMAGE = testcontainers-python:${PYTHON_VERSION}
PACKAGES = core $(addprefix modules/,$(notdir $(wildcard modules/*)))

UPLOAD = $(addsuffix /upload,${PACKAGES})
TESTS = $(addsuffix /tests,$(filter-out meta,${PACKAGES}))
TESTS_DIND = $(addsuffix -dind,${TESTS})
DOCTESTS = $(addsuffix /doctests,$(filter-out modules/README.md,${PACKAGES}))


install:  ## Set up the project for development
	uv sync --all-extras
	uv run pre-commit install

build:  ## Build the python package
	uv build && uv run twine check dist/*

tests: ${TESTS}  ## Run tests for each package
${TESTS}: %/tests:
	uv run coverage run --parallel -m pytest -v  $*/tests

coverage:  ## Target to combine and report coverage.
	uv run coverage combine
	uv run coverage report
	uv run coverage xml
	uv run coverage html

lint:  ## Lint all files in the project, which we also run in pre-commit
	uv run pre-commit run --all-files

mypy-core:  ## Run mypy on the core package
	uv run mypy --config-file pyproject.toml core

mypy-core-report:  ## Generate a report for mypy on the core package
	uv run mypy --config-file pyproject.toml core | uv run python scripts/mypy_report.py

docs: ## Build the docs for the project
	uv run --all-extras sphinx-build -nW . docs/_build

# Target to build docs watching for changes as per https://stackoverflow.com/a/21389615
docs-watch :
	uv run sphinx-autobuild . docs/_build # requires 'pip install sphinx-autobuild'

doctests: ${DOCTESTS}  ## Run doctests found across the documentation.
	uv run --all-extras sphinx-build -b doctest . docs/_build

${DOCTESTS}: %/doctests:  ##  Run doctests found for a module.
	uv run --all-extras sphinx-build -b doctest -c doctests $* docs/_build


clean:  ## Remove generated files.
	rm -rf docs/_build
	rm -rf build
	rm -rf dist
	rm -rf */*.egg-info

clean-all: clean ## Remove all generated files and reset the local virtual environment
	rm -rf .venv

# Targets that do not generate file-level artifacts.
.PHONY: clean docs doctests image tests ${TESTS}


# Implements this pattern for autodocumenting Makefiles:
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
#
# Picks up all comments that start with a ## and are at the end of a target definition line.
.PHONY: help
help:  ## Display command usage
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## --------------------------------------

.PHONY: serve-docs
serve-docs:
	uv run mkdocs serve -f mkdocs.yml -a 127.0.0.1:8000
