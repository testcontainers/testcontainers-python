.DEFAULT_GOAL := help


PYTHON_VERSION ?= 3.10
IMAGE = testcontainers-python:${PYTHON_VERSION}
PACKAGES = core $(addprefix modules/,$(notdir $(wildcard modules/*)))

UPLOAD = $(addsuffix /upload,${PACKAGES})
TESTS = $(addsuffix /tests,$(filter-out meta,${PACKAGES}))
TESTS_DIND = $(addsuffix -dind,${TESTS})
DOCTESTS = $(addsuffix /doctests,$(filter-out modules/README.md,${PACKAGES}))


install:  ## Set up the project for development
	poetry install --all-extras
	poetry run pre-commit install

build:  ## Build the python package
	poetry build && poetry run twine check dist/*

tests: ${TESTS}  ## Run tests for each package
${TESTS}: %/tests:
	poetry run pytest -v --cov=testcontainers.$* $*/tests

coverage:  ## Target to combine and report coverage.
	poetry run coverage combine
	poetry run coverage report
	poetry run coverage xml
	poetry run coverage html

lint:  ## Lint all files in the project, which we also run in pre-commit
	poetry run pre-commit run -a

mypy-core-report:
	poetry run mypy --config-file pyproject.toml core | poetry run python scripts/mypy_report.py

docs: ## Build the docs for the project
	poetry run sphinx-build -nW . docs/_build

# Target to build docs watching for changes as per https://stackoverflow.com/a/21389615
docs-watch :
	poetry run sphinx-autobuild . docs/_build # requires 'pip install sphinx-autobuild'

doctests: ${DOCTESTS}  ## Run doctests found across the documentation.
	poetry run sphinx-build -b doctest . docs/_build

${DOCTESTS}: %/doctests:  ##  Run doctests found for a module.
	poetry run sphinx-build -b doctest -c doctests $* docs/_build


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

DOCS_CONTAINER=mkdocs-container
DOCS_IMAGE=mkdocs-poetry
DOCS_DOCKERFILE := Dockerfile.docs

.PHONY: clean-docs
clean-docs:
	@echo "Destroying docs"
	docker rm -f $(DOCS_CONTAINER) || true
	docker rmi $(DOCS_IMAGE) || true

.PHONY: docs-ensure-image
docs-ensure-image:
	@if [ -z "$$(docker images -q $(DOCS_IMAGE))" ]; then \
		docker build -f $(DOCS_DOCKERFILE) -t $(DOCS_IMAGE) . ; \
	fi

.PHONY: serve-docs
serve-docs: docs-ensure-image
	docker run --rm --name $(DOCS_CONTAINER) -it -p 8000:8000 \
		-v $(PWD):/testcontainers-go \
		-w /testcontainers-go \
		$(DOCS_IMAGE) bash -c "\
			cd docs && poetry install --no-root && \
			poetry run mkdocs serve -f ../mkdocs.yml -a 0.0.0.0:8000"

.PHONY: watch-docs
watch-docs: docs-ensure-image
	docker run --rm --name $(DOCS_CONTAINER) -it -p 8000:8000 \
		-v $(PWD):/testcontainers-go \
		-w /testcontainers-go \
		$(DOCS_IMAGE) bash -c "\
			cd docs && poetry install --no-root && \
			poetry run mkdocs serve -f ../mkdocs.yml -a 0.0.0.0:8000" --live-reload

# Needed if dependencies are added to the docs site
.PHONY: export-docs-deps
export-docs-deps:
	cd docs && poetry export --without-hashes --output requirements.txt
