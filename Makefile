.DEFAULT_GOAL := help


PYTHON_VERSION ?= 3.10
IMAGE = testcontainers-python:${PYTHON_VERSION}

COMMUNITY_MODULES = $(patsubst tests/community/%/,%,$(wildcard tests/community/*/))
COMMUNITY_TESTS = $(addprefix community/,$(addsuffix /tests,$(COMMUNITY_MODULES)))
COMMUNITY_DOCTESTS = $(addprefix community/,$(addsuffix /doctests,$(COMMUNITY_MODULES)))


install:  ## Set up the project for development
	uv sync --all-extras
	uv run pre-commit install

build:  ## Build the python package
	uv build && uv run twine check dist/*

tests: core/tests community-tests  ## Run all tests

core/tests:  ## Run tests for the core package
	uv run coverage run --parallel -m pytest -v tests/core

community-tests: $(COMMUNITY_TESTS)  ## Run tests for all community modules
$(COMMUNITY_TESTS): community/%/tests:
	uv run coverage run --parallel -m pytest -v tests/community/$*

quick-core-tests:  ## Run core tests excluding long_running
	uv run coverage run --parallel -m pytest -v -m "not long_running" tests/core

coverage:  ## Target to combine and report coverage.
	uv run coverage combine
	uv run coverage report
	uv run coverage xml
	uv run coverage html

lint:  ## Lint all files in the project, which we also run in pre-commit
	uv run pre-commit run --all-files

docs: ## Build the docs for the project
	uv run --all-extras sphinx-build -nW docs docs/_build

# Target to build docs watching for changes as per https://stackoverflow.com/a/21389615
docs-watch:
	uv run sphinx-autobuild docs docs/_build # requires 'pip install sphinx-autobuild'

doctests: core/doctests community-doctests  ## Run doctests found across the documentation.

core/doctests:  ## Run doctests for the core package
	uv run --all-extras sphinx-build -b doctest -c doctests docs/core docs/_build

community-doctests: $(COMMUNITY_DOCTESTS)  ## Run doctests for all community modules
$(COMMUNITY_DOCTESTS): community/%/doctests:
	uv run --all-extras sphinx-build -b doctest docs docs/_build docs/community/$*.rst


clean:  ## Remove generated files.
	rm -rf docs/_build
	rm -rf build
	rm -rf dist
	rm -rf */*.egg-info

clean-all: clean ## Remove all generated files and reset the local virtual environment
	rm -rf .venv

# Targets that do not generate file-level artifacts.
.PHONY: clean docs doctests core/doctests community-doctests $(COMMUNITY_DOCTESTS) \
        tests core/tests community-tests $(COMMUNITY_TESTS) \
        quick-core-tests install build coverage lint mypy-core mypy-core-report docs-watch


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
